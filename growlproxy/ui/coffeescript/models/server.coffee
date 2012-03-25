define [ "jQuery", "Underscore", "Backbone" ], ($, _, Backbone) ->
  Server = Backbone.Model.extend(
    urlRoot: "api/servers"
    validate: (attrs) ->
      errs = []
      if attrs[ 'name' ]?.length < 1
      	errs.push( [ 'name', 'Name must not be empty' ] )
      if attrs[ 'remoteHost' ]?.length < 1
      	errs.push( [ 'remoteHost', 'Remote host must not be empty' ] )
      if errs.length > 0
      	return errs
      return
  )
  Server
