define [ "jQuery", "Underscore", "Backbone" ], ($, _, Backbone) ->
  RuleFilter = Backbone.Model.extend(
    initialize: ->
  )
  RuleFilterList = Backbone.Collection.extend(
    model: RuleFilter
    parse: (data, xhr) ->
      data.filters
    save: ->
      @forEach ( item ) ->
        item.save()
        item.new = false
  )
  Rule = Backbone.Model.extend(
    urlRoot: "api/rules"
    initialize: ->
      @filters = new RuleFilterList
      if @isNew()
      	@bind "sync", @newSync, this
      else
        @filters.url = "api/rules/" + @id + "/filters"

    newSync: ->
      # This function should only be called after the first save of the model
      @filters.url = "api/rules/" + @id + "/filters"
      @unbind "sync", @newSync, this
      @filters.save()

    addFilter: (attrs) ->
      filter = new RuleFilter( attrs )
      filter.urlRoot = @filters.url
      @filters.add( member )

    validate: (attrs) ->
      if attrs[ 'name' ]?.length < 1
      	return [ [ 'name', 'Name must not be empty' ] ]
      # TODO: Check that the servers actually exist
      return
  )
  return Rule
