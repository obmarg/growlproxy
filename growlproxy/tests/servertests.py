
import unittest
import threading
import time
from gntp import notifier
from growlproxy.server import *

class TestGrowlHandler( BaseGrowlHandler ):

    __slots__ = [ 
            'messages',
            'clients',
            ]

    def __init__( self ):
        self.Reset()
    
    def Reset( self ):
        self.messages = []
        self.clients = []

    def HandleRegister( self, message, client ):
        self.messages.append( message )
        self.clients.append( client )

    def HandleNotify( self, message, client ):
        self.messages.append( message )
        self.clients.append( client )

    def HandleSubscribe( self, message, client ):
        self.messages.append( message )
        self.clients.append( client )


class ServerTests( unittest.TestCase ):
    Port = 2345

    def CheckHandler( self, message = None, index = 0 ):
        assert len( self.handler.messages ) >= index
        assert len( self.handler.clients ) >= index
        if message:
            self.assertEqual( self.handler.messages[ index ], message )
        self.assertEqual( 
                self.handler.clients[ index ].remoteAddress,
                "127.0.0.1"
                )

    def setUp( self ):
        self.handler = TestGrowlHandler()
        self.server = GrowlServer(
                self.handler,
                hostname = "127.0.0.1",
                password = 'password',
                )
        self.thread = threading.Thread( target=lambda: self.server.Run() )
        self.thread.start()

    def tearDown( self ):
        self.server.Stop()
        self.thread.join()
        self.handler.Reset()

    def test_subscribe( self ):
        
        pass    # TODO: Test this

    def test_notify( self ):
        pass    # TODO: Test this

    def test_register( self ):
        pass    # TODO: Test this

    def test_notifyWithMini( self ):
        notifier.mini(
                hostname = "127.0.0.1",
                password = 'password',
                description = 'Rumble',
                )
        # Check addresses
        self.CheckHandler()
        self.CheckHandler( index=1 )

        # Check the type of notifications
        self.assertEqual( 
                self.handler.messages[ 0 ].info[ 'messagetype' ],
                'REGISTER'
                )
        self.assertEqual(
                self.handler.messages[ 1 ].info[ 'messagetype' ],
                'NOTIFY'
                )

        # Check the notification text
        self.assertEqual(
                self.handler.messages[ 1 ].headers[ 'Notification-Text' ],
                'Rumble'
                )
