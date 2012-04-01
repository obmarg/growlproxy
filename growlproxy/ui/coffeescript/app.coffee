define [ "jQuery", "Underscore", "Backbone", "router", "views/listView", "collections/serverList", "collections/groupList" ], ( $, _, Backbone, Router, ListView, servers, groups ) ->
  
  initialize = ->
    serverList = new ListView(
      el: $( '#serverList' )
      model: servers
      itemsType: "Servers"
      itemType: "Server"
      idType: "serverid"
      url: "/servers"
    )
    groupList = new ListView(
      el: $( '#groupList' )
      model: groups
      itemsType: "Groups"
      itemType: "Group"
      idType: "groupid"
      url: "/groups"
    )
    Router.initialize()

  initialize: initialize

