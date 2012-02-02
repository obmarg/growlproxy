define([
  'jQuery',
  'Underscore',
  'Backbone',
  'models/server'
], function($, _, Backbone,Server){
  
  var ServerList = Backbone.Collection.extend({
    model : Server,
    url : '/api/servers',
    parse: function(models,xhr){
        return models.servers;
    }
  });
  
  return ServerList;
});    
