
import os
import unittest
import tempfile
import json
import growlproxy.ui
import growlproxy.db
from collections import namedtuple
from growlproxy import models
from werkzeug.datastructures import MultiDict

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

class ServerTestCase(DbTestCase):
    ''' Base class for tests requiring servers '''

    def setUp(self):
        ''' Creates a bunch of servers for use in the tests '''
        super( ServerTestCase, self ).setUp()
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


class ServerListTestCase(ServerTestCase):

    def test_ServerList(self):
        rv = self.app.get('/servers/')
        #TODO: verify the xml properly?
        assert 'There is no place like it' in rv.data
        assert 'Testing 2' in rv.data

class DeleteServerTestCase(ServerTestCase):

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


class ServerGroupTestCase(ServerTestCase):
    ''' Base class for tests requiring server group data in db '''

    def setUp(self):
        super( ServerGroupTestCase, self ).setUp()
        servers = self.db.query( models.Server )
        g = models.ServerGroup(
                name = "Group No1"
                )
        g.members.append( 
                models.ServerGroupMembership( server = servers[0] )
                )
        self.db.add( g )
        g = models.ServerGroup(
                name = "Group No2"
                )
        g.members.append( 
                models.ServerGroupMembership( server = servers[1] ) 
                )
        self.db.add( g )
        g = models.ServerGroup(
                name = "Group No3"
                )
        g.members.append(
                models.ServerGroupMembership( server = servers[0] )
                )
        g.members.append(
                models.ServerGroupMembership( server = servers[1] )
                )
        self.db.add( g )
        self.db.commit()


class GroupListTest(ServerGroupTestCase):
    def test_BasicList(self):
        rv = self.app.get( '/groups/' )
        self.assertIn( "200", rv.status )
        # For now just check that group & server names are present
        self.assertIn( "Group No1", rv.data )
        self.assertIn( "Group No2", rv.data )
        self.assertIn( "Group No3", rv.data )
        self.assertIn( "There is no place like it", rv.data )
        self.assertIn( "Testing 2", rv.data )


class DeleteGroupTests(ServerGroupTestCase):
    def DeleteGroup( self, fail=True, **kwargs ):
        ''' 
        Utility function.  Deletes a server group
        @param: id      The id of the server to delete
        @param: kwargs  The arguments to delete
        '''
        prevCount = self.db.query( models.ServerGroup ).count()
        rv = self.app.post(
                '/api/DeleteGroup/',
                data = kwargs
                )
        if fail:
            self.assertIn( "500", rv.status )
            self.assertEqual(
                    self.db.query( models.ServerGroup ).count(),
                    prevCount
                    )
        else:
            self.assertIn( "200", rv.status )
            self.assertEqual(
                    self.db.query( models.ServerGroup ).count(),
                    prevCount - 1
                    )
    
    def test_DeleteNoGroup( self ):
        self.DeleteGroup()

    def test_DeleteGarbageGroup( self ):
        self.DeleteGroup( id = 'group' ) 

    def test_DeleteGroups( self ):
        ids = [ group.id for group in self.db.query( models.ServerGroup ) ]
        for id in ids:
            self.DeleteGroup(
                    fail = False,
                    id = id
                    )

class AddServerGroupTests(ServerTestCase):

    def VerifyForm( self, data ):
        ''' 
        Verifies the add server group form is in data
        @param: data    The data to verify
        '''
        self.assertIn( 'id', data )
        self.assertIn( 'name', data )
        self.assertIn( 'Name', data )
        self.assertIn( 'members', data )
        self.assertIn( 'Members', data )
        # Verify all servers are listed
        for server in self.db.query( models.Server ):
            self.assertIn( server.name, data )
            self.assertIn( 'value="%i"' % server.id, data )

    def VerifyGroup( self, name, members ):
        '''
        Verifies that a group exists (and there is only one)
        @param: name    The name of the group
        @param: members The members of the group
        '''
        query = self.db.query( models.ServerGroup ).filter_by( name = name )
        self.assertEqual( query.count(), 1 )
        self.assertEqual( query[0].name, name )
        query = query.join( "members", "server" )
        # Now that we've joined, count should be the same as 
        # the number of members
        self.assertEqual( query.count(), len( members ) )
        for index, dbMember in enumerate( query[0].members ):
            self.assertEqual( dbMember.priority, 0 )
            self.assertEqual( dbMember.server, members[ index ] )

    def VerifyList( self, data, expectedMembers=[] ):
        '''
        Verifies the returned list
        @param: data            The data to verify
        @param: expectedMembers The members we expect in the list
        '''
        #Verify the returned server list
        for group in self.db.query( models.ServerGroup ):
            self.assertIn( group.name, data )
        for server in expectedMembers:
                self.assertIn( server.name, data )

    def AddGroup( self, expectFail=False, verifyDb=False, **kwargs ):
        ''' 
        Adds a group
        @param: expectFail  Whether or not to expect failure
        @param: verifyDb    Whether or not to verify that the 
                            group was added to db
        '''
        data = MultiDict(kwargs)
        if 'members' in data:
            #Transform into list for sending
            del data['members']
            for member in kwargs['members']:
                data.add( 'members', member.id )
        rv = self.app.post(
                '/groups/add/',
                data = data,
                follow_redirects = True
                )
        self.assertIn( "200", rv.status )
        if expectFail:
            self.VerifyForm( rv.data )
        elif verifyDb:
            self.VerifyGroup( **kwargs )
            self.VerifyList( rv.data, kwargs.get( 'members', [] ) )
        return rv

    def test_NoData( self ):
        self.AddGroup( expectFail = True )

    def test_NoName( self ):
        self.AddGroup( 
                expectFail = True,
                members = self.db.query( models.Server )
                )

    def test_NoMembers( self ):
        self.AddGroup(
                expectFail = True,
                name = "A Group"
                )

    def test_InvalidMembers( self ):
        FakeServer = namedtuple( 'FakeServer', ['id'] )
        # Test with just a fake server
        fake = FakeServer( 99999 )
        self.AddGroup(
                expectFail = True,
                name = "A Group",
                members = [ fake ]
                )
        # Test with a real and fake server
        # This will succeed, but should only add the real one
        rv = self.AddGroup(
                name = "Another Group",
                members = [ 
                    fake, 
                    self.db.query( models.Server ).first()
                    ] )
        self.assertIn( "200", rv.status )
        members = [ self.db.query( models.Server ).first() ]
        self.VerifyList( rv.data, members )
        self.VerifyGroup( "Another Group", members )

    def test_Add( self ):
        # Test with one server
        self.AddGroup(
                verifyDb = True,
                name = "A group",
                members = [ self.db.query( models.Server ).first() ]
                )
        # Test with several
        self.AddGroup(
                verifyDb = True,
                name = "Another group",
                members = self.db.query( models.Server ).all()
                )
        
