define [ "jQuery", "Underscore", "Backbone", "router", "collections/serverList", "views/serverListView", "collections/groupList", "views/groupListView" ], ( $, _, Backbone, Router, servers, ServerListView, groups, GroupListView ) ->
  
  initialize = ->
    Router.initialize()
    serverList = new ServerListView(model: servers)
    groupList = new GroupListView(model: groups)

  initialize: initialize

