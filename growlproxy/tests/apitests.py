'''
File holds tests for the UI CRUD API classes
'''

from .modeltests import BaseModelTest
from growlproxy import models
from growlproxy.ui.api import *

class DataSetMeta(type):
    def __new__(cls, name, bases, attrs):
        '''
        New operator.
        Uses the DataSets attribute to create test functions
        Attribute should be a list
        '''
        #TODO: Make this a whole load more generic
        #       Class decorator *might* be suitable
        for i, dataset in enumerate( attrs['DataSets'] ):
            attrs[ 'testBasic' + str( i ) ] = ( 
                    lambda self: self.DoTest( dataset )
                    )
        return super(DataSetMeta, cls).__new__(cls, name, bases, attrs)

class ApiTestBase(BaseModelTest):
    '''
    Base class for API tests
    Subclasses should provide the following class variables:
    api - The API class to test
    DataSets - The data sets to run on
    IdAttrName - The id attribute name (defaults to id)
    FilterMapping - A dictionary mapping object attributes to their 
                    corresponding filter dict attribute name
    FilterChangesOnUpdate - Boolean indicating whether the filter values
                            will need recalculated after an update.
                            Default False
    '''
    IdAttrName = 'id'
    FilterMapping = { 'id' : 'itemId' }
    FilterChangesOnUpdate = False

    def setUp(self):
        super( ApiTestBase, self ).setUp()
        self.testApi = self.api( self.db )

    def GetFilterDict( self, item ):
        '''
        Gets a dictionary to unpack and pass to the Read/Update/Delete
        API calls for filtering
        @param: item    The item to filter for
        '''
        rv = {}
        for sourceKey, destKey in self.FilterMapping.iteritems():
                rv[ destKey ] = item[ sourceKey ]
        return rv

    def DoTest( self, dataSet ):
        '''
        Runs a basic generic test of an API object
        @param: dataSet     A list of dict's.  Each entry represents an object
                            to add/verify
        '''
        # Add some objects and verify individually
        actualList = []
        filterList = []
        for item in dataSet[ 'create' ]:
            copyItem = dict( item )
            # Add a bogus attr to ensure that it's ignored
            copyItem[ 'bogusAttribute' ] = 1234
            createObj = self.testApi.Create( copyItem )
            self.assertNotIn( 'bogusAttribute', createObj )
            # Check we got back an ID
            self.assertIn(
                    self.IdAttrName,
                    createObj,
                    'No ID returned from create'
                    )
            thisFilter = self.GetFilterDict( createObj )
            filterList.append( thisFilter )
            # Check that all the other parameters were passed correctly
            for key, value in item.iteritems():
                self.assertIn( key, createObj )
                self.assertEqual( value, createObj[ key ] )
            # Now, make sure that a Read on this object returns OK
            readObj = self.testApi.Read( **thisFilter )
            self.assertEqual( readObj, createObj ) 
            actualList.append( createObj )
        # Now that objects are created, attempt to read all of them
        readObj = self.testApi.Read()
        self.assertIn( self.api.listKeyName, readObj )
        self.assertEqual( readObj[ self.api.listKeyName ], actualList )

        actualList = []
        # Need to update the filter here in some cases, as updating the item
        # causes updates to the filter.  DAMN YOU lack of primary keys
        if self.FilterChangesOnUpdate:
            newFilterList = [ self.GetFilterDict( obj ) for obj in dataSet[ 'update' ] ]
        else:
            newFilterList = filterList
        for thisFilter, newFilter, newItem in zip( 
                filterList, newFilterList, dataSet[ 'update' ] 
                ):
            # Update the item
            copyItem = dict( newItem )
            # add a bogus attribute as aboe
            copyItem[ 'bogusAttribute' ] = 1234
            updateObj = self.testApi.Update( copyItem, **thisFilter )
            # check no bogus attribute
            self.assertNotIn( 'bogusAttribute', updateObj )
            # confirm that the update worked
            self.assertEqual( newItem, updateObj )
            # Now, make sure that we can read this object individually
            readObj = self.testApi.Read( **newFilter )
            for key, value in newItem.iteritems():
                self.assertIn( key, readObj )
                self.assertEqual( value, readObj[ key ] )
            actualList.append( readObj )
            # Check that updating without an id excepts
            self.assertRaises( Exception, self.testApi.Update, copyItem )
       
        # Switch to the new filter list
        filterList = newFilterList

        # Now, attempt to read all objects again
        readObj = self.testApi.Read()
        self.assertIn( self.api.listKeyName, readObj )
        self.assertEqual( readObj[ self.api.listKeyName ], actualList )

        # Now delete the objects individually
        for i, thisFilter in enumerate( filterList ):
            self.testApi.Delete( **thisFilter )
            self.db.commit()
            self.db.expire_all()
            # Ensure that we can't read this item specifically
            readObj = self.testApi.Read( **thisFilter )
            self.assertEqual( readObj, None )
            # Now ensure that we only get the rest of the items when
            # we ask for everything
            restItems = self.testApi.Read()
            self.assertIn( self.api.listKeyName, restItems )
            self.assertEqual( 
                    restItems[ self.api.listKeyName ],
                    actualList[ i+1: ]
                    )
            # Finally, check that deleting without an ID excepts
            # (and doesn't delete anything)
            self.assertRaises( Exception, self.testApi.Delete )
            restItems = self.testApi.Read()
            self.assertIn( self.api.listKeyName, restItems )
            self.assertEqual(
                    restItems[ self.api.listKeyName ],
                    actualList[ i+1: ]
                    )


