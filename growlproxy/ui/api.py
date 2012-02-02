from flask import g
from growlproxy import models

class Servers(object):
    def GetList( self, filterFunc = None ):
        '''
        Returns a server list suitable for use by JSON
        @param: filterFunc      Optional function to use to filter the query
        '''
        serverQuery = g.db.query( 
                models.Server.id,
                models.Server.name,
                models.Server.remoteHost,
                models.Server.receiveGrowls,
                models.Server.forwardGrowls,
                models.Server.userRegistered
                )
        if filterFunc:
            serverQuery = filterFunc( serverQuery )
        # This is a fucking ugly hack, but I can't find a better way
        # to do it just now
        colList = [ 
                'id',
                'name',
                'remoteHost',
                'receiveGrowls',
                'forwardGrowls',
                'userRegistered'
                ]
        return [ dict( zip(colList,server) ) for server in serverQuery ]

    def Read( self, id ):
        '''
        Reads a list of servers
        @param: id  The id of the server to return
        @return     A list of server(s)
        '''
        if id:
            return self.GetList( lambda q: q.filter( models.Server.id == id ) )
        else:
            return self.GetList()

    def Create( self, params ):
        '''
        Creates a server
        @param: params  The details of the server to create
        '''
        pass

    def Update( self, id, params ):
        '''
        Updates a server
        @param: id      The id of the server to update
        @param: params  The parameters of the server to update
        @return         The new server record
        '''
        pass

    def Delete( self, id ):
        '''
        Deletes a server
        @param: id      The id of the server to update
        '''
        pass

