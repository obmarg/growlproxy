define [ "jQuery", "Underscore", "Backbone", "views/serverEditView", "views/groupEditView", "views/ruleEditView", "models/server", "models/group", "models/rule", "collections/serverList", "collections/groupList", "collections/ruleList", "events" ], ($, _, Backbone, ServerEditView, GroupEditView, RuleEditView, Server, Group, Rule, servers, groups, rules, events ) ->
  AppRouter = Backbone.Router.extend(
    routes:
      "servers/:id": "server"
      "servers/add/" : "newServer"
      "groups/:id": "group"
      "groups/add/" : "newGroup"
      "rules/:id": "rule"
      "rules/add/" : "newRule"

    initialize: ->
      @currentView = null
      events.on( 'closeView', @onCloseEvent, @ )

    server: (id) ->
      @doEditView( id, servers, 'data-serverid', ( m ) -> 
        new ServerEditView( model: m )
      )

    newServer: ->
      @doNewView( servers, -> new ServerEditView( model: new Server ) )

    group: (id) ->
      @doEditView( id, groups, 'data-groupid', ( m ) -> 
        new GroupEditView( model: m )
      )

    newGroup: ->
      @doNewView( groups, -> new GroupEditView( model: new Group ) )

    rule: (id) ->
      @doEditView( id, rules, 'data-ruleid', ( m ) ->
        new RuleEditView( model: m )
      )

    newRule: ->
      @doNewView( rules, -> new RuleEditView( model: new Rule ) )

    doEditView: ( id, collection, dataAttr, viewFunc ) ->
      # Creates an edit view
      # Params:
      #     id - the id of the item
      #     collection - the collection to get the item from
      #     dataAttr - the data attribute name of the sidebar link
      #     viewFunc - A func that returns the edit view (accepts the model)
      @clearSidebar()
      item = collection.get( id )
      if not item?
        return
      # TODO: This active highlight thing appears to not be working
      #       (selector isn't matching i think)
      #       So fix it (at some point)
      $( ".sidebarLink[#{dataAttr}=#{id}]" ).addClass( 'active' )
      @changeView( viewFunc( item ) )

    doNewView: ( collection, viewFunc ) ->
      # Shows a new view
      # Params:
      #     collection - The collection that deals with this type
      #     viewFunc - A function that creates the view
      @clearSidebar()
      view = viewFunc()
      view.addToCollection = collection
      @changeView( view )

    changeView: (newView) ->
      @closeView()
      # TODO: Views remove themselves now, so it might be ok
      #         to skip this html( "" ) call.  Check and update
      $("#mainPanel").html ""
      $("#mainPanel").append newView.el
      newView.render()
      @currentView = newView

    clearSidebar: ->
      $( ".sidebarLink.active" ).removeClass( "active" )

    onCloseEvent: ->
      @closeView()
      @navigate( '/' )
    
    closeView: ->
      @clearSidebar()
      if @currentView isnt null
        @currentView.onClose()
        @currentView = null
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
