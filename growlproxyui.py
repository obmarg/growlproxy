#!/usr/bin/env python

from growlproxy.ui import app
from growlproxy.db import InitDb

if __name__ == "__main__":
    InitDb()
    app.run()
