define([
  'jQuery',
  'Underscore',
  'Backbone',
  'Mustache',
  'text!templates/groupList.html'
], function($, _, Backbone,Mustache,Template){

  var GroupListView = Backbone.View.extend({
    el: $("#groupList"),

    template: Template,

    events : {},

    initialize : function() {
      this.model.bind( 'change', this.render, this );
      this.model.bind( 'destroy', this.render, this );
    },

    render : function() {
      js = this.model.toJSON();
      el = $( this.el );
      el.html(
          Mustache.render( this.template, { 'groups' : js } )
      );
      return this;
    },

  });
  
  return GroupListView;
});