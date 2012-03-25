define [ "jQuery", "Underscore", "Backbone", "views/serverEditView", "views/groupEditView", "models/server", "models/group", "collections/serverList", "collections/groupList" ], ($, _, Backbone, ServerEditView, GroupEditView, Server, Group, servers, groups ) ->
  AppRouter = Backbone.Router.extend(
    routes:
      "servers/:id": "server"
      "servers/add/" : "newServer"
      "groups/:id": "group"
      "groups/add/" : "newGroup"

    initialize: ->
      @currentView = null

    changeView: (newView) ->
      if @currentView isnt null
        @currentView.close()
        @currentView = null
      $("#mainPanel").html ""
      $("#mainPanel").append newView.el
      newView.render()
      @currentView = newView

    server: (id) ->
      @clearSidebar()
      $( ".sidebarLink[data-serverid='#{id}']" ).addClass( "active" )
      view = new ServerEditView( model: servers.get(id) )
      @changeView view

    newServer: ->
      @clearSidebar()
      # TODO: Somehow want to add this server in to the collection
      #       after submit is clicked
      view = new ServerEditView( model: new Server )
      view.addToCollection = servers
      @changeView view

    group: (id) ->
      @clearSidebar()
      $( ".sidebarLink[data-groupid='#{id}']" ).addClass( "active" )
      view = new GroupEditView( model: groups.get(id) )
      @changeView view

    newGroup: ->
      @clearSidebar()
      view = new GroupEditView( model: new Group )
      view.addToCollection = groups
      @changeView view

    clearSidebar: ->
      $( ".sidebarLink.active" ).removeClass( "active" )
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