class ServersApiTest( ApiTestBase ):
    __metaclass__ = DataSetMeta

    api = ServersApi
    DataSets = [{
        'create' : [
                {
                    'name' : 'Test Server 1',
                    'remoteHost' : '192.168.5.6',
                    'receiveGrowls' : False,
                    'forwardGrowls' : True
                },
                {
                    'name' : 'Test Server 2',
                    'remoteHost' : '192.168.6.7',
                    'receiveGrowls' : True,
                    'forwardGrowls' : False
                }
            ],
        'update' : [
                {
                    'name' : 'Testorama',
                    'remoteHost' : '192.168.9.10',
                    'receiveGrowls' : False,
                    'forwardGrowls' : True
                },
                {
                    'name' : 'Test Server 2',
                    'remoteHost' : '192.168.10.1',
                    'receiveGrowls' : True,
                    'forwardGrowls' : False
                }
            ],
        }]

class GroupsApiTest( ApiTestBase ):
    __metaclass__ = DataSetMeta

    api = GroupsApi
    DataSets = [
            {
                'create' : [
                    { 'name' : 'Group 1' },
                    { 'name' : 'Group 2' }
                    ],
                'update' : [
                    { 'name' : 'GRP1' },
                    { 'name' : 'GRP2' }
                    ],
            },
            {
                'create' : [
                    { 'name' : 'Group 3' },
                    { 'name' : 'Group 4' },
                    { 'name' : 'Group 5' }
                ],
                'update' : [
                    { 'name' : 'GRP 3' },
                    { 'name' : 'GRP 4' },
                    { 'name' : 'GRP 5' }
                ]
            }
        ]

class GroupMembersApiTest( ApiTestBase ):
    __metaclass__ = DataSetMeta

    api = GroupMembersApi
    FilterChangesOnUpdate = True
    FilterMapping = { 'serverId' : 'serverId', 'groupId' : 'groupId' }

    def setUp( self ):
        '''
        Sets up some servers and groups (needed for this test to work)
        '''
        super( GroupMembersApiTest, self ).setUp()
        servers = [ 
                models.Server(
                    ourId=1,
                    name='Server 1',
                    remoteHost='192.157.2.3',
                    receiveGrowls=True,
                    forwardGrowls=True
                    ),
                models.Server(
                    ourId=2, 
                    name='Server 2',
                    remoteHost='192.165.7.4',
                    receiveGrowls=True,
                    forwardGrowls=True
                    )
                ]
        groups = [
                models.ServerGroup( ourId=1, name='Group 1' ),
                models.ServerGroup( ourId=2, name='Group 2' )
                ]
        self.db.add( servers[ 0 ] )
        self.db.add( servers[ 1 ] )
        self.db.add( groups[ 0 ] )
        self.db.add( groups[ 1 ] )
        self.db.commit()

    # This test isn't going to be perfect.  Won't verify the returned 
    # server name for one thing.  Would be good to add a test of this
    # at some point
    # Also would be good to verify that partial filters (i.e. groupId 
    # filters but no serverId) return a list rather than an object.
    DataSets = [
            {
                'create' : [ 
                    { 'serverId' : 1, 'groupId' : 1 },
                    { 'serverId' : 2, 'groupId' : 2 }
                    ],
                'update' : [
                    { 'serverId' : 1, 'groupId' : 2 },
                    { 'serverId' : 2, 'groupId' : 1 }
                    ]
            }
        ]

