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
            # TODO: Add filter rule checking etc. here
            pass

       
    def HandleSubscribe( self, message, client ):
        """
        Handler for subscribe messages

        @param: message     The subscribe message received from the client
        @param: client      The client that sent the subscribe message
        """
        pass

    def MakeReceivedString( self, client ):
        ''' Makes a string for the Received header used when forwarding '''
        return "From %s by %s ; %s " % (
                client.remoteAddress,
                self.server.hostname,
                datetime.now().isoformat(" ")
                )

    def Forward( self, message, client ):
        # TODO: Currently multiple levels of forwarding will overwrite this.
        # Probably want to update GNTP to stop that from happening
        message.headers[ 'Received' ] = self.MakeReceivedString( client )
        self.growls.append( message )
        self.CheckForwards()


    def CheckForwards( self ):
        forwardServers = (
            self.db.query( models.Server ).filter_by( forwardGrowls=True ).all()
            )
        logging.info( 
                "Forwading %i growls to %i servers", 
                len( self.growls ),
                len( forwardServers )
                )
        for growl in self.growls:
            for server in forwardServers:
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

