define([
  'jQuery',
  'Underscore',
  'Backbone',
], function($, _, Backbone){
  
  var GroupMember = Backbone.Model.extend({
    initialize : function(){
      // TODO: Do something if i need to
    }
  });
  
  var GroupMemberList = Backbone.Collection.extend({
    model: GroupMember,
    parse: function(data,xhr){
      return data.members;
    }
  });
  
  var Group = Backbone.Model.extend({
    urlRoot: 'api/groups',
    initialize : function(){
      this.members = new GroupMemberList;
      //TODO: might need to reset the url if this is a new group
      //      and doesn't have an id just yet
      this.members.url = '/groups/' + this.id + '/members'
    },
    
    validate : function( attrs ){
        //TODO: Check valid name, and valid members
    },
  });
  
  return Group;
});