
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
    return render_template( 'index.html' )

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

class RestApi(object):
    '''
    Decorator for REST API Functions
    @param: view    The view function to decorate
                    Function should return an object
                    mapping CRUD to functions to call
                    with callable members for
                    [ 'Create', 'Read', 'Update', 'Delete' ]
    @param: baseUrl The base url for the REST operations
                    with no trailing slash
    @paramL readParamName   The name of the dict key that
                            will be used to store the list
                            returned by read on multiple
                            objects
    '''

    def __init__( self, baseUrl, readParamName ):
        self.baseUrl = baseUrl
        self.readParamName = readParamName

    def __call__( self, view ):
        mappings = view()
        def InnerFunc(id):
            if request.method=='POST':
                mappings.Create( request.json )
                #TODO: Return some JSON?
                return "OK"
            elif request.method == 'PUT':
                update = mappings.Update( id, request.json )
                return jsonify( update )
            elif request.method == 'DELETE':
                mappings.Delete( id )
                #TODO: Figure out what to return here
                return "OK"
            # Must be a get.  Retreive stuff
            rvlist = mappings.Read(id)
            if id:
                assert len( rvlist ) < 2
                return jsonify( rvlist[0] )
            else:
                return jsonify( { self.readParamName : rvlist } ) 
        # Set up the url rules
        app.add_url_rule( 
                self.baseUrl,
                view.__name__,
                InnerFunc,
                defaults = { 'id' : None },
                methods = [ 'GET', 'POST' ]
                )
        app.add_url_rule(
                self.baseUrl + '/<int:id>',
                view.__name__,
                InnerFunc,
                methods = [ 'GET', 'PUT', 'DELETE' ]
                )
        return InnerFunc

@RestApi( '/api/servers', 'servers' )
def ServersApi():
    #return api.Servers()
    return api.SimpleApi(
                models.Server,
                {
                    'id' : models.Server.id,
                    'name' : models.Server.name,
                    'remoteHost' : models.Server.remoteHost,
                    'receiveGrowls' : models.Server.receiveGrowls,
                    'forwardGrowls' : models.Server.forwardGrowls,
                    'userRegistered' : models.Server.userRegistered
                    },
                models.Server.id
                )

