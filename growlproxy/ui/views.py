
import json
from flask import request, session, g, redirect, url_for, render_template
from flask import abort, flash, jsonify
from growlproxy.ui import app, LoadDb
from growlproxy import models
from growlproxy.ui import api

@app.before_request
def BeforeRequest():
    """
    Run before the code for a request.  Should create database connection etc.
    """
    LoadDb()

@app.teardown_request
def TeardownRequest( exception ):
    """
    Run after request.  Tears down db connection etc.
    @param: exception   The exception that occurred (if any)
    """
    if exception:
        print "Rolling back"
        g.db.rollback()
    else:
        g.db.commit()
        g.db.close()
    g.db = None

@app.route('/')
def Index():
    return render_template( 
            'index.html',
            bootstrap=api.GetBootstrapJson( g.db )
            )

#######
# JSON REST API Stuff starts here
#######

def CreateRestView( 
        apiObject, name, idUrl=None, anonUrl=None, baseUrl=None,
        create=True, read=True, update=True, delete=True,
        registerUrls=True 
        ):
    '''
    Creates a REST API view function and registers it with the app
    @param: apiObject       The api object to pass the CRUD operations to
    @param: name            The name of the view
    @param: baseUrl         The base url for this operation.  If this is 
                            supplied, then idUrl & anonUrl will be determined
                            based on it.
    @param: idUrl           The url that handles operations with an ID
    @param: anonUrl         The url that handles operations without an ID
    @param: create          If true, create operations allowed
    @param: read            If true, read opeartions allowed
    @param: update          If true, update operations allowed
    @param: delete          If true, delete operations allowed
    @param: registerUrls    If set to False, will not register URLs
                            (mostly for testing)
    @return A view function to handle this REST API 
    '''

    def RestView( *posargs, **kwargs ):
        '''
        A REST API view
        Passes all parameters on to API Object methods
        '''
        api = apiObject( g.db )
        if request.method=='POST' and create:
            rv = api.Create( request.json, *posargs, **kwargs )
            return jsonify( rv )
        elif request.method == 'PUT' and update:
            rv = api.Update( request.json, *posargs, **kwargs )
            return jsonify( rv )
        elif request.method == 'DELETE' and delete:
            api.Delete( *posargs, **kwargs )
            #TODO: Figure out what to return herE
            return "OK"
        elif request.method == 'GET' and read:
        # Must be a get.  Retreive stuff
            rv = api.Read( *posargs, **kwargs )
            return jsonify( rv ) 
        abort( 500 )

    if registerUrls:
        # Set up the url rules
        if baseUrl and baseUrl[-1] == '/':
            # Strip out any trailing slash
            baseUrl = baseUrl[:-1]
        if idUrl or baseUrl:
            if not idUrl:
                idUrl = baseUrl + '/<int:itemId>'
            methods = []
            if read:
                methods += [ 'GET' ]
            if update:
                methods += [ 'PUT' ]
            if delete:
                methods += [ 'DELETE' ]
            app.add_url_rule(
                idUrl,
                name,
                RestView,
                methods = methods
                )
        if anonUrl or baseUrl:
            if not anonUrl:
                anonUrl = baseUrl
            methods = []
            if read:
                methods += [ 'GET' ]
            if create:
                methods += [ 'POST' ]
            app.add_url_rule( 
                    anonUrl,
                    name,
                    RestView,
                    methods = methods
                    )
    return RestView

ServersApi = CreateRestView( 
        api.ServersApi, 
        'servers', 
        baseUrl = '/api/servers' 
        )

GroupsApi = CreateRestView( 
        api.GroupsApi, 
        'groups', 
        baseUrl = '/api/groups'
        )

GroupMembersApi = CreateRestView(
        api.GroupMembersApi,
        'members',
        anonUrl = '/api/groups/<int:groupId>/members',
        idUrl = '/api/groups/<int:groupId>/members/<int:serverId>',
        update = False,
        )
