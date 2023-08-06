# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Masonry(Component):
    """A Masonry component.
Wrapped from [react-masonry-component](https://github.com/eiriklv/react-masonry-component).

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    children.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- disableImagesLoaded (boolean; optional):
    default False.

- elementType (string; optional):
    default 'div'.

- enableResizableChildren (boolean; optional):
    enableResizableChildren.

- imagesLoadedOptions (dict; optional):
    default {}.

- options (dict; optional):
    masonry options.

    `options` is a dict with keys:

    - columnWidth (number | string; optional):
        Aligns items to a horizontal grid.

    - containerStyle (dict; optional):
        CSS styles that are applied to the container element.

    - fitWidth (boolean; optional):
        Sets the width of the container to fit the available number of
        columns, based the size of container's parent element. When
        enabled, you can center the container with CSS.

    - gutter (number; optional):
        Adds horizontal space between item elements.

    - horizontalOrder (boolean; optional):
        Lays out items to (mostly) maintain horizontal left-to-right
        order.

    - initLayout (boolean; optional):
        Enables layout on initialization. Enabled by default
        initLayout: True.

    - itemSelector (string; optional):
        Specifies which child elements will be used as item elements
        in the layout.

    - originLeft (boolean; optional):
        Controls the horizontal flow of the layout. By default, item
        elements start positioning at the left, with originLeft: True.
        Set originLeft: False for right-to-left layouts.

    - originTop (boolean; optional):
        Controls the vertical flow of the layout. By default, item
        elements start positioning at the top, with originTop: True.
        Set originTop: False for bottom-up layouts.

    - percentPosition (boolean; optional):
        Sets item positions in percent values, rather than pixel
        values. percentPosition: True works well with percent-width
        items, as items will not transition their position on resize.

    - resize (boolean; optional):
        Adjusts sizes and positions when window is resized. Enabled by
        default resize: True.

    - stagger (number | string; optional):
        Staggers item transitions, so items transition incrementally
        after one another. Set as a CSS time format, '0.03s', or as a
        number in milliseconds, 30.

    - stamp (string; optional):
        Specifies which elements are stamped within the layout.
        Masonry will layout items below stamped elements.

    - transitionDuration (number | string; optional):
        Duration of the transition when items change position or
        appearance, set in a CSS time format. Default:
        transitionDuration: '0.4s'.

- style (dict; optional):
    style.

- updateOnEachImageLoad (boolean; optional):
    default False and works only if disableImagesLoaded is False."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_grocery'
    _type = 'Masonry'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, class_name=Component.UNDEFINED, elementType=Component.UNDEFINED, options=Component.UNDEFINED, disableImagesLoaded=Component.UNDEFINED, updateOnEachImageLoad=Component.UNDEFINED, imagesLoadedOptions=Component.UNDEFINED, onImagesLoaded=Component.UNDEFINED, enableResizableChildren=Component.UNDEFINED, onLayoutComplete=Component.UNDEFINED, onRemoveComplete=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'class_name', 'disableImagesLoaded', 'elementType', 'enableResizableChildren', 'imagesLoadedOptions', 'options', 'style', 'updateOnEachImageLoad']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'class_name', 'disableImagesLoaded', 'elementType', 'enableResizableChildren', 'imagesLoadedOptions', 'options', 'style', 'updateOnEachImageLoad']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Masonry, self).__init__(children=children, **args)
