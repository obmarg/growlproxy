define [ "jQuery", "Underscore", "Backbone", "Mustache", "events", "collections/serverList", "text!templates/groupEdit.html", "text!templates/groupMember.html" ], ($, _, Backbone, Mustache, events, servers, groupEditTemplate, memberTemplate) ->
  GroupEditView = Backbone.View.extend(
    tagName: "div"
    id: "groupEdit"
    template: groupEditTemplate

    events:
      "click #submitButton": "submit"
      "click .deleteButton": "onDeleteMember"
      "click .addMemberLink": "onAddMember"

    initialize: ->
      events.on "AddGroupMember", @addGroupMember, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.members.bind "add", @renderMembers, this
      @model.members.bind "change", @renderMembers, this
      @model.members.bind "destroy", @renderMembers, this
      @model.members.bind "reset", @renderMembers, this

      @removedMembers = []

      if @model.id
        @model.fetch()
        @model.members.fetch()

      @$el.html Mustache.render(@template, @model.toJSON())
      #$("#addMemberList").change( ->
      #  selected = $(this).val()
      #  if selected != "Add Member"
      #    events.trigger( "AddGroupMember", selected )
      #)
      @render

    onClose: ->
      events.off "AddGroupMember", @addGroupMember, this
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this
      @model.members.unbind "add", @renderMembers, this
      @model.members.unbind "change", @renderMembers, this
      @model.members.unbind "destroy", @renderMembers, this
      @model.members.unbind "reset", @renderMembers, this

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
      @delegateEvents

    renderMembers: ->
      $("#memberList").html Mustache.render( memberTemplate,
        members : @model.members.toJSON()
      )
      #TODO: Re-implement this sortable shit
      #$("#memberList").sortable(
      #  update: @onMemberListUpdate
      #  )

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
      deleteString = origEvent.currentTarget.id
      id = parseInt( deleteString.split( '_' )[ 1 ], 10 )
      # TODO: Probably want to fix this up a bit.
      #         Suspect it won't work on items that haven't been submitted
      #         to server (as they have no id.  just a serverId  or whatever)
      #         Also would be good to animate the removing of items from list
      toRemove = @model.members.get( id )
      @model.members.remove( toRemove )
      $( origEvent.currentTarget.parentElement ).remove()
      toRemove.urlRoot = @model.members.url
      @removedMembers.push toRemove
      # TODO: If there are no more elements remaining, add "No Members" element

    submit: ->
      # TODO: Would be good to move the burden of deleting members to the
      #       collection/model rather than here.
      item.destroy() for item in @removedMembers
      @removedMembers = []
      @model.save name: $("#groupNameInput").val()
      #TODO: Figure out if the members.save is needed
      #      or done elsewhere.  If it's done elsewhere
      #      consider stopping that
      @model.members.save()
  )
  GroupEditView
