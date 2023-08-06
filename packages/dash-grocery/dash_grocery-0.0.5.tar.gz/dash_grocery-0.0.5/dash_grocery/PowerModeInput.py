# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PowerModeInput(Component):
    """A PowerModeInput component.
Wrapped from [power-mode-input](https://github.com/lindelof/power-mode-input).

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- config (dict; default {    height: 5,    tha: [0, 360],    g: 0.5,    num: 5,    radius: 6,    circle: True,    alpha: [0.75, 0.1],    color: 'random',}):
    You can use type=\"custom\" to achieve a higher degree of freedom
    for the particle background.

    `config` is a dict with keys:

    - alpha (number | list; optional)

    - circle (boolean; optional)

    - color (string | list of strings; optional)

    - g (number; optional)

    - height (number; optional)

    - num (number | list; optional)

    - radius (number | list; optional)

    - tha (number | list; optional)

- defaultValue (boolean | number | string | dict | list; optional):
    Default value of the input tag.

- maxLength (number; default 128):
    The length limit of the input.

- placeholder (string; optional):
    Placeholder of the input tag.

- style (dict; optional):
    Style of the input tag.

- type (string; default 'text'):
    Type of the input tag.

- value (boolean | number | string | dict | list; optional):
    Value of the input tag."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_grocery'
    _type = 'PowerModeInput'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, class_name=Component.UNDEFINED, type=Component.UNDEFINED, placeholder=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, maxLength=Component.UNDEFINED, style=Component.UNDEFINED, config=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'class_name', 'config', 'defaultValue', 'maxLength', 'placeholder', 'style', 'type', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'class_name', 'config', 'defaultValue', 'maxLength', 'placeholder', 'style', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(PowerModeInput, self).__init__(**args)
