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
      if @addToCollection isnt null
      	@addToCollection.add @model
      	@addToCollection = null

    render: ->
      @$el.html Mustache.render(@template, @model.toJSON())
      @delegateEvents "click button": "submit"
      $('button').button()
      #$('.buttonset').buttonset()
      # TODO: re-implement buttonset using bootstrap

    submit: ->
      @model.save
        name: $("#serverNameInput").val()
        remoteHost: $("#serverRemoteHostInput").val()
        receiveGrowls: $("#serverReceiveGrowls").attr("checked") isnt `undefined`
        forwardGrowls: $("#serverForwardGrowls").attr("checked") isnt `undefined`
  )
  ServerEditView
