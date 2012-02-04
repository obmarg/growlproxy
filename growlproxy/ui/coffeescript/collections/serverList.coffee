define [ "jQuery", "Underscore", "Backbone", "models/server" ], ($, _, Backbone, Server) ->
  ServerList = Backbone.Collection.extend(
    model: Server
    url: "/api/servers"
    parse: (models, xhr) ->
      models.servers
  )
  new ServerList
