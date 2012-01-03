
import os
import tempfile
import unittest
import growlproxy.db
from growlproxy.config import ConfigManager

class ConfigTests( unittest.TestCase ):
    
    def setUp(self):
        self.dbFd, self.dbPath = tempfile.mkstemp()
        growlproxy.db.InitDb( create=True, filename=self.dbPath )

    def tearDown(self):
        os.close( self.dbFd )
        os.unlink( self.dbPath )
       
    def test_AddRetrieveValues( self ):
        cm = ConfigManager()
        cm[ 'MyFace' ] = 'The Best'
        cm.YourFace = 'Fugly'

        self.assertEqual( cm[ 'MyFace' ], 'The Best' )
        self.assertEqual( cm[ 'YourFace' ], 'Fugly' )
        self.assertEqual( cm.MyFace, 'The Best' )
        self.assertEqual( cm.YourFace, 'Fugly' )

    def test_Exceptions( self ):
        cm = ConfigManager()
        with self.assertRaises( AttributeError ):
            x = cm.FakeValue
        with self.assertRaises( KeyError ):
            x = cm[ 'FakeValue' ]

    def test_Persistence( self ):
        cm = ConfigManager()
        cm[ 'Tests' ] = 'Winning'

        # Create another config manager
        cm = ConfigManager()
        self.assertEqual( cm.Tests, 'Winning' )

    def test_Defaults( self ):
        ConfigManager.defaults[ 'SaneDefault' ] = 'NoWay'
        ConfigManager.defaults[ 'InsaneDefault' ] = True
        
        cm = ConfigManager()
        self.assertEqual( cm.SaneDefault, 'NoWay' )
        self.assertEqual( cm[ 'SaneDefault' ], 'NoWay' )
        self.assertEqual( cm.InsaneDefault, True )
        assert( cm.InsaneDefault is True )

        # Reset the defaults
        ConfigManager.defaults = {}

    def test_DataTypes( self ):
        cm = ConfigManager()
        cm.ABool = True
        cm.AnotherBool = False
        cm.AnInt = 100

        assert( cm.ABool is True )
        assert( cm.AnotherBool is False )
        assert( isinstance( cm.AnInt, int ) )
        self.assertEqual( cm.AnInt, 100 )




