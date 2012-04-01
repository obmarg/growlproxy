define [ "jQuery", "Underscore", "Mustache", "views/baseEditView", "events", "collections/serverList", "text!templates/ruleEdit.html", "text!templates/ruleFilter.html" ], ($, _, Mustache, BaseEditView, events, servers, ruleEditTemplate, filterTemplate) ->
  RuleEditView = BaseEditView.extend(
    tagName: "div"
    id: "ruleEdit"
    template: ruleEditTemplate

    events:
      "click #submitButton": "submit"
      "click #cancelButton": "cancel"
      "click #deleteButton": "delete"
      #"click .deleteMember": "onDeleteMember"
      #"click .addMemberLink": "onAddMember"
      "change input" : "onChange"

    initialize: ->
      #events.on "AddGroupMember", @addGroupMember, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.bind "sync", @onSync, this
      @model.bind "error", @onError, this
      @model.filters.bind "add", @renderFilters, this
      @model.filters.bind "change", @renderFilters, this
      @model.filters.bind "destroy", @renderFilters, this
      @model.filters.bind "reset", @renderFilters, this

      @removedFilters = []

      @errors = false

      if @model.id
        @model.fetch()
        @model.filters.fetch()

      @$el.html Mustache.render(@template, @model.toJSON())
      @render

    onClose: ->
      #events.off "AddGroupMember", @addGroupMember, this
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this
      @model.unbind "sync", @onSync, this
      @model.unbind "error", @onError, this
      @model.filters.unbind "add", @renderFilters, this
      @model.filters.unbind "change", @renderFilters, this
      @model.filters.unbind "destroy", @renderFilters, this
      @model.filters.unbind "reset", @renderFilters, this
      @remove()

    render: ->
      $("#ruleNameInput").attr( 'value', @model.get( 'name' ) )
      @clearErrors()

    renderFilters: ->
      #$("#memberList").html Mustache.render( memberTemplate,
      #  members : @model.members.toJSON()
      #)

    submit: ->
      @model.save @getFields()
      if not @model.isNew()
        @model.filters.save()

    getFields: ->
      # Returns a hash of the current fields
      # (for validation or saving purposes)
      return name: $("#ruleNameInput").val()

    cancel: ->
      if not @model.isNew()
        # Need to fetch the actual members from the server, 
        # since they've probably been changed
        @model.filters.fetch()
      @close()

    delete: ->
      @model.destroy()
      events.trigger( 'closeView' )

  )
  RuleEditView
