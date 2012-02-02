define([
  'jQuery',
  'Underscore',
  'Backbone',
  'models/group'
], function($, _, Backbone, Group){
  var GroupList = Backbone.Collection.extend({
    model : Group,
    url : 'api/groups',
    parse: function(data,xhr){
      return data.groups;
    }
  });
  
  return GroupList;
});