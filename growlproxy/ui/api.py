from flask import g
from growlproxy import models
import json

class SimpleApi(object):
    def __init__( self, model, mappingDict, idObj, listKeyName ):
        '''
        Constructor
        @param: model           The model to operate on
        @param: mappingDict     Dictionary mapping { jsonName : modelProperty }
        @param: idObj           sqlalchemy id object
        @param: listKeyName     The key to use for lists that are wrapped in
                                dictionaries before being returned
                                Flask.jsonify refuses to parse lists, so this 
                                is required
        '''
        self.model = model
        self.mappingDict = mappingDict
        self.idObj = idObj
        self.listKeyName = listKeyName

    def _FilterQuery(self, query, id=None):
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

    def GetList(self, *posargs, **kwargs):
        '''
        Returns a list suitable for use by JSON
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        '''
        query = g.db.query(
                *self.mappingDict.itervalues()
                )
        query = self._FilterQuery( query, *posargs, **kwargs )
        colList = self.mappingDict.keys()
        return [ dict( zip(colList,item) ) for item in query ]

    def Read( self, id=None, *posargs, **kwargs ):
        '''
        Reads a list of items
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: id  The id of the item to return
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        @return     A list of item(s)
        '''
        if id:
            kwargs[ 'id' ] = id
        ls = self.GetList( *posargs, **kwargs )
        if id:
            return ls[0]
        else:
            return { self.listKeyName : ls } 

    def _ConvertParameters(self, params):
        '''
        Takes in a parameter dict (generated from json) and converts to 
        dict for passing to sqlalchemy
        @param: params        The json generated input parameters
        @reutrn:              A dict suitable for passing to sqlalchemy
        '''
        rv = {}
        for key, value in params.iteritems():
            try:
                newKey = self.mappingDict[ key ].key
                rv[ newKey ] = value
            except KeyError:
                # Ignore missing keys.
                pass
        return rv

    def Update( self, params, *posargs, **kwargs ):
        '''
        Does an update
        @param: params  The parameters of the server to update
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        @return         The new server record
        '''
        #TODO: Some validation etc. would be nice
        if id is None:
            raise Exception
        query = self._FilterQuery( g.db.query( self.model ), *posargs, **kwargs )
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
        obj = self.model( **self._ConvertParameters( params ) )
        g.db.add( obj )
        return self.Read( id = obj.id )

    def Delete( self, *posargs, **kwargs ):
        '''
        Deletes an item
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
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
    models.Server.id,
    'servers'
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
    models.ServerGroup.id,
    'groups'
    );

class GroupMemberObj( SimpleApi ):
    def _FilterQuery(self, query, groupId, serverId=None):
        '''
        Filters a query by 
        @param:    query     The query to filter
        @param:    groupId   The group id to query for 
        @param:    serverId  The server id to query for
        @returns             The filtered query
        '''
        rv = query.filter( 
                    models.ServerGroupMembership.groupId == groupId
                    )
        if serverId:
            rv = query.filter( 
                    models.ServerGroupMembership.serverId == serverId
                    )
        return rv.join( "server" )

GroupMembershipApi = GroupMemberObj(
        models.ServerGroupMembership,
        {
            'id' : models.ServerGroupMembership.serverId,
            'name' : models.Server.name
            },
        None,
        'members'
        )

def GetBootstrapJson():
    #TODO: Do I want to check these json blobs for xss injection type stuff?
    return {
        'servers' : json.dumps( ServersApi.GetList() ),
        'groups' : json.dumps( GroupsApi.GetList() )
        }
