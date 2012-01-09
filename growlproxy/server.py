#!/usr/bin/env python

import gntp
import socket
import logging
import traceback
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from collections import namedtuple

__all__ = [ 
    'GrowlServer',
    'GrowlClient',
    'BaseGrowlHandler',
    'IpEndpoint'
    ]

DefaultGrowlPort = 23053
DefaultSocketTimeout = 5
GntpMessageEnd = '\r\n\r\n'

IpEndpoint = namedtuple( "IpEndpoint", [ 'host', 'port' ] )

class Gntp(Protocol):
    def __init__( self, server ):
        ''' 
        Constructor
        @param: server      The server to pass growl messages to.
        '''
        self.server = server
        self.buffer = ""

    def dataReceived( self, data ):
        ''' Data received handler '''
        if len( self.buffer ) > 0:
            self.buffer = data
        else:
            self.buffer += data
        self.CheckBuffer()

    def CheckBuffer( self ):
        ''' Checks the contents of the buffer for whole messages '''
        if self.buffer.endswith( GntpMessageEnd ):
            self.ProcessPacket( self.buffer )
            self.buffer = ""
            #TODO: End the connection now?
        
    def ProcessPacket( self, packet ):
        ''' 
        Processes a packet
        @param: packet     The packet to process
        '''
        try:
            message = gntp.parse_gntp( packet, self.server.password )
        except:
            logging.exception('Failed to parse packet:\n%s' % packet )
            return
        if message:
            remoteAddress = self.transport.getPeer()
            logging.debug( 
                    'From %s:%s <%s>\n%s',
                    remoteAddress.host,
                    remoteAddress.port,
                    message.__class__,
                    message 
                    )
            resp = self.server.GetResponse( 
                    message, 
                    IpEndpoint( remoteAddress.host, remoteAddress.port ) 
                    )
            data = resp.encode()
            self.transport.write( data.encode('utf-8', 'replace') )

class GntpFactory(Factory):
    def __init__( self, server ):
        self.server = server

    def buildProtocol( self, addr ):
        return Gntp( self.server )

class GrowlServer(object):
    ''' Class to run a growl server '''
    
    connectionBacklog = 5

    def __init__(
            self,
            handler,
            hostname = "127.0.0.1",
            port = int( DefaultGrowlPort ),
            password = None
            ):
        """ 
        Constructor for GrowlServer
        @param: handler     The handler to use for incoming messages
        @param: hostname    The hostname to listen on
        @param: port        The port to listen on
        @param: password    The password to use
        """
        self.run = True
        self.handler = handler
        self.hostname = hostname
        self.port = port
        self.password = password
        self.endpoint = TCP4ServerEndpoint( reactor, self.port )

    def Run(self):
        """ Runs the server, listening for connections """
        #TODO: Listen for twisted stuff
        self.endpoint.listen( GntpFactory( self ) )
        reactor.run()
        pass

    def Stop(self):
        """ Stops the server from running """
        reactor.stop()
        #TODO: figure out if anything more is needed here

    def GetResponse( self, message, endpoint ):
        """
        Processes an incoming messsage and gets a response
        @param: message     The incoming message
        @param: endpoint    The endpoint it originated from
        """
        if message.info[ 'messagetype' ] == 'REGISTER':
            self.handler.HandleRegister( message, endpoint )
            # Send back an OK for now 
            resp = gntp.GNTPOK( action='Register' )
            return resp
        elif message.info[ 'messagetype' ] == 'NOTIFY':
            self.handler.HandleNotify( message, endpoint )
            # Send back an OK for now
            resp = gntp.GNTPOK( action='Notify' )
            return resp
        else:
            print "Received %s" % message.info[ 'messagetype' ]
            return None


class GrowlClient(object):
    """ Class to wrap a socket to a growl client """

    #TODO: Probably want to replace all this with a twisted python client
    def __init__(
            self,
            remoteAddress,
            port = int( DefaultGrowlPort ),
            sock=None,
            password=None
            ):
        """
        Constructor
        @param: remoteAddress   The remote address of the client
        @param: port            The port of the client
        @param: sock            The socket the client to speak to the client on
        @param: password        The password to use for the connection
        @todo: Probably want to allow hash algo setting
                Or at least stop using MD5 as the default
        """
        self.remoteAddress = remoteAddress
        self.password = password
        if sock:
            self.socket = sock
        else:
            self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.socket.settimeout( DefaultSocketTimeout )
            self.socket.connect( ( remoteAddress, port ) )

    def Disconnect(self):
        """ Disconnects the client """
        if self.socket:
            self.socket.shutdown( socket.SHUT_RDWR )
            self.socket.close()
            self.socket = None

    def Send(self, object):
        """
        Sends a growl packet
        @param: object    The growl object to send
        """
        #TODO: Add logging
        if ( 
                ( not hasattr( object, 'password' ) ) or 
                object.password != self.password
                ):
            # Reset the password on the object
            object.set_password( self.password )
        data = object.encode()
        self.socket.send( data.encode('utf-8', 'replace') )

    def Recv(self):
        """
        Receives a growl packet
        @returns        A gntp class representing the received data
        """
        data = self.socket.recv( 1024 )
        while not data.endswith( '\r\n\r\n' ):
            data += self.socket.recv( 1024 )
        message = gntp.parse_gntp( data, self.password )
        if message:
            remoteAddress = self.socket.getsockname()
            logging.debug( 
                    'From %s:%s <%s>\n%s',
                    remoteAddress[0],
                    remoteAddress[1],
                    message.__class__,
                    message 
                    )
        return message


class BaseGrowlHandler(object):
    """ Base class for growl message handlers """

    def HandleRegister( self, message, client ):
        """ 
        Handler for register messages 
        
        @param: message     The register message received from the client
        @param: client      The client that sent the register message
        """
        pass

    def HandleNotify( self, message, client ):
        """ 
        Handler for notify messages 
        
        @param: message     The notify message received from the client
        @param: client      The client that sent the notify message
        """
        pass

    def HandleSubscribe( self, message, client ):
        """
        Handler for subscribe messages

        @param: message     The subscribe message received from the client
        @param: client      The client that sent the subscribe message
        """
        pass


if __name__ == "__main__":
    logging.basicConfig( level=logging.DEBUG )
    gs = GrowlServer( BaseGrowlHandler(), password="password" )
    try:
        gs.Run()
    except KeyboardInterrupt:
        print "Keyboard Interupt.  Stopping"
        gs.Stop()
    finally:
        gs.Stop()

