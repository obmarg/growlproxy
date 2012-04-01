define [ "jQuery", "Underscore", "Backbone", "views/serverEditView", "views/groupEditView", "models/server", "models/group", "collections/serverList", "collections/groupList", "events" ], ($, _, Backbone, ServerEditView, GroupEditView, Server, Group, servers, groups, events ) ->
  AppRouter = Backbone.Router.extend(
    routes:
      "servers/:id": "server"
      "servers/add/" : "newServer"
      "groups/:id": "group"
      "groups/add/" : "newGroup"

    initialize: ->
      @currentView = null
      events.on( 'closeView', @closeView, @ )

    changeView: (newView) ->
      @closeView()
      $("#mainPanel").html ""
      $("#mainPanel").append newView.el
      newView.render()
      @currentView = newView

    server: (id) ->
      @clearSidebar()
      server = servers.get( id )
      if not server?
        return
      $( ".sidebarLink[data-serverid='#{id}']" ).addClass( "active" )
      view = new ServerEditView( model: server )
      @changeView view

    newServer: ->
      # TODO: Somehow want to add this server in to the collection
      #       after submit is clicked
      view = new ServerEditView( model: new Server )
      view.addToCollection = servers
      @changeView view

    group: (id) ->
      @clearSidebar()
      group = groups.get(id)
      if not group?
        return
      $( ".sidebarLink[data-groupid='#{id}']" ).addClass( "active" )
      view = new GroupEditView( model: group )
      @changeView view

    newGroup: ->
      @clearSidebar()
      view = new GroupEditView( model: new Group )
      view.addToCollection = groups
      @changeView view

    clearSidebar: ->
      $( ".sidebarLink.active" ).removeClass( "active" )

    closeView: ->
      @clearSidebar()
      if @currentView isnt null
        @currentView.close()
        @currentView = null
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
