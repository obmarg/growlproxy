
import os
import growlproxy.ui
import unittest
import tempfile

class UiTestCase(unittest.TestCase):

    def setUp(self):
        self.dbFd, dbPath = tempfile.mkstemp()
        growlproxy.ui.app.config[ 'DATABASE' ] = dbPath
        growlproxy.ui.app.config[ 'TESTING' ] = True
        self.app = growlproxy.ui.app.test_client()
        
    def tearDown(self):
        os.close( self.dbFd )
        os.unlink( growlproxy.ui.app.config[ 'DATABASE' ] )

class IndexTestCase(UiTestCase):
    def test_IndexMenu(self):
        rv = self.app.get('/')
        # TODO: Could actually parse the xml here or something
        assert 'Manage Servers' in rv.data
        assert 'Manage Groups' in rv.data
        assert 'Manage Forwarding Rules' in rv.data
        assert 'Manage Configuration' in rv.data
