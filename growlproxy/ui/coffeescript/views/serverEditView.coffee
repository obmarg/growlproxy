define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/serverEdit.html" ], ($, _, Backbone, Mustache, Template) ->
  ServerEditView = Backbone.View.extend(
    tagName: "div"
    id: "serverEdit"
    template: Template
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "sync", @onSync, this
      @model.bind "destroy", @render, this
      if @model.id
        @model.fetch()
      @render()

    onClose: ->
      @model.unbind "change", @render, this
      @model.unbind "sync", @onSync, this
      @model.unbind "destroy", @render, this

    onSync: ->
      if @addToCollection?
        @addToCollection.add @model
        @addToCollection = null
        # Trigger a page change to the newly created server
        window.location.hash = '/servers/' + @model.id

    render: ->
      @$el.html Mustache.render(@template, @model.toJSON())
      if @model.get( 'receiveGrowls' )
      	$('#receiveGrowls').button('toggle')
      if @model.get( 'forwardGrowls' )
      	$('#forwardGrowls').button('toggle')
      @delegateEvents
        "click #submitButton": "submit"
        "click #cancelButton": "render"

    submit: ->
      @model.save
        name: $("#serverNameInput").val()
        remoteHost: $("#serverRemoteHostInput").val()
        receiveGrowls: $("#receiveGrowls").hasClass("active")
        forwardGrowls: $("#forwardGrowls").hasClass("active")

  )
  ServerEditView
