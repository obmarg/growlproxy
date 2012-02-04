define [ "jQuery", "Underscore", "Backbone", "models/group" ], ($, _, Backbone, Group) ->
  GroupList = Backbone.Collection.extend(
    model: Group
    url: "api/groups"
    parse: (data, xhr) ->
      data.groups
  )
  gl = new GroupList
  gl.reset( $.parseJSON( groupBootstrap ) )
  return gl
