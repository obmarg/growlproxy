define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/groupEdit.html" ], ($, _, Backbone, Mustache, Template) ->
  GroupEditView = Backbone.View.extend(
    tagName: "dl"
    id: "groupEdit"
    template: Template
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.fetch()  if @model.id

    render: ->
      $(@el).html Mustache.render(@template, @model.toJSON())
      @delegateEvents "click button": "submit"

    onClose: ->
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this

    submit: ->
      @model.save name: $("#groupNameInput").val()
  )
  GroupEditView
