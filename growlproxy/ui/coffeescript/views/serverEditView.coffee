define [ "jQuery", "Underscore", "Mustache", "events", "views/baseEditView", "text!templates/serverEdit.html" ], ($, _, Mustache, eventRouter, BaseEditView, Template) ->
  ServerEditView = BaseEditView.extend(
    tagName: "div"
    id: "serverEdit"
    template: Template

    events:
        "click #submitButton": "submit"
        "click #cancelButton": "close"
        "click #deleteButton": "delete"
        "change input": "onChange"

    initialize: ->
      @model.bind "change", @render, this
      @model.bind "sync", @onSync, this
      @model.bind "error", @onError, this
      @errors = false
      if @model.id
        @model.fetch()
      @render()

    onClose: ->
      @remove()
      @model.unbind "change", @render, this
      @model.unbind "sync", @onSync, this
      @model.unbind "error", @onError, this

    render: ->
      @$el.html Mustache.render(@template, @model.toJSON())
      if @model.get( 'receiveGrowls' )
      	$('#receiveGrowls').button('toggle')
      if @model.get( 'forwardGrowls' )
      	$('#forwardGrowls').button('toggle')
      @clearErrors()
      @delegateEvents()

    submit: ->
      @model.save @getFields()

    getFields: ->
      name: $("#serverNameInput").val()
      remoteHost: $("#serverRemoteHostInput").val()
      receiveGrowls: $("#receiveGrowls").hasClass("active")
      forwardGrowls: $("#forwardGrowls").hasClass("active")

    delete: ->
      # Does a delete 
      @model.destroy()
      @close()
        
  )
  ServerEditView
