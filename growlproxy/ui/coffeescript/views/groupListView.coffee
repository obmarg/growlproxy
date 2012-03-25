define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/groupList.html" ], ($, _, Backbone, Mustache, Template) ->
  GroupListView = Backbone.View.extend(
    el: $("#groupList")
    template: Template
    events: {}
    initialize: ->
      @model.bind "add", @render, this
      @model.bind "remove", @render, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @render()

    render: ->
      js = @model.toJSON()
      el = $(@el)
      el.html Mustache.render(@template,
        groups: js
      )
      this

     onClose: ->
       @model.unbind "add", @render, this
       @model.unbind "remove", @render, this
       @model.unbind "change", @render, this
       @model.unbind "destroy", @render, this

  )
  GroupListView
