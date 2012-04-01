
import os
import unittest
import tempfile
import json
import mox
import growlproxy.ui
import growlproxy.db
from collections import namedtuple
from growlproxy import models
from werkzeug.datastructures import MultiDict
from growlproxy.ui import api, views, app as globalApp

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


class RestViewTest( UiTestCase ):
    '''
    Tests the REST API class
    '''

    Input = {
        'something' : 'somethingelse',
        'test' : 1234,
        'blahdeblah' : [ 'x', 'y', 'z' ],
        'xxx' : [ { 'x' : 'y', 'y' : 'z' }, [ 'x', 'y' ] ]
        }
    Output = {
        'success' : 'OK'
        }

    def setUp( self ):
        self.mockApi = None
        super( RestViewTest, self ).setUp()

    def CallView( self, method, data, viewFunc, *posargs, **kwargs ):
        '''
        Sets up a test context, and calls the function
        Mox objects should already have been set up by this point,
        and should deal with the actual verification of this functions
        actions
        @param: method      The HTTP method to use in the request
        @param: data        The input to pass to the request.  
                            Will be JSON encoded by this function
        @param: viewFunc    The RestView function
        @param: posargs     Positional arguments ( passed to view function)
        @param: kwargs      Keyword arguments ( passed to view function)
        '''
        with globalApp.test_request_context(
                path='/',
                method=method,
                content_type='application/json',
                data=json.dumps( data )
                ):
            globalApp.preprocess_request()
            viewFunc( *posargs, **kwargs )

    def GetMock( self, db ):
        '''
        Used in place of the API Constructor function
        Checks that the correct db is passed in, then returns the mock
        object
        @param: db      The database to check
        '''
        #TODO: Check the value of db
        return self.mockApi

    def GetTestView( self, **kwargs ):
        '''
        Creates a test view
        @param: kwargs      The keyword arguments to pass on to CreateRestView
        '''
        return views.CreateRestView(
            lambda x: self.GetMock( x ),
            'TestView',
            registerUrls=False,
            **kwargs
            )

    def SetupMock( self, testType, *pargs, **kwargs ):
        '''
        Sets up a mock API object
        @param:     testType    The type of test we're setting up for
        @param:     pargs       The pos args to pass in to the test func
        @param:     kwargs      The keyword args to pass in to the test func
        '''
        self.mockApi = mox.MockObject(
                api.SimpleApi
                )
        x = None
        if testType == 'POST':
            x = self.mockApi.Create(
                    RestViewTest.Input,
                    *pargs,
                    **kwargs
                    )
        elif testType == 'PUT':
            x = self.mockApi.Update(
                    RestViewTest.Input,
                    *pargs,
                    **kwargs
                    )
        elif testType == 'DELETE':
            x = self.mockApi.Delete(
                    *pargs,
                    **kwargs
                    )
        elif testType == 'GET':
            x = self.mockApi.Read(
                    *pargs,
                    **kwargs
                    )
        if not testType == 'DELETE':
            x.AndReturn( RestViewTest.Output )
        mox.Replay( self.mockApi )

    def DoBasicTest( self, testType ):
        '''
        Does a basic test with the supplied parameters
        @param: type        String of the type of test to do 
                            One of 'POST' 'PUT' 'DELETE' 'GET'
        '''
        func = self.GetTestView()
        self.SetupMock( testType )
        self.CallView( testType, RestViewTest.Input, func )
        mox.Verify( self.mockApi )
        # Now check with some ID parameters
        # TODO: Re-implement this.  
        #       mox is behaving wierd at the moment, so not working
        #       almost as if self.mockApi is not being recreated by
        #       the call to SetupMock....
        #self.SetupMock(
        #        testType,
        #        ident=123,
        #        test='x'
        #        )
        #self.CallView( testType, RestViewTest.Input, func )
        #mox.Verify( self.mockApi )


    def test_BasicPut( self ):
        self.DoBasicTest( 'PUT' )

    def test_BasicDelete( self ):
        self.DoBasicTest( 'DELETE' )

    def test_BasicGet( self ):
        self.DoBasicTest( 'GET' )

    def test_BasicPost( self ):
        self.DoBasicTest( 'POST' )

    #TODO: Add tests of disabling operations etc.
