define [ "jQuery", "Underscore", "Backbone", "Mustache", "text!templates/groupEdit.html", "text!templates/groupMember.html" ], ($, _, Backbone, Mustache, groupEditTemplate, memberTemplate) ->
  GroupEditView = Backbone.View.extend(
    tagName: "div"
    id: "groupEdit"
    template: groupEditTemplate
    initialize: ->
      @model.bind "change", @render, this
      @model.bind "destroy", @render, this
      @model.members.bind "change", @renderMembers, this
      @model.members.bind "destroy", @renderMembers, this
      @model.members.bind "reset", @renderMembers, this
      if @model.id
        @model.fetch()
        @model.members.fetch()
      # Maybe replace this append with templated stuff sometime?
      @$el.append(
        "<h2>Edit Group</h2>
        <dl id='groupEditDl'></dl>
        Members:
        <ul id='memberList'></ul>"
      )
      @render

    render: ->
      $("#groupEditDl").html Mustache.render(@template, @model.toJSON())
      @delegateEvents "click button": "submit"

    renderMembers: ->
      $("#memberList").html Mustache.render( memberTemplate,
        members : @model.members.toJSON()
      )

    onClose: ->
      @model.unbind "change", @render, this
      @model.unbind "destroy", @render, this
      @model.members.unbind "change", @render, this
      @model.members.unbind "destroy", @render, this
      @model.members.unbind "reset", @renderMembers, this

    submit: ->
      @model.save name: $("#groupNameInput").val()
      #TODO: Figure out if the members.save is needed
      @model.members.save()
  )
  GroupEditView
