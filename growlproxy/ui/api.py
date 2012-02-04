from flask import g
from growlproxy import models
import json

class SimpleApi(object):
    def __init__( self, model, mappingDict, idObj ):
        '''
        Constructor
        @param: model          The model to operate on
        @param: mappingDict    Dictionary mapping { jsonName : modelProperty }
        @param: idObj          sqlalchemy id object
        '''
        self.model = model
        self.mappingDict = mappingDict
        self.idObj = idObj

    def _FilterQuery(self, query, id):
        '''
        Filters a query by id
        @param:    query     The query to filter
        @param:    id        The id to query for 
        @returns             The filtered query
        '''
        if id:
            return query.filter( self.idObj == id )
        else:
            return query

    def _GetList(self, id):
        '''
        Returns a list suitable for use by JSON
        @param: id  The id of the item to return
        '''
        query = g.db.query(
                *self.mappingDict.itervalues()
                )
        query = self._FilterQuery( query, id )
        colList = self.mappingDict.keys()
        return [ dict( zip(colList,item) ) for item in query ]

    def Read( self, id=None ):
        '''
        Reads a list of items
        @param: id  The id of the item to return
        @return     A list of item(s)
        '''
        return self._GetList( id )

    def _ConvertParameters(self, params):
        '''
        Takes in a parameter dict (generated from json) and converts to 
        dict for passing to sqlalchemy
        @param: params        The json generated input parameters
        @reutrn:              A dict suitable for passing to sqlalchemy
        '''
        rv = {}
        for key, value in params.iteritems():
            newKey = self.mappingDict[ key ].key
            rv[ newKey ] = value
        return rv

    def Update( self, id, params ):
        '''
        Does an update
        @param: id      The id of the item to update
        @param: params  The parameters of the server to update
        @return         The new server record
        '''
        #TODO: Some validation etc. would be nice
        if id is None:
            raise Exception
        query = self._FilterQuery( g.db.query( self.model ), id )
        query.update(
            self._ConvertParameters( params ),
            False
            )
        return params

    def Create( self, params ):
        '''
        Creates an item
        @param: params  The details of the item to create
        '''
        pass

    def Delete( self, id ):
        '''
        Deletes an item
        @param: id      The id of the item to delete
        '''
        pass

ServersApi = SimpleApi(
    models.Server,
    {
        'id' : models.Server.id,
        'name' : models.Server.name,
        'remoteHost' : models.Server.remoteHost,
        'receiveGrowls' : models.Server.receiveGrowls,
        'forwardGrowls' : models.Server.forwardGrowls,
        'userRegistered' : models.Server.userRegistered
        },
    models.Server.id
    )

# SimpleApi isn't really that great for Groups, because it can only really
# handle simple data.  Which this won't be, unless I split the saving into
# 2 seperate operations (which is possible I suppose, so long as I ensure
# client side validation is done first)
GroupsApi = SimpleApi(
    models.ServerGroup,
    {
        'id' : models.ServerGroup.id,
        'name' : models.ServerGroup.name
        },
    models.ServerGroup.id
    );

def GetBootstrapJson():
    #TODO: Do I want to check these json blobs for xss injection type stuff?
    return {
        'servers' : json.dumps( ServersApi.Read() ),
        'groups' : json.dumps( GroupsApi.Read() )
        }
