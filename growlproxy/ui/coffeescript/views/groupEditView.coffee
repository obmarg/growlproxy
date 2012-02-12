define [ "jQuery", "Underscore", "Backbone", "Mustache", "events", "collections/serverList", "text!templates/groupEdit.html", "text!templates/groupMember.html" ], ($, _, Backbone, Mustache, events, servers, groupEditTemplate, memberTemplate) ->
  GroupEditView = Backbone.View.extend(
    tagName: "div"
    id: "groupEdit"
    template: groupEditTemplate

    initialize: ->
      events.on "AddGroupMember", @addGroupMember, this
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.members.bind "add", @renderMembers, this
      @model.members.bind "change", @renderMembers, this
      @model.members.bind "destroy", @renderMembers, this
      @model.members.bind "reset", @renderMembers, this
      if @model.id
        @model.fetch()
        @model.members.fetch()
      # Maybe replace this append with templated stuff sometime?
      @$el.append(
        "<h2 class='ui-state-default ui-state-active ui-corner-all'>Edit Group</h2>
        <dl id='groupEditDl'></dl>
        Members:
        <ul id='memberList'></ul>
        <select id='addMemberList'>
        </select>
        <div class='formButtons'>
          <button class='submitGroup'>Submit</button>
        </div>
        "
      )
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
      $("#groupEditDl").html Mustache.render(@template, @model.toJSON())
      @delegateEvents "click button": "submit"
      $(".submitGroup").button()
      $("input[type=text]").button()
      $("#addMemberList").append(
        "<option>Add Member</option>"
      )
      servers.forEach( ( element ) ->
        $("#addMemberList").append(
          $("<option>", value: element.attributes.id ).text(
            element.attributes.name
          )
        )
      )
      $("#addMemberList").selectbox(
        height: 1.6
        change: -> 
          selected = $("#addMemberList").val()
          if selected != "Add Member"
            events.trigger( "AddGroupMember", selected )
        )
      #$("#addMemberList").bind(
      #  "selectboxclose",
      #  -> alert( "BLAH" )
      #)

    renderMembers: ->
      $("#memberList").html Mustache.render( memberTemplate,
        members : @model.members.toJSON()
      )
      $("#memberList").sortable(
        update: @onMemberListUpdate
        )

    addGroupMember: ( serverId ) ->
      # TODO: Add priority and shit to this
      @model.addMember(
        serverId: serverId
        name: servers.get( serverId ).attributes.name
      )

    submit: ->
      @model.save name: $("#groupNameInput").val()
      #TODO: Figure out if the members.save is needed
      #      or done elsewhere.  If it's done elsewhere
      #      consider stopping that
      @model.members.save()
  )
  GroupEditView
