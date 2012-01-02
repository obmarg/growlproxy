'''
This file contains all the general database code (opening db etc.)
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import growlproxy.ui

engine = None
GetDbSession = None

def InitDb( create=False, filename=None ):
    ''' 
    Initialises GetDbSession with the correct path from configuration

    @param: create      If true, the database will be created
    @param: filename    If set, this will override the configuration
                        filename
    '''
    global engine, GetDbSession
    if filename is None:
        filename = growlproxy.ui.app.config['DATABASE']
    engine = create_engine( 
        'sqlite:///' + filename,
        echo=True 
        )
    GetDbSession = sessionmaker( bind = engine )
    if create:
        from growlproxy.models import Base
        Base.metadata.create_all( engine )

