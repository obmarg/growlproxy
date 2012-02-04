define [ "jQuery", "Underscore", "Backbone", "views/serverEditView", "views/groupEditView", "collections/serverList", "collections/groupList" ], ($, _, Backbone, SeverEditView, GroupEditView, servers, groups ) ->
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
      view = new SeverEditView( model: servers.get(id) )
      @changeView view

    group: (id) ->
      view = new GroupEditView( model: groups.get(id) )
      @changeView view
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
