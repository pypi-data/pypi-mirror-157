# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Snake(Component):
    """A Snake component.
Wrapped from [react-snake](https://github.com/derrmru/react-snake).

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- backgroundColor (string; default '#ebebeb'):
    background.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- color1 (string; default '#248ec2'):
    Snake's color.

- color2 (string; default '#1d355e'):
    Apple's color."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_grocery'
    _type = 'Snake'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, class_name=Component.UNDEFINED, color1=Component.UNDEFINED, color2=Component.UNDEFINED, backgroundColor=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'backgroundColor', 'class_name', 'color1', 'color2']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'backgroundColor', 'class_name', 'color1', 'color2']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Snake, self).__init__(**args)
