
import growlproxy.db
from .models import ConfigOption

class ConfigManager(object):

    defaults = {
            'forwardAll' : False,
            'password' : 'password'
            }

    def __init__( self ):
        '''
        Constructor
        '''
        self.db = growlproxy.db.GetDbSession()

    def __setitem__( self, key, value ):
        self.db.merge( 
                ConfigOption( key, value ) 
                )
        self.db.commit()

    def __getitem__( self, key ):
        option = self.db.query( ConfigOption ).filter_by(
                key = key
                ).first()
        if option is None:
            if key in self.defaults:
                return self.defaults[ key ]
            raise KeyError( 
                "Key %s not in database" % key
                )
        return option.GetValue()

    def __getattr__( self, name ):
        try:
            return self.__getitem__( name )
        except KeyError:
            raise AttributeError

    def __setattr__( self, name, value ):
        if name == 'db':
            if 'db' not in self.__dict__:
                # If db is not yet set, then set it on instance
                return super( ConfigManager, self ).__setattr__( name, value )
        return self.__setitem__( name, value )
