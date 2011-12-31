'''
This file contains all the general database code (opening db etc.)
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import growlproxy.ui

engine = create_engine( 
        'sqlite:///' + growlproxy.ui.app.config['DATABASE'],
        echo=True 
        )

GetDbSession = sessionmaker( bind = engine )

