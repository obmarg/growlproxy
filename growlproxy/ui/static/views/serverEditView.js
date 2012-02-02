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
    el: $( "#mainPanel" ),

    template: Template,

    events : {},

    initialize: function(){
      if( this.model.id ) {
        this.model.fetch();
      }
      this.model.bind( 'change', this.render, this );
      this.model.bind( 'destroy', this.render, this );
    },

    render: function(){
      //TODO: Make sure that this isn't called too much
      $( this.el ).html( Mustache.render( this.template, this.model ) );
    },

    onClose: function(){
      this.model.unbind( 'change', this.render, this );
      this.model.unbind( 'destroy', this.render, this );
    },
  });
  
  return ServerEditView;
});