'''
This file contains all the general database code (opening db etc.)
'''

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import growlproxy.ui

all = [ 
    'engine',
    'GetDbSession',
    'InitDb'
    ]

engine = None
GetDbSession = None

def OnConnectListener( dbApiConn, connRecord ):
    '''
    Listener for sqlite conection creation.
    Runs a pragma to ensure that foreign key support is enabled
    '''
    dbApiConn.execute( "PRAGMA foreign_keys=on;" )

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
    event.listen( engine, 'connect', OnConnectListener )
    GetDbSession = sessionmaker( bind = engine )
    if create:
        from growlproxy.models import Base
        Base.metadata.create_all( engine )

