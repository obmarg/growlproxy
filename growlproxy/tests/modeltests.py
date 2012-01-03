
import os
import tempfile
import unittest
import growlproxy.db
from growlproxy.models import *

class ModelTests(unittest.TestCase):
    ''' Base class for model tests '''

    def setUp(self):
        self.dbFd, self.dbPath = tempfile.mkstemp()
        growlproxy.db.InitDb( create=True, filename=self.dbPath )
        self.db = growlproxy.db.GetDbSession()

    def tearDown(self):
        os.close( self.dbFd )
        os.unlink( self.dbPath )

    def test_Cascades( self ):
        ''' 
        Tests cascading of updates & deletes
        This also effectively tests adding, deleting and querying of most/all 
        records
        '''
        # First create some records
        servers = [ 
                Server( 'Server1', '127.0.0.1' ),
                Server( 'Server2', '127.0.0.2' ),
                Server( 'Server3', '127.0.0.3' )
                ]
        for s in servers:
            self.db.add( s )

        groups = [
                ServerGroup( 'Group1' ),
                ServerGroup( 'Group2' ),
                ]

        groups[0].members.append(
                ServerGroupMembership( 
                    server = servers[0]
                    ) )
        groups[0].members.append(
                ServerGroupMembership(
                    server = servers[1]
                    ) )
        groups[1].members.append(
                ServerGroupMembership(
                    server = servers[2]
                    ) )

        for g in groups:
            self.db.add( g )

        rules = [
                ForwardRule( 
                    'Rule1',
                    groups[0].id,
                    groups[1].id
                    ),
                ForwardRule(
                    "Rule2",
                    groups[1].id,
                    groups[0].id
                    ) ]

        rules[ 0 ].filters.append(
                RuleFilter(
                    applicationName = "Something"
                    ) )
        rules[ 1 ].filters.append(
                RuleFilter( 
                    growlTitle = "Something"
                    ) )
        
        for r in rules:
            self.db.add( r )

        # Commit the transaction
        self.db.commit()

        #Reload the session, just in case stuff is cached
        self.db.close()
        growlproxy.db.InitDb( filename = self.dbPath )
        self.db = growlproxy.db.GetDbSession()

        # Check that all our records are there
        query = self.db.query( Server )
        self.assertEqual( query.count(), 3 )
        query = self.db.query( ServerGroup )
        self.assertEqual( query.count(), 2 )
        query = query.filter_by( 
                name="Group1" 
                ).join( 'members', 'server' )
        self.assertEqual( query.count(), 2 )
        query = self.db.query( ServerGroup ).filter_by( 
                name="Group2" 
                ).join( "members", "server" )
        self.assertEqual( query.count(), 1 )
        self.assertEqual(
            self.db.query( ServerGroupMembership ).count(),
            3
            )

        #TODO: Add rule & filter support to these tests
        #       Currently, we just create records don't
        #       actually query against them
        

        # Now delete a server and make sure cascading works
        self.db.query( Server ).filter_by(
                name = "Server1"
                ).delete()
        self.assertEqual(
                self.db.query( ServerGroupMembership ).count(),
                2
                )
        query = self.db.query( ServerGroup ).filter_by(
                name = "Group1"
                ).join( "members", "server" )
        self.assertEqual(
                query.count(),
                1
                )
        self.assertEqual(
                query[0].members[0].server.name,
                "Server2"
                )

        # Ensure that Group2 still contains server 3
        query = self.db.query( ServerGroup ).filter_by(
                name = "Group2"
                ).join( "members", "server" )
        self.assertEqual(
                query.count(),
                1
                )
        self.assertEqual(
                query[0].members[0].server.name,
                "Server3"
                )




