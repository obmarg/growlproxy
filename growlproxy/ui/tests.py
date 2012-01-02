
import os
import unittest
import tempfile
import json
import growlproxy.ui
import growlproxy.db
from growlproxy import models

class UiTestCase(unittest.TestCase):

    def setUp(self):
        self.dbFd, dbPath = tempfile.mkstemp()
        growlproxy.ui.app.config[ 'DATABASE' ] = dbPath
        growlproxy.ui.app.config[ 'TESTING' ] = True
        growlproxy.db.InitDb( create=True )
        self.app = growlproxy.ui.app.test_client()
        
    def tearDown(self):
        os.close( self.dbFd )
        os.unlink( growlproxy.ui.app.config[ 'DATABASE' ] )

class IndexTestCase(UiTestCase):
    def test_IndexMenu(self):
        rv = self.app.get('/')
        # TODO: Could actually parse the xml here or something
        assert 'Manage Servers' in rv.data
        assert 'Manage Groups' in rv.data
        assert 'Manage Forwarding Rules' in rv.data
        assert 'Manage Configuration' in rv.data

class ServerListTestCase(UiTestCase):
    def setUp(self):
        ''' Creates a bunch of servers to use in the tests '''
        super( ServerListTestCase, self ).setUp()
        self.db = growlproxy.db.GetDbSession()
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

    def tearDown(self):
        self.db.close()
        self.db = None
        super( ServerListTestCase, self ).tearDown()

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


