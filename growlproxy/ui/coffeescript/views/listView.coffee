define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/sidebarList.html" ], ($, _, Backbone, Mustache, Template) ->
  ListView = Backbone.View.extend(
    initialize: ->
      @model.bind "add", @render, this
      @model.bind "remove", @render, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @render()

    render: ->
      js = @model.toJSON()
      el = $(@el)
      el.html Mustache.render(Template,
        items: js
        itemsType: @options.itemsType
        itemType: @options.itemType
        idType: @options.idType
        url: @options.url
      )
      this

     onClose: ->
       @model.unbind "add", @render, this
       @model.unbind "remove", @render, this
       @model.unbind "change", @render, this
       @model.unbind "destroy", @render, this

  )
  ListView
