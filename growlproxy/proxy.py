#!/usr/bin/env python

import logging
from datetime import datetime
from growlproxy.server import GrowlServer, BaseGrowlHandler, GrowlClient
from growlproxy import models
from growlproxy.config import ConfigManager
import growlproxy.db 

class GrowlProxy(BaseGrowlHandler):
    ''' Main class for growl proxy '''

    def __init__( self, hostname=None, port=None ):
        ''' Constructor '''
        self.db = growlproxy.db.GetDbSession()
        self.config = ConfigManager()
        params = {
                'password' : self.config.password
                }
        if hostname:
            params[ 'hostname' ] = hostname
        if port:
            params[ 'port' ] = port
        self.server = GrowlServer( self, **params )

        # No database for growls just yet, so for now
        # create a temporary variable to hold all our growls
        self.growls = []

    def Run(self):
        ''' Runs the server '''
        self.server.Run()

    def HandleRegister( self, message, client ):
        """ 
        Handler for register messages 
        
        @param: message     The register message received from the client
        @param: client      The client that sent the register message
        """
        logging.debug( "received register" )
        pass # Currently, do nothing.  Caller will return OK

    def HandleNotify( self, message, client ):
        """ 
        Handler for notify messages 
        
        @param: message     The notify message received from the client
        @param: client      The client that sent the notify message
        """
        if self.config.forwardAll:
            self.Forward( message, client )
        else:
            logging.debug( "checking forward rules" )
            self.CheckForwardRules( message, client )
       
    def HandleSubscribe( self, message, client ):
        """
        Handler for subscribe messages

        @param: message     The subscribe message received from the client
        @param: client      The client that sent the subscribe message
        """
        pass
    
    def CheckForwardRules( self, message, client ):
        '''
        Checks if the incoming message should be forwarded and appends it
        to the forwarding list if neccesary.
        
        @param: message     The incoming message received from the client
        @param: client      The client that sent the notify message
        '''
        # Find the remote server
        query = self.db.query( models.Server )
        query = query.filter_by( 
                    forwardGrowls=True 
                    ).filter_by( 
                                remoteHost=client.host 
                                )
        try:
            server = query.one()
            for membership in server.groupMemberships:
                for forwardRule in membership.group.forwardFromRules:
                    forward = any( 
                                  filter.MatchesMessage( message )
                                  for rule in forwardRule.filters
                                  )
                    # TODO: Decide what to do here.
                    #        Either ignore if no forwardRules
                    #        or as just now, forward if no rules
                    if ( len( forwardRule.filters ) == 0 ) or forward:
                        self.Forward( 
                                     message,
                                     client,
                                     destGroup = forwardRule.toServerGroup
                                     )
        except:
            logging.info( "Ignoring growl from %s", client.host )
            return
        

    def MakeReceivedString( self, client ):
        ''' Makes a string for the Received header used when forwarding '''
        return "From %s by %s ; %s " % (
                client.host,
                self.server.hostname,
                datetime.now().isoformat(" ")
                )

    def Forward( self, message, client, destGroup=None ):
        ''' 
        Stores a message for forwarding
        @param: message      The message to store
        @param: destGroup    The destination group to forward to
        '''
        # TODO: Currently multiple levels of forwarding will overwrite this.
        # Probably want to update GNTP to stop that from happening
        logging.debug( "Forwarding message from %s to %s", client, destGroup )
        message.headers[ 'Received' ] = self.MakeReceivedString( client )
        self.growls.append( ( message, destGroup ) )
        self.CheckForwards()

    def CheckForwards( self ):
        forwardServers = (
            self.db.query( models.Server ).filter_by( forwardGrowls=True )
            )
        logging.info( 
                    "Forwading %i growls", 
                    len( self.growls )
                    )
        for growl, group in self.growls:
            if group:
                # TODO: Sort this shit by priority sometime
                filteredList = [ member.server for member in group.members ] 
            else:
                # If we don't have a group, send to all
                filteredList = forwardServers 
            for server in filteredList:
                logging.debug( "Forwarding growl to %s", server )
                try:
                    client = GrowlClient(
                            remoteAddress = server.remoteHost,
                            password = 'password'
                            )
                    client.Send( growl )
                except:
                    logging.warning(
                            "Caught exception when sending growl to %s",
                            server.remoteHost
                            )
                    pass
        self.growls = []

