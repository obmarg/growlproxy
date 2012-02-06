define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/serverList.html" ], ($, _, Backbone, Mustache, Template) ->
  ServerListView = Backbone.View.extend(
    el: $("#serverList")
    template: Template
    events: {}
    initialize: ->
      @model.bind "add", @render, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @render()

    render: ->
      js = @model.toJSON()
      @$el.html Mustache.render(@template,
        servers: js
      )
      this

     onClose: ->
       @model.unbind "add", @render, this
       @model.unbind "change", @render, this
       @model.unbind "destroy", @render, this

  )
  ServerListView
