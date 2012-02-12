from growlproxy import models
import json

#TODO: Need to stop using id as a name.  if id:  will always return true because of 
#       id builtin function

class SimpleApi(object):
    '''
    Simple API base class
    API classes should derive from this and provide the following details:
    model - The model to operate on
    writeMappings - The write mapping dictionary.  jsonName : modelProperty
    readMappings - The read mapping dictionary - jsonName : modelProperty
                   Defaults to the same as writeMappings.
                   Set to an empty dict for none
    filterMappings - A mapping dictionary - jsonName : modelProperty
                     This contains mappings that should be used when creating
                     and filtering a model, but should not be returned to the
                     user
    createToFilterMappings - A mapping dict - jsonCreateName : filterName
                             Maps attributes of create json to names of filters
                             Used for querying for a return object after 
                             creating an item
    idObj - The instrumented sql alchemy ID column (wrapped in a tuple to 
            avoid descriptor related errors)
            This item can probably be omitted if using a filterMappings
            dictionary
    listKeyName - The key to use for lists that are wrapped in
                  dictionaries before being returned
                  Flask.jsonify refuses to parse lists, so this
                  is required
    joins - A list of table names to join to during filter operations
            [ [ Join1Table1, Join1Table2 ], [ Join2Table1 ] ]
    '''
    readMappings = None
    writeMappings = None
    filterMappings = None
    createToFetchMappings = { 'id' : 'itemId' }
    joins = []

    def __init__( self, db ):
        '''
        Constructor
        @param: db      The database to operate on
        '''
        self.db = db
        if not self.filterMappings:
            # Set up the default itemId to idObj mapping
            self.filterMappings = { 'itemId' : self.idObj[0] }
        if self.readMappings is None:
            self.readMappings = dict( self.writeMappings )

    def _FilterQuery(self, query, requireFilter=True, doJoins=False, **kwargs):
        '''
        Filters a query by id
        @param:    query            The query to filter
        @param:    reqireFilter     If true, an exception will be thrown if no 
                                    filter criteria provided
        @parama:    doJoins         If True, will join tables as set in class 
                                    attributes
        @param:     kwargs          A dictionary containing all the filter criteria
        @returns                    The filtered query
        '''
        filtered = False
        for key, value in kwargs.iteritems():
            try:
                query = query.filter( self.filterMappings[ key ] == value )
                filtered = True
            except KeyError:
                pass
        if requireFilter and not filtered:
            raise Exception( "Filter is required" )
        if doJoins:
            for join in self.joins:
                query = query.join( *join )
        return query

    def GetList(self, *posargs, **kwargs):
        '''
        Returns a list suitable for use by JSON
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        '''
        query = self.db.query(
                *self.readMappings.itervalues()
                )
        query = self._FilterQuery( 
                query, requireFilter=False, doJoins=True,
                *posargs, **kwargs )
        colList = self.readMappings.keys()
        return [ dict( zip(colList,item) ) for item in query ]

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
                newKey = self.writeMappings[ key ].key
                rv[ newKey ] = value
            except KeyError:
                # Ignore missing keys.
                pass
        return rv

    def _StripInvalidItems( self, params ):
        '''
        Takes in a parameter dict (generated from json) and removes all the
        items that don't map to readable columns
        @param: params      The json generated input parameters
        @return:            A dict suitable for returning to the client, 
                            with all the invalid items removed
        '''
        rv = {}
        for key, value in params.iteritems():
            if key in self.readMappings:
                rv[ key ] = value
        return rv

    def _InputToFilter( self, item ):
        '''
        Converts input params into a filter dictionary for unpacking into
        a read call.
        @param: item    The item, post creation
        @return:        A dictionary for unpacking into a filter call
        '''
        rv = {}
        for key, value in self.createToFetchMappings.iteritems():
                rv[ value ] = item.__getattribute__( key )
        return rv

    def Read( self, *posargs, **kwargs ):
        '''
        Reads a list of items
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        @return         A list of item(s)
        '''
        ls = self.GetList( *posargs, **kwargs )
        numFiltersUsed = len(
                [ True for x in kwargs.iterkeys() if x in self.filterMappings ]
                )
        if numFiltersUsed == len( self.filterMappings ):
            if len( ls ) == 0:
                return None
            return ls[0]
        else:
            return { self.listKeyName : ls } 

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

    def Create( self, params, **kwargs ):
        '''
        Creates an item
        @param: params  The details of the item to create
        @parma: kwargs  Catch all extra keyword arguments 
                        (will be added into the params)
        '''
        params.update( kwargs )
        obj = self.model( **self._ConvertParameters( params ) )
        self.db.add( obj )
        self.db.commit()
        return self.Read( **self._InputToFilter( obj ) )

    def Delete( self, *posargs, **kwargs ):
        '''
        Deletes an item
        @param: posargs The positional arguments (passed on to _FilterQuery)
        @param: kwargs  The keyword arguments (passed on to _FilterQuery)
        '''
        query = self._FilterQuery( self.db.query( self.model ), *posargs, **kwargs )
        query.delete()


class ServersApi( SimpleApi ):
    '''
    Handles the Server CRUD API
    '''
    model = models.Server
    writeMappings = {
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
    writeMappings = {
        'id' : models.ServerGroup.id,
        'name' : models.ServerGroup.name
        }
    idObj = ( models.ServerGroup.id, )
    listKeyName = 'groups'

class GroupMembersApi( SimpleApi ):
    '''
    Handles the Group Member CRUD API
    '''
    model = models.ServerGroupMembership
    readMappings = {
            'id' : models.ServerGroupMembership.serverId,
            'name' : models.Server.name,
            'groupId' : models.ServerGroupMembership.groupId,
            'serverId' : models.ServerGroupMembership.serverId
            }
    writeMappings = {
            'groupId' : models.ServerGroupMembership.groupId,
            'serverId' : models.ServerGroupMembership.serverId
            }
    filterMappings = {
            'serverId' : models.ServerGroupMembership.serverId,
            'groupId' : models.ServerGroupMembership.groupId
            }
    createToFetchMappings = { 'serverId' : 'serverId', 'groupId' : 'groupId' }
    listKeyName = 'members'
    joins = [ [ 'server' ] ]


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
