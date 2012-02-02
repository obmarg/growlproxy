define([
  'jQuery',
  'Underscore',
  'Backbone',
], function($, _, Backbone){
  
  var Group = Backbone.Model.extend({
    validate : function( attrs ){
        //TODO: Check valid name, and valid members
        },
  });
  
  return Group;
});