# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Stars(Component):
    """A Stars component.
Wrapped from [react-stars](https://github.com/n49/react-stars).

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- char (string; optional):
    Which character you want to use as a star.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- color1 (string; optional):
    Color of inactive star (this supports any CSS valid value).

- color2 (string; optional):
    Color of selected or active star.

- count (number; optional):
    How many total stars you want.

- edit (boolean; optional):
    Should you be able to select rating or just see rating (for
    reusability).

- half (boolean; optional):
    Should component use half stars, if not the decimal part will be
    dropped otherwise normal algebra rools will apply to round to half
    stars.

- size (number | string; optional):
    Size of stars (in px).

- value (number; optional):
    Set rating value."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_grocery'
    _type = 'Stars'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, class_name=Component.UNDEFINED, value=Component.UNDEFINED, count=Component.UNDEFINED, char=Component.UNDEFINED, color1=Component.UNDEFINED, color2=Component.UNDEFINED, size=Component.UNDEFINED, edit=Component.UNDEFINED, half=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'char', 'class_name', 'color1', 'color2', 'count', 'edit', 'half', 'size', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'char', 'class_name', 'color1', 'color2', 'count', 'edit', 'half', 'size', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Stars, self).__init__(**args)
