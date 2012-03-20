define [ "jQuery", "Underscore", "Backbone", "router", "collections/serverList", "views/serverListView", "collections/groupList", "views/groupListView" ], ( $, _, Backbone, Router, servers, ServerListView, groups, GroupListView ) ->
  
  initialize = ->
    serverList = new ServerListView(model: servers)
    groupList = new GroupListView(model: groups)
    Router.initialize()

  initialize: initialize

