
import os
import unittest
import tempfile
import json
import growlproxy.ui
import growlproxy.db
from growlproxy import models

class UiTestCase(unittest.TestCase):
    ''' Base class for all ui tests '''

    def setUp(self):
        self.dbFd, dbPath = tempfile.mkstemp()
        growlproxy.ui.app.config[ 'DATABASE' ] = dbPath
        growlproxy.ui.app.config[ 'TESTING' ] = True
        growlproxy.ui.app.config[ 'CSRF_ENABLED' ] = False
        growlproxy.db.InitDb( create=True )
        self.app = growlproxy.ui.app.test_client()
        
    def tearDown(self):
        os.close( self.dbFd )
        os.unlink( growlproxy.ui.app.config[ 'DATABASE' ] )

class DbTestCase(UiTestCase):
    ''' Base class for ui tests that need direct db access '''

    def setUp(self):
        super( DbTestCase, self ).setUp()
        self.db = growlproxy.db.GetDbSession()

    def tearDown(self):
        self.db.close()
        self.db = None
        super( DbTestCase, self ).tearDown()

class IndexTestCase(UiTestCase):
    def test_IndexMenu(self):
        rv = self.app.get('/')
        # TODO: Could actually parse the xml here or something
        assert 'Manage Servers' in rv.data
        assert 'Manage Groups' in rv.data
        assert 'Manage Forwarding Rules' in rv.data
        assert 'Manage Configuration' in rv.data

class ServerListTestCase(DbTestCase):
    ''' 
    Contains tests for the server list & delete server functionality.
    Technically delete server stuff should maybe be in a different class,
    but they both require creation of some servers in the database, so seems
    sensible to group them together
    '''

    def setUp(self):
        ''' Creates a bunch of servers to use in the tests '''
        super( ServerListTestCase, self ).setUp()
        self.db.add( models.Server( 
            name='There is no place like it',
            remoteHost='127.0.0.1',
            receiveGrowls = True,
            forwardGrowls = True,
            userRegistered = True
            ) )
        self.db.add( models.Server(
            name= 'Testing 2',
            remoteHost = '192.168.5.1'
            ) )
        self.db.commit()

    def test_ServerList(self):
        rv = self.app.get('/servers/')
        #TODO: verify the xml properly?
        assert 'There is no place like it' in rv.data
        assert 'Testing 2' in rv.data

    def test_DeleteNoServer(self):
        # Test sending no id
        rv = self.app.post('/api/DeleteServer/' )
        self.assertIn( '500', rv.status ) 

    def test_DeleteGarbageServer(self):
        # Test sending garbage server ids
        rv = self.app.post(
                '/api/DeleteServer/',
                data = { 'id' : 'fuckingbullshit' }
                )
        self.assertIn( '500', rv.status ) 

    def test_DeleteOneServer(self):
        id = self.db.query( models.Server ).first().id
        rv = self.app.post(
                '/api/DeleteServer/',
                data = { 'id' : json.dumps( [ id ] ) }
                )
        self.assertIn( '200', rv.status )
        self.assertEqual(
                self.db.query( models.Server ).count(),
                1
                )

    def test_DeleteAllServers(self):
        ids = [ entry[0] for entry in self.db.query( models.Server.id ).all() ]
        rv = self.app.post(
                '/api/DeleteServer/',
                data = { 'id' : json.dumps( ids ) }
                )
        self.assertIn( '200', rv.status )
        self.assertEqual( 
                self.db.query( models.Server ).count(),
                0
                )

class AddServerTestCase(DbTestCase):
    
    def VerifyForm( self, data, validationErrors=False ):
        ''' 
        Utility function, verifies that the form appears to be present in data
        @param: data                The data to verify
        @param: validationErrors    If true, check for error 
                                    text in data
        '''
        self.assertIn( 'id', data )
        self.assertIn( 'Name', data )
        self.assertIn( 'Remote Hostname', data )
        self.assertIn( 'Receive Growls', data )
        self.assertIn( 'Forward Growls', data )
        if validationErrors:
            self.assertIn( 'class="errors"', data )

    def AddServer( self, expectFail=False, verifyDb=False, **kwargs ):
        ''' 
        Utility function.  Attempts to add server with the supplied arguments
        @param: expectFail      If true, expects failure of adding server
        @param: verifyDb        If true, verifies the server is in the database
        '''
        rv = self.app.post(
                '/servers/add/',
                data = kwargs,
                follow_redirects = True
                )
        if expectFail:
            self.VerifyForm( rv.data, True )
        elif verifyDb:
            self.VerifyServerInDb( **kwargs )
        return rv

    def VerifyServerInDb( 
            self,
            name,
            remoteHost,
            receiveGrowls=False,
            forwardGrowls=False
            ):
        ''' 
        Utility function.   Verifies a single server is in the database
        '''
        query = self.db.query( models.Server )
        self.assertEqual( query.count(), 1 )
        s = query.first()
        self.assertEqual( s.name, name )
        self.assertEqual( s.remoteHost, remoteHost )
        self.assertEqual( s.receiveGrowls, receiveGrowls )
        self.assertEqual( s.forwardGrowls, forwardGrowls )
        self.assertEqual( s.userRegistered, True )
    
    def test_InitialGet(self):
        # Get the form and validate all fields seem to be 
        # there
        rv = self.app.get( '/servers/add/' )
        self.assertIn( '200', rv.status )
        self.VerifyForm( rv.data )
        
    def test_MissingFields(self):
        rv = self.AddServer( True )
        rv = self.AddServer( True, name='BLAH' )
        rv = self.AddServer( True, remoteHost='BLAH' )

    def test_AddingServers(self):
        rv = self.AddServer( 
                verifyDb = True,
                name='TEST1',
                remoteHost = 'TestHost'
                )
        #TODO: Verify the "server added" type message when it's implemented

        # Check that the new server is in the returned list
        self.assertIn( "200", rv.status )
        self.assertIn( "TEST1", rv.data )

        # Delete all, and add another
        self.db.query( models.Server ).delete( False )
        self.db.commit()

        rv = self.AddServer(
                verifyDb = True,
                name = 'TEST2',
                remoteHost = 'TestHost',
                receiveGrowls = True
                )

        self.assertIn( "200", rv.status )
        self.assertIn( "TEST2", rv.data )

        self.db.query( models.Server ).delete( False )
        self.db.commit()

        rv = self.AddServer(
                verifyDb = True,
                name = 'TEST3',
                remoteHost = 'TestHost',
                forwardGrowls = True
                )
        self.assertIn( "200", rv.status )
        self.assertIn( "TEST3", rv.data )

    def test_AddSeveralServers( self ):
        names = [ 'Server' + str(i) for i in range( 5 ) ]
        for name in names:
            rv = self.AddServer(
                    name = name,
                    remoteHost = 'TestHost'
                    )
        #Verify returned page
        self.assertIn( "200", rv.status )
        for name in names:
            self.assertIn( name, rv.data )
        # Check that we have the correct number of servers in db.  
        # Ignore actual data (for now at least)
        self.assertEqual( self.db.query( models.Server ).count(), len( names ) )
