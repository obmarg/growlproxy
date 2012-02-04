define [ "jQuery", "Underscore", "Backbone", "models/server", "views/serverEditView", "models/group", "views/groupEditView" ], ($, _, Backbone, Server, SeverEditView, Group, GroupEditView) ->
  AppRouter = Backbone.Router.extend(
    routes:
      "servers/:id": "server"
      "groups/:id": "group"

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
      view = new SeverEditView(model: new Server(id: id))
      @changeView view

    group: (id) ->
      view = new GroupEditView(model: new Group(id: id))
      @changeView view
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
