define [ "jQuery", "Underscore", "Backbone" ], ($, _, Backbone) ->
  GroupMember = Backbone.Model.extend(
    initialize: ->
  )
  GroupMemberList = Backbone.Collection.extend(
    model: GroupMember
    parse: (data, xhr) ->
      data.members
  )
  Group = Backbone.Model.extend(
    urlRoot: "api/groups"
    initialize: ->
      @members = new GroupMemberList
      @members.url = "/api/groups/" + @id + "/members"

    validate: (attrs) ->
  )
  Group
