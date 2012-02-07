
import json
from flask import request, session, g, redirect, url_for, render_template
from flask import abort, flash, jsonify
from growlproxy.ui import app, LoadDb, forms
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

@app.route('/servers/')
def ServerList():
    options = {
            'servers' : g.db.query( models.Server ),
            'confirmDeleteDialog' : { 
                'itemType' : 'Server',
                'url' : url_for( 'DeleteServer' )
                }
            }
    return render_template(
            'serverList.html',
            **options
            )

@app.route('/servers/add/', methods=['GET','POST'])
def AddServer():
    form = forms.ServerDetails()
    if form.validate_on_submit():
        s = models.Server(
                form.name.data,
                form.remoteHost.data,
                form.receiveGrowls.data,
                form.forwardGrowls.data,
                True
                )
        g.db.add( s )
        flash('Success')
        return redirect( url_for( 'ServerList' ) )
    return render_template( 'addServer.html', form=form )

@app.route('/api/DeleteServer/', methods=['POST'])
def DeleteServer():
    if 'id' not in request.form:
        abort(500)
    try:
        ids = json.loads( request.form['id'] )
    except:
        abort(500)
    g.db.query( models.Server ).filter(
            models.Server.id.in_( ids ) 
            ).delete( False )
    flash( 'Deleted succesfully' )
    return "OK"

@app.route('/groups/')
def GroupList():
    groupQuery = g.db.query( models.ServerGroup ).join( 'members', 'server' )
    options = {
            'groups' : groupQuery.all(),
            'confirmDeleteDialog' : { 
                'itemType' : 'Group',
                'url' : url_for( 'DeleteGroup' )
                }
            }
    return render_template( 'groupList.html', **options )

@app.route('/groups/add/', methods=['GET','POST'])
def AddGroup():
    form = forms.GroupDetails()
    if form.validate_on_submit():
        group = models.ServerGroup(
                name = form.name.data
                )
        for member in form.members.data:
            group.members.append( 
                    models.ServerGroupMembership(
                        server = member
                        )
                    )
        g.db.add( group )
        flash('Success')
        return redirect( url_for( 'GroupList' ) )
    return render_template( 'addGroup.html', form=form )

@app.route('/api/DeleteGroup/', methods=['POST'])
def DeleteGroup():
    if 'id' not in request.form:
        abort(500)
    try:
        id = int( request.form[ 'id' ], 10 )
    except:
        abort( 500 )
    g.db.query( models.ServerGroup ).filter_by( id=id ).delete( False )
    flash( 'Deleted Succesfully' )
    return "OK"

@app.route('/rules/')
def RuleList():
    ruleQuery = g.db.query( models.ForwardRule )
    options = {
            'rules' : ruleQuery.all(),
            'confirmDeleteDialog' : { 
                'itemType' : 'Rule',
                'url' : url_for( 'DeleteRule' )
                }
            }
    return render_template( 'ruleList.html', **options )

@app.route('/api/DeleteRule/', methods=['POST'])
def DeleteRule():
    if 'id' not in request.form:
        abort( 500 )
    try:
        id = int( request.form[ 'id' ], 10 )
    except:
        abort( 500 )
    g.db.query( models.ForwardRule ).filter_by( id=id ).delete( False )
    flash( "Deleted Succesfully" )
    return "OK"

@app.route('/rules/add/', methods=['GET','POST'])
def AddRule():
    form = forms.RuleDetails()
    if form.validate_on_submit():
        rule = models.ForwardRule(
                name = form.name.data,
                fromServerGroupId = form.fromGroup.data.id,
                toServerGroupId = form.toGroup.data.id,
                sendToAll = form.sendToAll.data,
                storeIfOffline = form.storeIfOffline.data
                )
        filterDict = {}
        if form.applicationName.data:
            filterDict[ 'applicationName' ] = form.applicationName.data
        if form.growlTitle.data:
            filterDict[ 'growlTitle' ] = form.growlTitle.data
        filter = None
        if len( filterDict ) > 0:

            filter = models.RuleFilter(
                    rule = rule,
                    **filterDict
                    )
        g.db.add( rule )
        if filter:
            g.db.add( filter )
        flash('Success')
        return redirect( url_for( 'RuleList' ) )
    return render_template( 'addRule.html', form=form )

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
                idUrl = baseUrl + '/<int:id>'
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
