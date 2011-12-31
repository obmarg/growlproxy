from flask import request, session, g, redirect, url_for, render_template
from growlproxy.ui import app
from growlproxy import models
from growlproxy.models import GetDbSession

@app.before_request
def BeforeRequest():
    """
    Run before the code for a request.  Should create database connection etc.
    """
    g.db = GetDbSession()

@app.teardown_request
def TeardownRequest( exception ):
    """
    Run after request.  Tears down db connection etc.
    @param: exception   The exception that occurred (if any)
    """
    if exception:
        g.db.rollback()
    else:
        g.db.close()
    g.db = None

@app.route('/')
def index():
    return render_template( 'index.html' )
