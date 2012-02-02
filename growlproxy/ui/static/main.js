// Filename: main.js

require.config({
  baseUrl: '/static/',
  paths: {
    jQuery: 'libs/jquery/jquery-wrapper',
    Underscore: 'libs/underscore/underscore-wrapper',
    Backbone: 'libs/backbone/backbone-wrapper',
    Mustache: 'libs/mustache/mustache-wrapper'
  }
});

require([

  // Load our app module and pass it to our definition function
  'app',

  // Some plugins have to be loaded in order due to there non AMD compliance
  // Because these scripts are not "modules" they do not pass any values to the definition function below
  'order!libs/jquery/js/jquery-1.7.1',
  'order!static/libs/jquery/js/jquery-ui-1.8.16.custom.min.js',
  'order!libs/underscore/underscore',
  'order!libs/backbone/backbone',
], function(App){
  // The "app" dependency is passed in as "App"
  // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function
  App.initialize();
});