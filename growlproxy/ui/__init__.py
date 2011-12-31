from flask import Flask, g

app = Flask(__name__)
app.config.from_object("settings")
app.config.from_envvar("GROWLPROXY_SETTINGS", silent=True)

def LoadDb():
    """ Creates the database in g.db """
    from growlproxy.db import GetDbSession
    g.db = GetDbSession()

import growlproxy.ui.views
