
import json
from flask import request, session, g, redirect, url_for, render_template
from flask import abort, flash, jsonify
from growlproxy.ui import app, LoadDb, forms
from growlproxy import models

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

@app.route('/api/servers', defaults={ 'id' : None }, methods=[ 'GET' ] )
@app.route('/api/servers/<int:id>', methods=[ 'GET' ])
def ServersApi(id):
    # For now, just implement the GET functionality
    # Send down all the server details, bar group membership
    serverQuery = g.db.query( 
            models.Server.id,
            models.Server.name,
            models.Server.remoteHost,
            models.Server.receiveGrowls,
            models.Server.forwardGrowls,
            models.Server.userRegistered
            )
    if id:
        serverQuery = serverQuery.filter( models.Server.id == id )
    # This is a fucking ugly hack, but I can't find a better way
    # to do it just now
    colList = [ 
            'id',
            'name',
            'remoteHost',
            'receiveGrowls',
            'forwardGrowls',
            'userRegistered'
            ]
    serverList = [ dict( zip(colList,server) ) for server in serverQuery ]
    if id:
        assert len( serverList ) == 1
        return jsonify( serverList[0] )
    else:
        return jsonify( servers=serverList )
