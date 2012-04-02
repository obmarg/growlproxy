define [ "jQuery", "Underscore", "Mustache", "views/baseEditView", "events", "collections/groupList", "text!templates/ruleEdit.html", "text!templates/ruleFilter.html" ], ($, _, Mustache, BaseEditView, events, groups, ruleEditTemplate, filterTemplate) ->
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
      "change input#ruleNameInput" : "onChange"
      "change #ruleFilters input" : "onFilterChange"

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
      fromGs = "<option value=''>Select Group...</option>"
      toGs = "<option value=''>Select Group...</option>"
      groups.forEach( ( group ) -> 
        id = group.id
        name = group.get( 'name' )
        fromGs += "<option value='#{id}'>#{name}</option>"
        toGs += "<option value='#{id}'>#{name}</option>"
      )
      toGroupSelect = @$el.find( '#toGroupSelect' )
      fromGroupSelect = @$el.find( '#fromGroupSelect' )
      toGroupSelect.html( toGs )
      fromGroupSelect.html( fromGs )
      if not @model.isNew()
        # If model isn't new, then select the correct groups
        toId = @model.get( 'toServerGroupId' )
        toGroupSelect.val( toId )
        fromId = @model.get( 'fromServerGroupId' )
        fromGroupSelect.val( fromId )
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
      @renderFilters()

    renderFilters: ->
      output = ""
      @model.filters.forEach( ( item ) ->
        output += Mustache.render( filterTemplate,
          filter : item.toJSON() 
        )
      )
      # TODO: The next filter call is going to need some sort of
      # "This is new" identifier
      output += Mustache.render( filterTemplate,
        filter : {}
      )
      $("#ruleFilters").html output

    onFilterChange: ( origEvent ) ->
      target = $( origEvent.currentTarget )
      filterid = target.attr( 'data-filterid' )
      if filterid == "" and target.val() != ""
        # New filter
        containerDiv = target.parents( ".ruleFilter" )
        containerDiv.prepend(
          "<a class='close deleteFilter' data-filterid='' href=''>
          <i class='icon-trash'></i>
          </a>"
        )
        containerDiv.find( 'input' ).attr( 'data-filterid', 'new' )
        $("#ruleFilters").append( Mustache.render( filterTemplate,
          filter: {}
        ) )
        # Run validation on this one

    submit: ->
      @model.save @getFields()
      if not @model.isNew()
        @model.filters.save()

    getFields: ->
      # Returns a hash of the current fields
      # (for validation or saving purposes)
      name: $("#ruleNameInput").val()
      fromServerGroupId: $( '#fromGroupSelect' ).val()
      toServerGroupId: $( '#toGroupSelect' ).val()
      sendToAll: $( '#sendToAll' ).hasClass( 'active' )
      storeIfOffline: $( '#storeIfOffline' ).hasClass( 'active' )

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
