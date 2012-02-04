define [ "jQuery", "Underscore", "Backbone" ], ($, _, Backbone) ->
  Server = Backbone.Model.extend(
    urlRoot: "api/servers"
    validate: (attrs) ->
  )
  Server
