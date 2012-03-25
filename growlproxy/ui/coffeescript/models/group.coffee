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
      # TODO: Need to do something about this: New groups won't have an id to use here
      if @isNew()
      	@bind "sync", @newSync, this
      else
        @members.url = "api/groups/" + @id + "/members"

    newSync: ->
      # This function should only be called after the first save of the model
      @members.url = "api/groups/" + @id + "/members"
      @unbind "sync", @newSync, this
      @members.save()

    addMember: (attrs) ->
      member = new GroupMember( attrs )
      member.urlRoot = @members.url
      @members.add( member )

    validate: (attrs) ->
  )
  Group
