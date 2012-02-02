define([
  'jQuery',
  'Underscore',
  'Backbone',
  'Mustache',
  'text!templates/groupEdit.html'
], function($, _, Backbone,Mustache,Template){
  
  var GroupEditView = Backbone.View.extend({
    tagName: 'dl',
    id: 'groupEdit',
    
    template: Template,

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
      this.delegateEvents({
        'click button' : 'submit'
      });
    },

    onClose: function(){
      this.model.unbind( 'change', this.render, this );
      this.model.unbind( 'destroy', this.render, this );
    },
    
    submit: function(){
      this.model.save({
        name : $('#groupNameInput').val(),
      });
    }
  });
  
  return GroupEditView;
});