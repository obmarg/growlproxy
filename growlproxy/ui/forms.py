from flaskext.wtf import Form, TextField, Required, HiddenField, BooleanField, SubmitField
from wtforms.validators import Required

class ServerDetails(Form):
    id = HiddenField( "Id", default='None' )
    name = TextField( "Name", [Required()] )
    remoteHost = TextField( "Remote Hostname", [Required()] )
    receiveGrowls = BooleanField( "Receive Growls From Server" )
    forwardGrowls = BooleanField( "Forward Growls To Server" )


