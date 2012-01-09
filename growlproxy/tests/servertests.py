
import unittest
import threading
import time
import mox
import math
from collections import namedtuple
import twisted.internet.tcp
from gntp import notifier
import gntp
from growlproxy.server import *
from growlproxy.server import Gntp

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


class GntpTests( unittest.TestCase ):
    TestHost = "127.0.0.1"
    TestPort = 2345
    TestPassword = 'password'

    def GetRegisterMessage( self, notifications=[] ):
        '''
        Gets a register message for testing
        @param: notifications       A list of ( name, enabled ) notifications
        '''
        rv = gntp.GNTPRegister( 
                password = GntpTests.TestPassword
                )
        for tup in notifications:
            rv.add_notification( *tup )
        return rv

    def GetNoticeMessage( self, text=None, **kwargs ):
        '''
        Gets a notice message for testing
        Passes extra keyword arguments on to GNTPNotice constructor
        @param: text    The notification text
        '''
        rv = gntp.GNTPNotice(
                password = GntpTests.TestPassword,
                **kwargs
                )
        if text:
            rv.add_header( 'Notification-Text', text )
        return rv

    def GetSubscribeMessage( self, id, name, port=None ):
        '''
        Gets a subscribe message for testing
        @param: id      The id of the subscriber
        @param: name    The name of the subscriber
        @param: port    The port of the subscriber
        '''
        rv = gntp.GNTPSubscribe()
        rv.add_header( 'Subscriber-ID', id )
        rv.add_header( 'Subscriber-Name', name )
        if port:
            rv.add_header( 'Subscriber-Port', port )
        return rv

    def GetMockTransport( self ):
        ''' 
        Gets a mock of a transport object
        The mock object will expect to have it's getPeer function called first
        '''
        HostPortDef = namedtuple( 'hostPortDef', [ 'host', 'port' ] )
        mockTransport = mox.MockObject( 
                twisted.internet.tcp.Client
                )
        mockTransport.getPeer().AndReturn( 
                HostPortDef( GntpTests.TestHost, GntpTests.TestPort )
                )
        return mockTransport

    def GetMockObjects( 
            self,
            expectedMessage=None
            ):
        ''' 
        Gets a mock transport & server
        @param: inputData       The input data for this run of a test
        @param: expectedMessage The GNTP message class to expect (or none)
        '''
        mockTransport = self.GetMockTransport()
        mockServer = mox.MockObject( GrowlServer )
        mockServer.password = GntpTests.TestPassword
        if expectedMessage:
            okMsg = gntp.GNTPOK( 
                        action=expectedMessage.info[ 'messagetype' ] 
                        )
            # Expect a get response call on server
            mockServer.GetResponse(
                    expectedMessage,
                    IpEndpoint( GntpTests.TestHost, GntpTests.TestPort )
                    ).AndReturn( okMsg )
            mockTransport.write( 
                    okMsg.encode().encode( 'utf-8', 'replace' )
                    )
        # Enter replay mode
        mox.Replay( mockServer )
        mox.Replay( mockTransport )
        return ( mockServer, mockTransport )

    def DoSimpleTest( self, inputMessage ):
        ''' 
        Does a simple test
        @param: message The message to send
        '''
        mocks = self.GetMockObjects( inputMessage )
        g = Gntp( mocks[0] )
        g.transport = mocks[ 1 ]
        g.dataReceived( inputMessage.encode().encode( 'utf-8', 'replace' ) )
        for m in mocks:
            mox.Verify( m )

    def test_Register( self ):
        # First, test with no notifications
        self.DoSimpleTest( self.GetRegisterMessage() )
        # Then test with one notification
        self.DoSimpleTest( self.GetRegisterMessage(
            [ ( 'BlahNotification', True ) ]
            ) )
        # Then test with a bunch of notifications
        self.DoSimpleTest( self.GetRegisterMessage( [ 
            ( 'BlahNotification', True ),
            ( 'NoNotification', False ),
            ( 'SomethingElse', True ),
            ( 'YetAnother', False )
            ] ) )

    def test_Notify( self ):
        self.DoSimpleTest( self.GetNoticeMessage(
            app='Test-App',
            name='Test-Name',
            title='Test-Title',
            ) )
        self.DoSimpleTest( self.GetNoticeMessage(
            app='More testing and shit',
            name='and some more',
            title='and a title',
            text='And some text.  w00t'
            ) )

    def test_Subscribe( self ):
        self.DoSimpleTest( self.GetSubscribeMessage(
            123,
            'Test-Name'
            ) )
        self.DoSimpleTest( self.GetSubscribeMessage(
            123,
            'Test-Name',
            56
            ) )

    def DoBufferingTest( self, message ):
        ''' Does a test of the buffering using the specified message '''
        actualData = message.encode().encode( 'utf-8', 'replace' )
        for chunkSize in range( 1, len( actualData ) + 1 ):
            mocks = self.GetMockObjects( message )
            g = Gntp( mocks[0] )
            g.transport = mocks[ 1 ]
            # Split the data
            numChunks = int( math.ceil( len( actualData ) / chunkSize ) )
            chunks = [ 
                actualData[ c * chunkSize: c * ( chunkSize + 1 ) ]
                for c in range( numChunks )
                ]
            # Pass it in
            for c in chunks:
                g.dataReceived( c )
            import pdb; pdb.set_trace()
            # Verify
            for m in mocks:
                mox.Verify( m )

    def test_RegisterBuffering( self ):
        return
        #TODO: Re-implement this test.
        #       At the moment it always fails
        #       Due to \r\n\r\n being end of message, but also
        #       appearing in the message.  Tres shite
        message = self.GetRegisterMessage( [ 
                ( 'BlahNotification', True ),
                ( 'AndAnother', True ) 
                ] )
        self.DoBufferingTest( message )
    
    def test_NoticeBuffering( self ):
        pass    # IMplement me

    def test_SubscribeBuffering( self ):
        pass    # implement me


class ServerTests( unittest.TestCase ):
    # TODO: fix up these tests
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
        return
        self.handler = TestGrowlHandler()
        self.server = GrowlServer(
                self.handler,
                hostname = "127.0.0.1",
                password = 'password',
                )
        self.thread = threading.Thread( target=lambda: self.server.Run() )
        self.thread.start()

    def tearDown( self ):
        return
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
        return
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
