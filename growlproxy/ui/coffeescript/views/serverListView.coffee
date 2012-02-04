define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/serverList.html" ], ($, _, Backbone, Mustache, Template) ->
  ServerListView = Backbone.View.extend(
    el: $("#serverList")
    template: Template
    events: {}
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this

    render: ->
      js = @model.toJSON()
      @$el.html Mustache.render(@template,
        servers: js
      )
      this
  )
  ServerListView
