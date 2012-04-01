define [ "jQuery", "Underscore", "Backbone", 'events' ], ($, _, Backbone, eventRouter ) ->
  # BaseEditView is a base class for edit views
  # Provides error functionality
  # Relies on subclasses to set up certain things:
  #    @model.bind( "error", @onError, this )
  #    @errors = false (in initialize)
  #    Binding change events on relevant fields to @onChange
  #    @getFields() should return fields for validation
  # Templates should also group things into control-group div's
  # With help-inline span's for error text.
  # Default text should be contained in data-text and
  # @clearErrors should be called to set up the text initially
  BaseEditView = Backbone.View.extend(

    onError: ( model, error ) ->
      @clearErrors()
      @errors = true
      @handleError( e[ 0 ], e[ 1 ] ) for e in error

    clearErrors: ->
      @errors = false
      $( '.control-group.error' ).removeClass( 'error' )
      # Set up the help text
      $( '.help-inline[data-text]' ).each( ->
        t = $( this )
        t.text( t.attr( 'data-text' ) )
      )

    handleError: ( field, message ) ->
      # Handles a single error message
      controlGroup = $( ".control-group[data-field=#{field}]" )
      controlGroup.addClass( 'error' )
      controlGroup.children( '.help-inline' ).text( message )

    onChange: ->
      # Handler for change events
      # Does validation, and displays errors if needed
      res = @model.validate( @getFields() )
      if res?
      	@onError( @model, res )
      else if @errors
      	@clearErrors()
    
    onSync: ->
      # Handler for synchronisation.
      # Adds to collection if needed, then closes
      if @addToCollection?
        @addToCollection.add @model
        @addToCollection = null
      @close()

    close: ->
      eventRouter.trigger( 'closeView' )
  )

  return BaseEditView
