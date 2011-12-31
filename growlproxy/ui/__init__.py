from flask import Flask

app = Flask(__name__)
app.config.from_object("settings")
app.config.from_envvar("GROWLPROXY_SETTINGS", silent=True)

import growlproxy.ui.views


