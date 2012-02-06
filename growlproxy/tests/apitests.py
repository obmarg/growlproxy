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
        # Add some objects and verify individually
        actualList = []
        for item in dataSet:
            copyItem = dict( item )
            # Add a bogus attr to ensure that it's ignored
            copyItem[ 'bogusAttribute' ] = 1234
            createObj = self.testApi.Create( copyItem )
            self.assertNotIn( 'bogusAttribute', createObj )
            # Check we got back an ID
            idAttrList = [ 
                    key for key, value 
                    in self.api.mappingDict.iteritems()
                    if value == self.api.idObj[0]
                    ]
            self.assertEqual( 1, len( idAttrList ) )
            idAttrName = idAttrList[ 0 ]
            self.assertIn(
                    idAttrName,
                    createObj,
                    'No ID returned from create'
                    )
            thisId = createObj[ idAttrName ]
            # Check that all the other parameters were passed correctly
            for key, value in item.iteritems():
                self.assertIn( key, createObj )
                self.assertEqual( value, createObj[ key ] )
            # Now, make sure that a Read on this object returns OK
            readObj = self.testApi.Read( id = thisId )
            self.assertEqual( readObj, createObj ) 
            actualList.append( createObj )
        # Now that objects are created, attempt to read all of them
        readObj = self.testApi.Read()
        self.assertIn( self.api.listKeyName, readObj )
        self.assertEqual( readObj[ self.api.listKeyName ], actualList )

        # TODO: test of update functionality
        # TODO: Also test deleting 
        #       (and then query for individual + list to confirm)

class ServersApiTest( ApiTestBase ):
    __metaclass__ = DataSetMeta

    api = ServersApi
    DataSets = [
            [
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
            ]
        ]

class GroupsApiTest( ApiTestBase ):
    __metaclass__ = DataSetMeta

    api = GroupsApi
    DataSets = [
            [
                { 'name' : 'Group 1' },
                { 'name' : 'Group 2' }
            ],
            [
                { 'name' : 'Group 3' },
                { 'name' : 'Group 4' },
                { 'name' : 'Group 5' }
            ]
        ]


