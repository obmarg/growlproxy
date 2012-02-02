define([
  // These are path alias that we configured in our bootstrap
  'jQuery',
  'Underscore',
  'Backbone',
  'models/server',
  'views/serverEditView',
], function($, _, Backbone, Server, SeverEditView){
  
  var AppRouter = Backbone.Router.extend({
    routes: {
      'servers/:id' : "server"
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