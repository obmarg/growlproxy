$(function(){

    // Define prototype of view close function
    Backbone.View.prototype.close = function(){
        this.remove();
        this.unbind();
        if ( this.onClose ){
            this.onClose();
        }
    }

    //TODO: Fix fucked up vim indents.  (For good preferably)

    window.Server = Backbone.Model.extend({
        urlRoot: 'api/servers',
        validate : function(attrs){
            //TODO: validate the server.
            //       Return error string on fail
        }
    });

    window.ServerView = Backbone.View.extend({
        el: $( "#mainPanel" ),

        template: $( "#serverForm" ).html(),

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

    window.ServerList = Backbone.Collection.extend({
        model : Server,
        url : '/api/servers',
        parse: function(models,xhr){
            return models.servers;
        }
    });

    window.Servers = new ServerList;

    window.ServerListView = Backbone.View.extend({
        el: $("#serverList"),

        template: "{{#servers}}<li><a href='#/servers/{{id}}'>{{name}}</a></li>{{/servers}}",

        model : Servers,

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
                     //el.jstree({ 'plugins' : [ 'themes', 'html_data' ] });
                     return this;
                 },

    });

    //      Then write basic JSON server side code
    //      Then create app to manage all this shite
    //      Then integrate into index.
    //      Then test (probably including writing unit tests somewhere)


    window.ServerGroup = Backbone.Model.extend({
        validate : function( attrs ){
            //TODO: Check valid name, and valid members
            },
    });

    window.ServerGroupList = Backbone.Collection.extend({
        model : ServerGroup,
        url : 'api/groups'
    });

    window.ServerGroupView = Backbone.Collection.extend({
        tagName : 'li',
        template : "<li>ServerGroup</li>",
        model : ServerGroupList,
        events: {},

        initialize : function(){
            //TODO: DO something
            this.model.bind( 'change', this.render, this );
            this.model.bind( 'destroy', this.render, this );
        },

        render : function(){
            //Do something
            return this;
        }
    });

    window.AppView = Backbone.View.extend({
        el: $("#ProxyApp"),

        initialize: function(){
            window.serverList = new ServerListView;
            //TODO: Pre-load this stuff, and remove the initial fetch
            Servers.fetch({
                success: function(coll, response){
                    window.serverList.render();
                }
            });
        }
    });

    window.App = new AppView;

    window.RouterDef = Backbone.Router.extend({
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
            this.currentView = newView;
            newView.render();
        },

        server: function( id ){
            // Display the edit server stuff
            view = new ServerView({ 'model' : new Server({ 'id' : id }) });
            this.changeView( view );
        }
    });
    
    window.Router = new RouterDef;
    Backbone.history.start();
});
