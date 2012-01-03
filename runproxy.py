#!/usr/bin/env python

from growlproxy.proxy import GrowlProxy
from growlproxy.db import InitDb
import logging

if __name__ == "__main__":
    logging.basicConfig( level = logging.DEBUG )
    InitDb()
    g = GrowlProxy()
    g.Run()
