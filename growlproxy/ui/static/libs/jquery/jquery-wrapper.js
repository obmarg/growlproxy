define([
// Load the original jQuery source file
  'order!libs/jquery/js/jquery-1.7.1',
  'order!libs/jquery/js/bootstrap/bootstrap.min',
  // Don't know why I'm needed to specify static here
  // Bit fucking crap isn't it....
  // TODO: find out why
], function(){
  // Tell Require.js that this module returns a reference to jQuery
  return $;
});
