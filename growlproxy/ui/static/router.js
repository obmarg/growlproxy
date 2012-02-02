define([
  // These are path alias that we configured in our bootstrap
  'jQuery',
  'Underscore',
  'Backbone',
  'models/server',
  'views/serverEditView',
  'models/group',
  'views/groupEditView',
], function($, _, Backbone, Server, SeverEditView, Group, GroupEditView){
  
  var AppRouter = Backbone.Router.extend({
    routes: {
      'servers/:id' : "server",
      'groups/:id' : "group"
    },

    initialize: function(){
      // Init shit
      this.currentView = null;
    },

    changeView: function( newView ){
      // Change the view to a new one
      if ( this.currentView !== null ) {
        this.currentView.close();
        this.currentView = null;
      }
      $( "#mainPanel" ).html("");
      $( "#mainPanel" ).append( newView.el );
      newView.render();
      this.currentView = newView;
    },

    server: function( id ){
      // Display the edit server stuff
      view = new SeverEditView({ 'model' : new Server({ 'id' : id }) });
      this.changeView( view );
    },
    
    group: function( id ){
      view = new GroupEditView({ model : new Group({ 'id' : id }) });
      this.changeView( view );
    }
  });
  
  var initialize = function(){
    var app_router = new AppRouter;
    Backbone.history.start();
  };
  
  return {
    initialize: initialize
  };
  // What we return here will be used by other modules
});