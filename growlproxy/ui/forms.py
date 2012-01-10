from flaskext.wtf import Form, TextField, Required, HiddenField, BooleanField, SubmitField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from growlproxy.models import Server, ServerGroup
from flask import g

class ServerDetails(Form):
    # TODO: Update this to use wtforms.ext.sqlalchemy.orm.model_form
    #       which is undocumented, but exactly what i want
    id = HiddenField( "Id", default='None' )
    name = TextField( "Name", [Required()] )
    remoteHost = TextField( "Remote Hostname", [Required()] )
    receiveGrowls = BooleanField( "Receive Growls From Server" )
    forwardGrowls = BooleanField( "Forward Growls To Server" )

def ServerQueryFactory():
    """ Factory method for server queries """
    return g.db.query( Server )

class GroupDetails(Form):
    id = HiddenField( "Id", default='None' )
    name = TextField( "Name", [Required()] )
    members = QuerySelectMultipleField( 
            "Members",
            [Required()], 
            query_factory = ServerQueryFactory
            )

def GroupQueryFactory():
    """ Factory method for group queries """
    return g.db.query( ServerGroup )

class RuleDetails(Form):
    id = HiddenField( "Id", default='None' )
    name = TextField( "Name", [Required()] )
    fromGroup = QuerySelectField(
            "From Group",
            [Required()],
            query_factory = GroupQueryFactory
            )
    toGroup = QuerySelectField(
            "To Group",
            [Required()],
            query_factory = GroupQueryFactory
            )
    sendToAll = BooleanField( "Send To All Servers" )
    storeIfOffline = BooleanField( "Store If Offline" )
    # TODO: Add the rest of the filter fields, and
    #       split the filter fields out into their own form
    #       or something
    applicationName = TextField( "Sending Application Name" )
    growlTitle = TextField( "Growl Title" )

