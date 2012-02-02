define([
  'jQuery',
  'Underscore',
  'Backbone',
  'Mustache',
  'text!templates/serverList.html'
], function($, _, Backbone,Mustache,Template){

  var ServerListView = Backbone.View.extend({
    el: $("#serverList"),

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
          Mustache.render( this.template, { 'servers' : js } )
      );
      return this;
    },

  });
  
  return ServerListView;
});