# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ResponsiveGridLayout(Component):
    """A ResponsiveGridLayout component.
Wrapped from [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout).

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    children.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- allowOverlap (boolean; optional):
    If True, grid can be placed one over the other. If set, implies
    `preventCollision`.

- autoSize (boolean; optional):
    If True, the container height swells and contracts to fit
    contents.

- breakpoints (dict; optional):
    {name: pxVal}, e.g. {lg: 1200, md: 996, sm: 768, xs: 480}
    Breakpoint names are arbitrary but must match in the cols and
    layouts objects.

- class_name (string; optional):
    Often used with CSS to style elements with common properties.

- cols (dict; optional):
    # of cols. This is a breakpoint -> cols map, e.g. {lg: 12, md: 10,
    ...}.

- compactType (a value equal to: 'vertical', 'horizontal'; optional):
    Compaction type.

- containerPadding (optional):
    containerPadding (in pixels). Can be specified either as
    horizontal and vertical padding, e.g. `[10, 10]` or as a
    breakpoint -> containerPadding map, e.g. `{lg: [10, 10], md: [10,
    10], ...}.

- draggableCancel (string; optional):
    A CSS selector for tags that will not be draggable. For example:
    draggableCancel:'.MyNonDraggableAreaClassName' If you forget the
    leading . it will not work. .react-resizable-handle\" is always
    prepended to this value.

- draggableHandle (string; optional):
    A CSS selector for tags that will act as the draggable handle. For
    example: draggableHandle:'.MyDragHandleClassName' If you forget
    the leading . it will not work.

- droppingItem (dict; optional):
    Configuration of a dropping element. Dropping element is a
    \"virtual\" element which appears when you drag over some element
    from outside. It can be changed by passing specific parameters: i
    - id of an element w - width of an element h - height of an
    element.

    `droppingItem` is a dict with keys:

    - h (number; optional)

    - i (string; optional)

    - w (number; optional)

- isBounded (boolean; optional):
    Flag.

- isDraggable (boolean; optional):
    Flag.

- isDroppable (boolean; optional):
    If True, droppable elements (with `draggable={True}` attribute)
    can be dropped on the grid. It triggers \"onDrop\" callback with
    position and event object as parameters. It can be useful for
    dropping an element in a specific position.

- isResizable (boolean; optional):
    Flag.

- layout (list; optional):
    // Layout is an array of object with the format: {x: number, y:
    number, w: number, h: number} The index into the layout must match
    the key used on each item component. If you choose to use custom
    keys, you can specify that key in the layout array objects like
    so: {i: string, x: number, y: number, w: number, h: number}.

- layouts (dict; optional):
    layouts is an object mapping breakpoints to layouts. e.g. {lg:
    Layout, md: Layout, ...}.

- margin (optional):
    margin (in pixels). Can be specified either as horizontal and
    vertical margin, e.g. `[10, 10]` or as a breakpoint -> margin map,
    e.g. `{lg: [10, 10], md: [10, 10], ...}.

- preventCollision (boolean; optional):
    If True, grid items won't change position when being dragged over.
    If `allowOverlap` is still False, this simply won't allow one to
    drop on an existing object.

- resizeHandle (dash component; optional):
    Custom component for resize handles See `handle` as used in
    https://github.com/react-grid-layout/react-resizable#resize-handle
    Your component should have the class `.react-resizable-handle`, or
    you should add your custom class to the `draggableCancel` prop.

- resizeHandles (list; optional):
    Defines which resize handles should be rendered Allows for any
    combination of: 's' - South handle (bottom-center) 'w' - West
    handle (left-center) 'e' - East handle (right-center) 'n' - North
    handle (top-center) 'sw' - Southwest handle (bottom-left) 'nw' -
    Northwest handle (top-left) 'se' - Southeast handle (bottom-right)
    'ne' - Northeast handle (top-right).

- rowHeight (number; optional):
    Rows have a static height, but you can change this based on
    breakpoints if you like.

- transformScale (number; optional):
    If parent DOM node of ResponsiveReactGridLayout or ReactGridLayout
    has \"transform: scale(n)\" css property, we should set scale
    coefficient to avoid render artefacts while dragging.

- useCSSTransforms (boolean; optional):
    Uses CSS3 translate() instead of position top/left. This makes
    about 6x faster paint performance.

- width (number; optional):
    This allows setting the initial width on the server side. This is
    required unless using the HOC <WidthProvider> or similar."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, class_name=Component.UNDEFINED, width=Component.UNDEFINED, autoSize=Component.UNDEFINED, breakpoints=Component.UNDEFINED, cols=Component.UNDEFINED, draggableCancel=Component.UNDEFINED, draggableHandle=Component.UNDEFINED, compactType=Component.UNDEFINED, layout=Component.UNDEFINED, layouts=Component.UNDEFINED, margin=Component.UNDEFINED, containerPadding=Component.UNDEFINED, rowHeight=Component.UNDEFINED, droppingItem=Component.UNDEFINED, isDraggable=Component.UNDEFINED, isResizable=Component.UNDEFINED, isBounded=Component.UNDEFINED, useCSSTransforms=Component.UNDEFINED, transformScale=Component.UNDEFINED, allowOverlap=Component.UNDEFINED, preventCollision=Component.UNDEFINED, isDroppable=Component.UNDEFINED, resizeHandles=Component.UNDEFINED, resizeHandle=Component.UNDEFINED, onLayoutChange=Component.UNDEFINED, onDrop=Component.UNDEFINED, onDropDragOver=Component.UNDEFINED, onBreakpointChange=Component.UNDEFINED, onWidthChange=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'allowOverlap', 'autoSize', 'breakpoints', 'class_name', 'cols', 'compactType', 'containerPadding', 'draggableCancel', 'draggableHandle', 'droppingItem', 'isBounded', 'isDraggable', 'isDroppable', 'isResizable', 'layout', 'layouts', 'margin', 'preventCollision', 'resizeHandle', 'resizeHandles', 'rowHeight', 'transformScale', 'useCSSTransforms', 'width']
        self._type = 'ResponsiveGridLayout'
        self._namespace = 'dash_grocery'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'allowOverlap', 'autoSize', 'breakpoints', 'class_name', 'cols', 'compactType', 'containerPadding', 'draggableCancel', 'draggableHandle', 'droppingItem', 'isBounded', 'isDraggable', 'isDroppable', 'isResizable', 'layout', 'layouts', 'margin', 'preventCollision', 'resizeHandle', 'resizeHandles', 'rowHeight', 'transformScale', 'useCSSTransforms', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ResponsiveGridLayout, self).__init__(children=children, **args)
