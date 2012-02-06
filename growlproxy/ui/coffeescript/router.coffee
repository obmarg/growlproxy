define [ "jQuery", "Underscore", "Backbone", "views/serverEditView", "views/groupEditView", "models/server", "collections/serverList", "collections/groupList" ], ($, _, Backbone, ServerEditView, GroupEditView, Server, servers, groups ) ->
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
      view = new ServerEditView( model: servers.get(id) )
      @changeView view

    newServer: ->
      # TODO: Somehow want to add this server in to the collection
      #       after submit is clicked
      view = new ServerEditView( model: new Server )
      view.addToCollection = servers
      @changeView view

    group: (id) ->
      view = new GroupEditView( model: groups.get(id) )
      @changeView view

    newGroup: ->
      # TODO: Do something
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
