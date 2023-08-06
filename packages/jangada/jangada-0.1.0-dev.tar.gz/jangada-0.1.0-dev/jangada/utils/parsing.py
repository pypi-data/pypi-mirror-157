#  -*- coding: utf-8 -*-
"""

Author: Rafael R. L. Benevides
Date: 10/03/2021

"""


def get_class_complete_name(cls):
    """
    Returns complete name of a class.

    :param cls: Class
    :type cls: `type <https://docs.python.org/3/library/functions.html#type>`_

    :return: Complete class name
    :rtype: `str <https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str>`_
    """

    module = cls.__module__

    if module is None or module == 'builtins':
        return cls.__name__

    return "{module}.{cls_name}".format(module=module, cls_name=cls.__name__)


def get_obj_type_complete_name(obj):
    """
    Returns the complete name of an object type.

    :param obj: Python object
    :type obj: `object <https://docs.python.org/3/library/functions.html#object>`_

    :return: Complete name of object type
    :rtype: `str <https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str>`_
    """
    return get_class_complete_name(type(obj))


def parse_types(obj, types, is_none_acceptable=False):
    """
    Test if ``obj`` is an instance of one of given ``types``.

    :param obj: Object whose type must be tested.
    :type obj: object

    :param types: Expected types for ``obj``.
    :type types: type of list of types

    :param is_none_acceptable: Set this if ``None`` is an acceptable value for ``obj``. If set ``True`` and ``obj=None``,
        ``None`` is returned. Else, a TypeError is raised.
    :type is_none_acceptable: bool

    :return: Parsed object
    :rtype: object or None
    """

    if obj is None:

        if is_none_acceptable:
            return

        error = "Expected instance of one of the following classes: {}. Given None"
        raise TypeError(error)

    if isinstance(obj, types):
        return obj

    if isinstance(types, (tuple, list)):
        error = "Expected instance of one of the following classes: {}. Given instance of {} instead."
        cls = [get_class_complete_name(_cls) for _cls in types]

    else:
        error = "Expected instance of {}. Given instance of {} instead."
        cls = get_class_complete_name(types)

    raise TypeError(error.format(cls, get_obj_type_complete_name(obj)))


def parser(types):
    """
    Returns a type parser function.

    :param types: Expected types.
    :type types: type of list of types

    :return: A type parser function
    :rtype: callable
    """
    def __parser(obj):
        return parse_types(obj, types)

    return __parser


def pop_and_parse(kwargs, key, default_value=None, types=None, parser=None):
    """
    Removes, parses and returns the value associated to the ``key`` from ``kwargs``.

    This function is mainly designed to conveniently parse key arguments from functions and methods. If ``key`` does not
    belong to ``kwargs``, the ``default_value`` will be returned (no parse is applied to ``default_value``). The value
    is parsed if one of the arguments ``parser`` or ``types`` is set.

    :param kwargs: Dictionary, usually the key arguments from a function or method.
    :type kwargs: `dict <https://docs.python.org/3/library/stdtypes.html#mapping-types-dict>`_

    :param key: Key to be removed and whose value must be parsed.

    :param default_value: Value to be returned if ``key`` is not in ``kwargs``.

    :param types: Value expected type or types list.
    :type types: `type <https://docs.python.org/3/library/functions.html#type>`_ or list of types.

    :param parser: Function that performs the parse. It must return the parsed value.
    :type parser: callable

    :return: The parsed value or ``default_value``
    :rtype: object
    """

    if parser and types:
        error = "Only one of the following key arguments must be set: value_type or parser"
        raise ValueError(error)

    if key in kwargs:

        value = kwargs.pop(key)

        if types:
            if isinstance(value, types):
                return value

            error = "Expected instance of {types}. Given instance of {obj_type}"
            raise TypeError(error.format(types=types, obj_type=get_obj_type_complete_name(value)))

        if parser:
            if callable(parser):
                return parser(value)

            raise TypeError("Given parser is not callable")

        return value

    return default_value
