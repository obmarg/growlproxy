'''
File holds tests for the UI CRUD API classes
'''

from .modeltests import BaseModelTest
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
    '''

    def setUp(self):
        super( ApiTestBase, self ).setUp()
        self.testApi = self.api( self.db )

    def DoTest( self, dataSet ):
        '''
        Runs a basic generic test of an API object
        @param: dataSet     A list of dict's.  Each entry represents an object
                            to add/verify
        '''
        # Get the name of the id attribute
        idAttrList = [ 
                    key for key, value 
                    in self.api.mappingDict.iteritems()
                    if value == self.api.idObj[0]
                    ]
        self.assertEqual( 1, len( idAttrList ) )
        idAttrName = idAttrList[ 0 ]

        # Add some objects and verify individually
        actualList = []
        idList = []
        for item in dataSet[ 'create' ]:
            copyItem = dict( item )
            # Add a bogus attr to ensure that it's ignored
            copyItem[ 'bogusAttribute' ] = 1234
            createObj = self.testApi.Create( copyItem )
            self.assertNotIn( 'bogusAttribute', createObj )
            # Check we got back an ID
            self.assertIn(
                    idAttrName,
                    createObj,
                    'No ID returned from create'
                    )
            thisId = createObj[ idAttrName ]
            idList.append( thisId )
            # Check that all the other parameters were passed correctly
            for key, value in item.iteritems():
                self.assertIn( key, createObj )
                self.assertEqual( value, createObj[ key ] )
            # Now, make sure that a Read on this object returns OK
            readObj = self.testApi.Read( itemId = thisId )
            self.assertEqual( readObj, createObj ) 
            actualList.append( createObj )
        # Now that objects are created, attempt to read all of them
        readObj = self.testApi.Read()
        self.assertIn( self.api.listKeyName, readObj )
        self.assertEqual( readObj[ self.api.listKeyName ], actualList )

        actualList = []
        for thisId, newItem in zip( idList, dataSet[ 'update' ] ):
            # Update the item
            copyItem = dict( newItem )
            # add a bogus attribute as above
            copyItem[ 'bogusAttribute' ] = 1234
            updateObj = self.testApi.Update( copyItem, itemId=thisId )
            # check no bogus attribute
            self.assertNotIn( 'bogusAttribute', updateObj )
            # confirm that the update worked
            self.assertEqual( newItem, updateObj )
            # Now, make sure that we can read this object individually
            # This item will contain the ID, so make a copy of the 
            # dict with the ID
            readObj = self.testApi.Read( itemId = thisId )
            for key, value in newItem.iteritems():
                self.assertIn( key, readObj )
                self.assertEqual( value, readObj[ key ] )
            actualList.append( readObj )

        # Now, attempt to read all objects again
        readObj = self.testApi.Read()
        self.assertIn( self.api.listKeyName, readObj )
        self.assertEqual( readObj[ self.api.listKeyName ], actualList )

        # TODO: Also test deleting 
        #       (and then query for individual + list to confirm)

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


