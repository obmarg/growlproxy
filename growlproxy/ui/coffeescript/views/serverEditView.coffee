define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/serverEdit.html" ], ($, _, Backbone, Mustache, Template) ->
  ServerEditView = Backbone.View.extend(
    tagName: "div"
    id: "serverEdit"
    template: Template
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.fetch()  if @model.id

    render: ->
      @$el.html Mustache.render(@template, @model.toJSON())
      @delegateEvents "click button": "submit"

    onClose: ->
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this

    submit: ->
      @model.save
        name: $("#serverNameInput").val()
        remoteHost: $("#serverRemoteHostInput").val()
        receiveGrowls: $("#serverReceiveGrowls").attr("checked") isnt `undefined`
        forwardGrowls: $("#serverForwardGrowls").attr("checked") isnt `undefined`
  )
  ServerEditView
