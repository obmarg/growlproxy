define([
  'jQuery',
  'Underscore',
  'Backbone',
  'Mustache',
  'text!templates/serverEdit.html'
], function($, _, Backbone,Mustache,Template){
  
  //TODO: Think there's a chance this'll be called before
  //      the page is loaded.  Fix that problem somehow
  var ServerEditView = Backbone.View.extend({
    template: Template,

    events : {},

    initialize: function(){
      this.model.bind( 'change', this.render, this );
      this.model.bind( 'destroy', this.render, this );
      
      if( this.model.id ) {
        this.model.fetch();
      }
    },

    render: function(){
      //TODO: Make sure that this isn't called too much
      $( this.el ).html( 
          Mustache.render( this.template, this.model.toJSON() ) 
      );
    },

    onClose: function(){
      this.model.unbind( 'change', this.render, this );
      this.model.unbind( 'destroy', this.render, this );
    },
  });
  
  return ServerEditView;
});