define [ "jQuery", "Underscore", "Backbone", "models/rule" ], ($, _, Backbone, Rule) ->
  RuleList = Backbone.Collection.extend(
    model: Rule
    url: "api/rules"
    parse: (data, xhr) ->
      data.rule
  )
  rl = new RuleList
  # TODO: bootstrap the rule list
  # gl.reset( $.parseJSON( groupBootstrap ) )
  return rl
