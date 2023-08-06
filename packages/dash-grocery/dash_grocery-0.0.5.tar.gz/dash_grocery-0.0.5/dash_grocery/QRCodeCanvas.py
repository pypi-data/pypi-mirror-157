# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class QRCodeCanvas(Component):
    """A QRCodeCanvas component.
Wrapped from [qrcode.react](https://github.com/zpao/qrcode.react).

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- bgColor (string; optional):
    Background color. \"#FFFFFF\".

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- fgColor (string; optional):
    Foreground color. \"#000000\".

- imageSettings (dict; optional):
    Settings for pictures inserted in the QR code.

    `imageSettings` is a dict with keys:

    - excavate (boolean; optional):
        excavate.

    - height (number; optional):
        height of the img.

    - src (string; optional):
        The src of the image tag.

    - width (number; optional):
        width of the img.

    - x (number; optional):
        none, will center.

    - y (number; optional):
        none, will center.

- includeMargin (boolean; optional):
    Whether to include margins.

- level (string; optional):
    ('L' 'M' 'Q' 'H').

- size (number; optional):
    size.

- value (string; optional):
    The value of the QR code."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_grocery'
    _type = 'QRCodeCanvas'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, class_name=Component.UNDEFINED, value=Component.UNDEFINED, size=Component.UNDEFINED, bgColor=Component.UNDEFINED, fgColor=Component.UNDEFINED, level=Component.UNDEFINED, includeMargin=Component.UNDEFINED, imageSettings=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'bgColor', 'class_name', 'fgColor', 'imageSettings', 'includeMargin', 'level', 'size', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'bgColor', 'class_name', 'fgColor', 'imageSettings', 'includeMargin', 'level', 'size', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(QRCodeCanvas, self).__init__(**args)
