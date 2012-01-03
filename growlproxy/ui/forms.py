from flaskext.wtf import Form, TextField, Required, HiddenField, BooleanField, SubmitField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from growlproxy.models import Server
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

