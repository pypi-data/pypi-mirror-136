# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SelectFilter(Component):
    """A SelectFilter component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- classes (dict; optional):
    The classes displayed in the component.

- endDate (boolean | number | string | dict | list; optional):
    The endDate displayed in the input.

- label (string; optional):
    A label that will be printed when this component is rendered.

- startDate (boolean | number | string | dict | list; optional):
    The startDate displayed in the input.

- type (boolean | number | string | dict | list; optional):
    The type of dateformat in the input.

- value (boolean | number | string | dict | list; optional):
    The value displayed in the input."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.UNDEFINED, value=Component.UNDEFINED, startDate=Component.UNDEFINED, type=Component.UNDEFINED, endDate=Component.UNDEFINED, classes=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'classes', 'endDate', 'label', 'startDate', 'type', 'value']
        self._type = 'SelectFilter'
        self._namespace = 'select_filter'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'classes', 'endDate', 'label', 'startDate', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(SelectFilter, self).__init__(**args)
