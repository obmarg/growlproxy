define [ "jQuery", "Underscore", "Backbone", "router", "models/serverList", "views/serverListView", "models/groupList", "views/groupListView" ], ( $, _, Backbone, Router, ServerList, ServerListView, GroupList, GroupListView ) ->
  
  initialize = ->
    Router.initialize()
    servers = new ServerList
    serverList = new ServerListView(model: servers)
    servers.fetch success: (coll, response) ->
      serverList.render()

    groups = new GroupList
    groupList = new GroupListView(model: groups)
    groups.fetch success: (coll, response) ->
      groupList.render()

  initialize: initialize

