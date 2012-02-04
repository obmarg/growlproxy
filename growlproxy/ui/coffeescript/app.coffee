define [ "jQuery", "Underscore", "Backbone", "router", "collections/serverList", "views/serverListView", "models/groupList", "views/groupListView" ], ( $, _, Backbone, Router, servers, ServerListView, GroupList, GroupListView ) ->
  
  initialize = ->
    Router.initialize()
    serverList = new ServerListView(model: servers)
    servers.fetch success: (coll, response) ->
      serverList.render()

    groups = new GroupList
    groupList = new GroupListView(model: groups)
    groups.fetch success: (coll, response) ->
      groupList.render()

  initialize: initialize

