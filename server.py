#!/usr/bin/env python

import gntp
import socket
import logging

class GrowlServer(object):
    ''' Class to run a growl server '''
    
    connectionBacklog = 5

    def __init__(self, hostname="127.0.0.1", port=23053, password=None):
        """ 
        Constructor for GrowlServer
        @param: hostname    The hostname to listen on
        @param: port        The port to listen on
        @param: password    The password to use
        """
        self.run = True
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.socket.bind( ( hostname, port ) )
        self.password = password

    def Run(self):
        """ Runs the server, listening for connections """
        self.socket.listen( self.connectionBacklog )
        while self.run:
            acceptRes = self.socket.accept()
            client = GrowlClient( *acceptRes, password=self.password )
            self.HandleConnection( client )
            client.Disconnect()

    def Stop(self):
        """ Stops the server from running """
        self.run = False
        if self.socket:
            self.socket.close()
            self.socket = None

    def HandleConnection(self, client):
        """
        Handles an incoming connection
        @param: client      A GrowlClient representing the client
        """
        message = client.Recv()
        if message.info[ 'messagetype' ] == 'REGISTER':
            # Probably recieving a growl from somewhere.
            # Send back an OK for now (maybe want to make a list of clients)
            resp = gntp.GNTPOK( action='Register' )
            client.Send( 'GNTPOK', resp.encode() )
        elif message.info[ 'messagetype' ] == 'NOTIFY':
            # Received a growl.  Print it out to log, and respond
            logging.info( 'Message Received: %r', message.headers[ 'Notification-Text' ] )
            resp = gntp.GNTPOK( action='Notify' )
            client.Send( 'GNTPOK', resp.encode() )
        else:
            print "Received %s" % message.info[ 'messagetype' ]


class GrowlClient(object):
    """ Class to wrap a socket to a growl client """

    def __init__( self, socket, remoteAddress, password ):
        """
        Constructor
        @param: socket          The socket the client to speak to the client on
        @param: remoteAddress   The remote address of the client
        @param: password        The password to use for the connection
        """
        self.socket = socket
        self.remoteAddress = remoteAddress
        self.password = password

    def Disconnect(self):
        """ Disconnects the client """
        if self.socket:
            self.socket.close()
            self.socket = None

    def Send(self, type, data):
        """
        Sends a growl packet
        @param: type    The type of packet to send
        @param: data    The data to send (usually the result of calling 
                        encode() on a growl object)
        """
        #TODO: Add logging
        self.socket.send( data.encode('utf-8', 'replace') )

    def Recv(self):
        """
        Receives a growl packet
        @returns        A gntp class representing the received data
        """
        message = gntp.parse_gntp( self.socket.recv( 1024 ), self.password )
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

if __name__ == "__main__":
    logging.basicConfig( level=logging.DEBUG )
    gs = GrowlServer( password="password" )
    try:
        gs.Run()
    except KeyboardInterrupt:
        print "Keyboard Interupt.  Stopping"
    finally:
        gs.Stop()

