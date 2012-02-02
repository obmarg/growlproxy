from flask import g

class SimpleApi(object):
    def __init__( self, model, mappingDict, filterObj=None ):
        '''
        Constructor
        @param: model          The model to operate on
        @param: mappingDict    Dictionary mapping { jsonName : modelProperty }
        @param: filterFunc     Filter function for Read operations
        '''
        self.model = model
        self.mappingDict = mappingDict
        self.filterObj = filterObj

    def _FilterQuery(self, query, id):
        '''
        Filters a query by id
        @param:    query     The query to filter
        @param:    id        The id to query for 
        @returns             The filtered query
        '''
        if id:
            return query.filter( self.filterObj == id )
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

    def Read( self, id ):
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
