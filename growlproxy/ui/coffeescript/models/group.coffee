define [ "jQuery", "Underscore", "Backbone" ], ($, _, Backbone) ->
  GroupMember = Backbone.Model.extend(
    initialize: ->
  )
  GroupMemberList = Backbone.Collection.extend(
    model: GroupMember
    parse: (data, xhr) ->
      data.members
    save: ->
      @forEach ( item ) ->
        item.save()
        item.new = false
  )
  Group = Backbone.Model.extend(
    urlRoot: "api/groups"
    initialize: ->
      @members = new GroupMemberList
      @members.url = "/api/groups/" + @id + "/members"

    addMember: (attrs) ->
      member = new GroupMember( attrs )
      @members.add( member )

    validate: (attrs) ->
  )
  Group
