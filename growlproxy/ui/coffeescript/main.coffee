require.config
  baseUrl: "/static/"
  paths:
    jQuery: "libs/jquery/jquery-wrapper"
    Underscore: "libs/underscore/underscore-wrapper"
    Backbone: "libs/backbone/backbone-wrapper"
    Mustache: "libs/mustache/mustache-wrapper"

require [ 
  "app",
  "order!libs/jquery/js/jquery-1.7.1",
  "order!libs/jquery/js/bootstrap/bootstrap.min"
  "order!libs/underscore/underscore",
  "order!libs/backbone/backbone"
], (App) ->
  App.initialize()
