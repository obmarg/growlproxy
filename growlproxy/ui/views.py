
import json
from flask import request, session, g, redirect, url_for, render_template
from flask import abort, flash
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
