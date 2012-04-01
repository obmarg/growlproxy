define [ "jQuery", "Underscore", "Backbone", "router", "views/listView", "collections/serverList", "collections/groupList", "collections/ruleList" ], ( $, _, Backbone, Router, ListView, servers, groups, rules ) ->
  
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
    ruleList = new ListView(
      el: $( '#ruleList' )
      model: rules
      itemsType: "Rules"
      itemType: "Rule"
      idType: "ruleid"
      url: "/rules"
    )
    Router.initialize()

  initialize: initialize

