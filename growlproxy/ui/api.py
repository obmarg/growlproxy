from growlproxy import models
import json

#TODO: Need to stop using id as a name.  if id:  will always return true because of 
#       id builtin function

class SimpleApi(object):
    '''
    Simple API base class
    API classes should derive from this and provide the following details:
    model - The model to operate on
    mappingDict - The mapping dictionary: jsonName : modelProperty
    idObj - The instrumented sql alchemy ID column (wrapped in a tuple to 
            avoid wierd errors)
    listKeyName - The key to use for lists that are wrapped in
                  dictionaries before being returned
                  Flask.jsonify refuses to parse lists, so this
                  is required
    '''

    def __init__( self, db ):
        '''
        Constructor
        @param: db      The database to operate on
        '''
        self.db = db

    def _FilterQuery(self, query, requireFilter=True, itemId=None):
        '''
        Filters a query by id
        @param:    query            The query to filter
        @param:    reqireFilter     If true, an exception will be thrown if no 
                                    filter criteria provided
        @param:    itemId           The id to query for 
        @returns                    The filtered query
        '''
        if itemId:
            return query.filter( self.idObj[0] == itemId )
        else:
            if requireFilter:
                raise Exception( "Filter is required" )
            return query

    def GetList(self, *posargs, **kwargs):
        '''
        Returns a list suitable for use by JSON
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        '''
        query = self.db.query(
                *self.mappingDict.itervalues()
                )
        query = self._FilterQuery( query, requireFilter=False, *posargs, **kwargs )
        colList = self.mappingDict.keys()
        return [ dict( zip(colList,item) ) for item in query ]

    def Read( self, itemId=None, *posargs, **kwargs ):
        '''
        Reads a list of items
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: itemId  The id of the item to return
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        @return         A list of item(s)
        '''
        if itemId:
            # If id is set, then add it to the kwargs dict so it gets passed 
            # to GetList
            kwargs[ 'itemId' ] = itemId
        ls = self.GetList( *posargs, **kwargs )
        if itemId:
            return ls[0]
        else:
            return { self.listKeyName : ls } 

    def _ConvertParameters(self, params):
        '''
        Takes in a parameter dict (generated from json) and converts to 
        dict for passing to sqlalchemy
        @param: params        The json generated input parameters
        @return:              A dict suitable for passing to sqlalchemy
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

    def _StripInvalidItems( self, params ):
        '''
        Takes in a parameter dict (generated from json) and removes all the
        items that don't map to database columns
        @param: params      The json generated input parameters
        @return:            A dict suitable for returning to the client, 
                            with all the invalid items removed
        '''
        rv = {}
        for key, value in params.iteritems():
            if key in self.mappingDict:
                rv[ key ] = value
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
        query = self._FilterQuery( self.db.query( self.model ), *posargs, **kwargs )
        query.update(
            self._ConvertParameters( params ),
            False
            )
        return self._StripInvalidItems( params )

    def Create( self, params ):
        '''
        Creates an item
        @param: params  The details of the item to create
        '''
        obj = self.model( **self._ConvertParameters( params ) )
        self.db.add( obj )
        self.db.commit()
        #TODO: This isn't very generic.  Chances are the id isn't always going to be 
        # called id.  So figure out a fix for this at some point
        return self.Read( itemId = obj.id )

    def Delete( self, *posargs, **kwargs ):
        '''
        Deletes an item
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        '''
        pass

class ServersApi( SimpleApi ):
    '''
    Handles the Server CRUD API
    '''
    model = models.Server
    mappingDict = {
        'id' : models.Server.id,
        'name' : models.Server.name,
        'remoteHost' : models.Server.remoteHost,
        'receiveGrowls' : models.Server.receiveGrowls,
        'forwardGrowls' : models.Server.forwardGrowls,
        'userRegistered' : models.Server.userRegistered
        }
    idObj = ( models.Server.id, )
    listKeyName = 'servers'

# SimpleApi isn't really that great for Groups, because it can only really
# handle simple data.  Which this won't be, unless I split the saving into
# 2 seperate operations (which is possible I suppose, so long as I ensure
# client side validation is done first)
class GroupsApi(SimpleApi):
    '''
    Handles the Group CRUD API
    '''
    model = models.ServerGroup
    mappingDict = {
        'id' : models.ServerGroup.id,
        'name' : models.ServerGroup.name
        }
    idObj = ( models.ServerGroup.id, )
    listKeyName = 'groups'

class GroupMembersApi( SimpleApi ):
    '''
    Handles the Group Member CRUD API
    '''
    model = models.ServerGroupMembership,
    mappingDict = {
        'id' : models.ServerGroupMembership.serverId,
        'name' : models.Server.name
        }
    idObj = ( None, )
    listKeyName = 'members'

    def _FilterQuery(self, query,groupId, requireFilter=True, serverId=None):
        '''
        Filters a query by 
        @param: query           The query to filter
        @param: groupId         The group id to query for 
        @param: requireFilter   If True, will except if no filter provided
        @param: serverId        The server id to query for
        @returns             The filtered query
        '''
        rv = query.filter( 
                    models.ServerGroupMembership.groupId == groupId
                    )
        if serverId:
            rv = query.filter( 
                    models.ServerGroupMembership.serverId == serverId
                    )
        elif requireQuery:
            raise Exception( "Filter is required" )
        return rv.join( "server" )

def GetBootstrapJson( db ):
    '''
    Gets the JSON required for bootstrapping the web app
    @param: db  The database to operate on
    '''
    #TODO: Do I want to check these json blobs for xss injection type stuff?
    servers = ServersApi( db )
    groups = GroupsApi( db )
    return {
        'servers' : json.dumps( servers.GetList() ),
        'groups' : json.dumps( groups.GetList() )
        }
