define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/groupList.html" ], ($, _, Backbone, Mustache, Template) ->
  GroupListView = Backbone.View.extend(
    el: $("#groupList")
    template: Template
    events: {}
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this

    render: ->
      js = @model.toJSON()
      el = $(@el)
      el.html Mustache.render(@template,
        groups: js
      )
      this
  )
  GroupListView
