define([
  'jQuery',
  'Underscore',
  'Backbone',
  'router', // Request router.js
  'models/serverList',
  'views/serverListView'
], function( $, _, Backbone, Router, ServerList, ServerListView ){
  var initialize = function(){
    // Pass in our Router module and call it's initialize function
    Router.initialize();
    
    var servers = new ServerList;
    
    var serverList = new ServerListView({ model : servers });
    
    //TODO: Bootstrap this stuff, and remove the initial fetch
    servers.fetch({
        success: function(coll, response){
            serverList.render();
        }
    });
  }

  return {
    initialize: initialize
  };
});