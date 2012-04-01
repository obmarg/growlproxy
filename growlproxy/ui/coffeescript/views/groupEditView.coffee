define [ "jQuery", "Underscore", "Mustache", "views/baseEditView", "events", "collections/serverList", "text!templates/groupEdit.html", "text!templates/groupMember.html" ], ($, _, Mustache, BaseEditView, events, servers, groupEditTemplate, memberTemplate) ->
  GroupEditView = BaseEditView.extend(
    tagName: "div"
    id: "groupEdit"
    template: groupEditTemplate

    events:
      "click #submitButton": "submit"
      "click #cancelButton": "cancel"
      "click #deleteButton": "delete"
      "click .deleteMember": "onDeleteMember"
      "click .addMemberLink": "onAddMember"
      "change input" : "onChange"

    initialize: ->
      events.on "AddGroupMember", @addGroupMember, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.bind "sync", @onSync, this
      @model.bind "error", @onError, this
      @model.members.bind "add", @renderMembers, this
      @model.members.bind "change", @renderMembers, this
      @model.members.bind "destroy", @renderMembers, this
      @model.members.bind "reset", @renderMembers, this

      @removedMembers = []

      @errors = false

      if @model.id
        @model.fetch()
        @model.members.fetch()

      @$el.html Mustache.render(@template, @model.toJSON())
      @render

    onClose: ->
      events.off "AddGroupMember", @addGroupMember, this
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this
      @model.unbind "sync", @onSync, this
      @model.unbind "error", @onError, this
      @model.members.unbind "add", @renderMembers, this
      @model.members.unbind "change", @renderMembers, this
      @model.members.unbind "destroy", @renderMembers, this
      @model.members.unbind "reset", @renderMembers, this
      @remove()

    render: ->
      $("#groupNameInput").attr( 'value', @model.get( 'name' ) )
      $("#addMemberList").html( "" )
      servers.forEach( ( element ) ->
        id = element.get( 'id' )
        name = element.get( 'name' )
        $("#addMemberList").append(
          $("<li>").html(
            "<a href='#' class='addMemberLink' data-id='#{id}'>#{name}</a>"
          )
        )
      )
      @clearErrors()

    renderMembers: ->
      $("#memberList").html Mustache.render( memberTemplate,
        members : @model.members.toJSON()
      )

    addGroupMember: ( serverId ) ->
      # TODO: Add priority and shit to this
      @model.addMember(
        serverId: serverId
        name: servers.get( serverId ).attributes.name
      )

    onAddMember: ( origEvent ) ->
      serverToAdd = $( origEvent.currentTarget ).attr( 'data-id' )
      @addGroupMember( serverToAdd )
      #TODO: Remove this server from the dropdown
      return false

    onDeleteMember: ( origEvent ) ->
      id = $( origEvent.currentTarget ).parent().attr( 'data-memberid' ) 
      # TODO: Probably want to fix this up a bit.
      #         Suspect it won't work on items that haven't been submitted
      #         to server (as they have no id.  just a serverId  or whatever)
      #         Also would be good to animate the removing of items from list
      toRemove = @model.members.get( id )
      @model.members.remove( toRemove )
      $( origEvent.currentTarget.parentElement ).remove()
      toRemove.urlRoot = @model.members.url
      @removedMembers.push toRemove
    
    submit: ->
      # TODO: Would be good to move the burden of deleting members to the
      #       collection/model rather than here.
      item.destroy() for item in @removedMembers
      @removedMembers = []
      @model.save @getFields()
      if not @model.isNew()
        @model.members.save()

    getFields: ->
      # Returns a hash of the current fields
      # (for validation or saving purposes)
      return name: $("#groupNameInput").val()

    cancel: ->
      if not @model.isNew()
        # Need to fetch the actual members from the server, 
        # since they've probably been changed
        @model.members.fetch()
      @close()

    delete: ->
      @model.destroy()
      events.trigger( 'closeView' )

  )
  GroupEditView
