from typing import Any


def is_primitive(attribute) -> bool:
    return not hasattr(attribute, '__dict__')


def include_attribute(attribute_name: str, include_private: bool) -> bool:
    return include_private or not attribute_name.startswith('_')


def _short_details(obj: Any) -> str:
    """Return class name + first attribute and its value."""
    items = tuple(vars(obj).items())
    class_name = obj.__class__.__name__
    if len(items) == 0:
        return class_name
    else:
        return f"{class_name}({items[0][0]}={items[0][1]})"


# pylint: disable=too-many-branches, disable=too-few-public-methods
def _full_details(obj, include_private: bool = False, indent: int = 0, key_name: str = '') -> str:
    """Provides a readable representation of __dict__ based Python object.

    Parameters
    ----------
    obj : Any
        The object for printing.
    include_private : bool
        Include private attributes in the string.
    indent : int
        Indent of the current function call.
    key_name : str
        Attribute name

    Returns
    -------
    str
        String with full details of the object.
    """
    class_name = obj.__class__.__name__
    to_print = ''
    first_time = True
    for key, value in vars(obj).items():
        if isinstance(value, list) and (len(value) == 0 or not is_primitive(value[0])):
            for index, inner_obj in enumerate(value):
                if index == 0:
                    if include_attribute(key, include_private):
                        to_print += _full_details(inner_obj, include_private, indent + len(class_name) + 1, key)
                else:
                    if include_attribute(key, include_private):
                        to_print += _full_details(inner_obj, include_private,
                                                  indent + len(class_name) + 1 + len(key) + 1, '')
        elif not is_primitive(value):
            if include_attribute(key, include_private):
                to_print += _full_details(value, include_private, indent + len(class_name) + 1, key)
        else:
            prefix = ''
            if first_time is False:
                if len(key_name) > 0:
                    prefix = (len(class_name) + 1 + indent + len(key_name) + 1) * ' '
                else:
                    prefix = (len(class_name) + 1 + indent) * ' '
            if include_attribute(key, include_private):
                to_print += (prefix + f"{key}={value!r}" + '\n')
        first_time = False
    if first_time is True or key_name == '':
        if to_print[-1] == '\n':
            to_print = to_print[:-1]  # remove last '\n'
        return f"{indent * ' '}{class_name}({to_print})\n"
    else:
        to_print = to_print[:-1]  # remove last '\n'
        return f"{indent * ' '}{key_name}={class_name}({to_print})\n"


class ObjectRepr:
    """
    Provide dynamic __repr__ method for any __dict__ based class.
    Order of the printed items is defined by vars(self) dict.
    For default not include private attributes (start with '_').
    """

    def __repr__(self) -> str:
        return _full_details(obj=self)

    def __format__(self, format_spec) -> str:
        if format_spec == 'include_privates':
            return _full_details(obj=self, include_private=True)
        else:
            return _full_details(obj=self)

    def __str__(self) -> str:
        return _short_details(obj=self)
