define([
  'jQuery',
  'Underscore',
  'Backbone',
  'router', // Request router.js
  'models/serverList',
  'views/serverListView',
  'models/groupList',
  'views/groupListView',
], function( 
    $,
    _,
    Backbone,
    Router,
    ServerList,
    ServerListView,
    GroupList,
    GroupListView
    ){
  
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
      
      var groups = new GroupList;
      
      var groupList = new GroupListView({ model : groups });
      
      groups.fetch({
        success: function(coll, response){
            groupList.render();
        }
      });
    }
  
    return {
      initialize: initialize
    };
});