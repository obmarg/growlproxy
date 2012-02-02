define([
  'jQuery',
  'Underscore',
  'Backbone',
], function($, _, Backbone){
  var Server = Backbone.Model.extend({
    urlRoot: 'api/servers',
    validate : function(attrs){
        //TODO: validate the server.
        //       Return error string on fail
    }
  });
  
  return Server;
});

