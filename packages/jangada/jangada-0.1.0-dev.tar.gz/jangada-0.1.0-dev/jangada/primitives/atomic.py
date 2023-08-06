#  -*- coding: utf-8 -*-
"""

Author: Rafael R. L. Benevides
Date: 10/03/2021

"""

import copy
import string
import collections
import json
import pandas

from pathlib import Path

from abc import ABCMeta, abstractmethod

from jangada.utils import parse_types


# ========== ========== ========== ========== ========== ========== Taggable
class Taggable:
    """
    Objects with tags

    A tag is a mnemonic string used to identify an object and to interact with it. In a simplified way,
    it works like a key in a dictionary, but in a more specialised context where the mapped objects are
    "aware" of their keys which are accessed as an attribute (a property actually). For this reason, a
    tag must be formed by only ASCII letters, digits and underscores and its first character must be a
    letter. Although there is no maximum size for a tag, it is encouraged that it would be kept as short
    as possible to facilitate its usage.


    :Instantiating:

    .. code-block::
        :linenos:
        :name: taggable-code-instantiating
        :caption: Instantiating Taggable

        >>> from jangada.primitives import Taggable

        >>> obj = Taggable()
        >>> obj.tag  # None it is the default value of a tag

        >>> obj.tag = "room_temperature"
        >>> obj.tag
        'room_temperature'

    :Subclassing:

        Even though Taggable is not an abstract class, it is mainly designed to be extended rather than instantiated. As
        a matter of fact, subclassing Taggable is actually a quite easy task:

        .. code-block::
            :linenos:
            :name: taggable-code-subclassing
            :caption: Subclassing Taggable

            class CustomTaggable(Taggable):

                _default_tag = 'untagged'

                def _tag_is_about_to_change_callback(self, current_value, next_value):
                    if next_value == "python_is_bad":
                        raise ValueError("Well, that's not a good tag. Choose a better one, will you?!")

                def _tag_just_changed_callback(self, previous_value, current_value):
                    print("To whom it may concern, I henceforth should be referred as"
                          "{} and no longer as {}".format(current_value, previous_value))

        * First, if you do not want the default tag of your subclass to be :any:`None`, then you should
          override the class protected attribute :attr:`_default_tag`. Nevertheless, be aware that :any:`None`
          will always be accepted as an resetting key of tag. In other words, :code:`custom_taggable.tag = None` will
          reset the tag to the default value that you defined.

        * Second, if you would like more control on parsing the tags the user will set, then you should override
          the class protected method :meth:`_tag_is_about_to_change_callback`. This method is called after
          the given tag has been successfully parsed by the Taggable internal parser but right before the internal
          state that stores the tag is set with it. Then, if you wish to prevent it to be set, you might want to
          raise an exception inside this method. **This method is not abstract and by default it does nothing (pass)**.

        * Third, it is possible that your custom taggable object needs to run some code after its tag has changed
          (like informing other objects that it has happened). In this case, you should override the class protected
          method :meth:`_tag_just_changed_callback`. This method is always called after the tag is set with its
          new value. **This method is not abstract and by default it does nothing (pass)**.

        Furthermore, although it is common, there is no need to override the :meth:`__init__` method nor initialise the
        tag in it (unless you really want to do this). Actually, nor Taggable overrides it from object (that's why the
        :any:`obj` in the :ref:`taggable-code-instantiating` example could not be "initialised" with a tag) and the
        internal state that stores the tag is built, and the default value is assigned to it, at the first time it is
        called.



    .. seealso:: :class:`jangada.primitives.Describable`

    |

    """

    # ========== ========== ========== ========== ========== ========== class attributes
    _default_tag = None
    """Default value of the tag. Override it in your subclass if it needs another value as default."""

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    @classmethod
    def __parse_tag(cls, value):

        # None is always acceptable as the resetting key of tag
        if value is None:
            value = copy.deepcopy(cls._default_tag)

            # if the default value is also None, then return it
            if value is None:
                return

        # checks if the value is a string
        parse_types(value, str)

        # creates a list of characters that are allowed to figure in tag
        allowed_chars = string.ascii_letters + string.digits + '_'

        # checks if tag is empty or if there is any forbidden characters in it
        if not value or not all(char in allowed_chars for char in value):
            error = "tag accepts only the following characters: {}".format(allowed_chars)
            raise ValueError(error)

        # checks if the first char of tag is a number or underscore
        if value[0] in string.digits or value[0] == '_':
            error = "tag must start with letters"
            raise ValueError(error)

        # well, if the program reaches thi line, then no problem has been found in value
        return value

    # ========== ========== ========== ========== ========== ========== protected methods
    def _tag_is_about_to_change_callback(self, current_value, next_value):
        """
        This protected method, which is designed to be overridden by Taggable subclasses, is called before a new value
        for tag is officially set. It intends to provide more control of the values of the tag for the subclasses. By
        default, it does nothing.

        :param current_value: Current value of tag
        :type current_value: :class:`str` or :any:`None`
        :param next_value: Value of the tag that is attempting to be set
        :type next_value: :class:`str` or :any:`None`
        """

    def _tag_just_changed_callback(self, previous_value, current_value):
        """
        This protected method, which is designed to be overridden by Taggable subclasses, is called after a new value
        for tag has been set. By default, it does nothing.

        :param previous_value: Last value of tag
        :type previous_value: :class:`str` or :any:`None`
        :param current_value: Current value of tag (that has just been set)
        :type current_value: :class:`str` or :any:`None`
        """
        pass

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    @property
    def tag(self):
        """
        A tag is a mnemonic. It must be a non-empty string formed only by ASCII letters, digits and underscores
        and its first character must be a letter.

        :getter: (:class:`str` or :any:`None`) returns the tag of the object

        :setter: (:class:`str` or :any:`None`) sets the tag of the object

        :default value: None

        :raise:
            :TypeError: If the set value is neither None nor an instance of str.

            :ValueError: If it is set with a non-allowed string.

            Other types of exceptions may eventually be raised in subclasses that override the method
            :meth:`_tag_is_about_to_change_callback`.

        """

        try:
            return self.__tag

        except AttributeError:

            self.__tag = type(self).__parse_tag(None)

            return self.__tag

    @tag.setter
    def tag(self, value):

        # parses the given value
        next_value = type(self).__parse_tag(value)

        # saves current tag
        current_value = self.tag

        # emits the callback to verify if any other object has some problem with this value
        self._tag_is_about_to_change_callback(current_value, next_value)

        # if previous line raises no error, then the tag is good to go
        self.__tag = next_value

        # ---------- ---------- ---------- ---------- ---------- ----------
        previous_value = current_value

        current_value = next_value

        self._tag_just_changed_callback(previous_value, current_value)


# ========== ========== ========== ========== ========== ========== Describable
class Describable:
    """
    Objects with descriptions

    At the most obvious way, a description is a string that contains information about an object, usually describing it.
    Different from :py:attr:`tags <jangada.primitives.Taggable.tag>`, descriptions may be any non-empty string (in this
    context, a string of spaces is also considered to be empty). The description of a Describable object is designed to
    be accessed (read and write) as an attribute (see :py:attr:`description`) and by default its value is :any:`None`
    (see :attr:`_default_description`).

    Of course the main goal of having a description is let the user see it whenever he needs. For that reason
    descriptions are usually intended to be shown in console and to avoid showing massive text on the screen,
    Describable defines the maximum length for description representations on console through the property
    :py:attr:`max_length_description_repr` which can be understood as the maximum number of characters that will be
    shown whenever a short representation of description is needed (see :meth:`_get_description_repr`). By default, it
    is set to 30 characters (see :attr:`_default_max_length_description_repr`).


    :Instantiating:

        .. code-block::
            :linenos:
            :name: describable-code-instantiating
            :caption: Instantiating Describable

            >>> from jangada.primitives import Describable

            >>> obj = Describable()
            >>> obj.description  # None it is the default value of a description

            >>> obj.description = "Temperature of the living room"
            >>> obj.description
            'Temperature of them living room'

    :Subclassing:

        Although Describable is not an abstract class, it is mainly designed to be extended rather than instantiated. As
        a matter of fact, subclassing Describable is actually a quite easy task:

        .. code-block::
            :linenos:
            :name: describable-code-subclassing
            :caption: Subclassing Describable

            class CustomDescribable(Describable):

                _default_description = 'no description available'

                _defatul_max_length_description_repr = 25

                def _description_just_changed_callback(self, previous_value, current_value):
                    print("My new description is: {}".format(current_value))

        * First, if you do not want the default description of your subclass to be :any:`None`, then you should
          override the class protected attribute :attr:`_default_description`. Nevertheless, be aware that
          :any:`None` will always be accepted as an resetting key of description. In other words,
          :code:`custom_describable.description = None` will reset the description to the default value that you
          defined. In the same fashion, you can change the default value of the maximum number of characters that
          short description representations will have by setting :attr:`_default_max_length_description_repr`.

        * Second, it is possible that your custom describable object needs to run some code after its description
          changed (like informing other objects that it has happened). In this case, you should override the class
          protected method :meth:`_description_just_changed_callback`. This method is always called after the
          description is set. **This method is not abstract and by default it does nothing (pass)**.

        Furthermore, although it is common, there is no need to override the :meth:`__init__` method nor initialise the
        description in it (unless you really want to do this). Actually, nor Describable overrides it from object
        (that's why the :any:`obj` in the :ref:`describable-code-instantiating` example could not be "initialised" with
        a description) and the internal state that stores it is built, and the default value is assigned to it, at the
        first time it is called.




    .. seealso::
        :class:`jangada.primitives.Taggable`

    |
    """

    # ========== ========== ========== ========== ========== ========== class attributes
    _default_description = None
    """Default value of the description. Override it in your subclass if it needs another value as default."""

    _default_max_length_description_repr = 30
    """Default value of the maximum length of description representation. 
    Override it in your subclass if it needs another value as default."""

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    @classmethod
    def __parse_description(cls, value):

        if value is None:
            value = copy.deepcopy(cls._default_description)

            if value is None:
                return

        parse_types(value, str)

        value = value.strip()

        if not value:
            error = 'description cannot be an empty string. If it must be unset, then set it to None'
            raise ValueError(error)

        return value

    @classmethod
    def __parse_max_length_description_repr(cls, value):

        if value is None:
            value = copy.deepcopy(cls._default_max_length_description_repr)

        parse_types(value, int)

        if value < 10:
            error = 'max_length_description_repr must be greater or equal to 10. Given {}'
            raise ValueError(error.format(value))

        return value

    # ========== ========== ========== ========== ========== ========== protected methods
    def _get_description_repr(self):
        """
        The representation of the description.

        :return:
             If the length of description is less or equal than :py:attr:`max_length_description_repr`, than it is returned.
             Else, the first :code:`max_length_description_repr - 3` characters plus :any:`'...'` is returned.

        :rtype:
            :class:`str` or :any:`None`
        """
        if not self.description:
            return

        if len(self.description) <= self.max_length_description_repr:
            return self.description

        return self.description[:self.max_length_description_repr - 3] + '...'

    def _description_just_changed_callback(self, previous_value, current_value):
        """
        This protected method, which is designed to be overridden by Describable subclasses, is called after a new value
        for description has been set. By default, it does nothing.

        :param previous_value: Last value of description
        :type previous_value: :class:`str` or :any:`None`
        :param current_value: Current value of description (that has just been set)
        :type current_value: :class:`str` or :any:`None`
        """
        pass

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    @property
    def description(self):
        """
        The description. It must be a non-empty string (in this context, a string of spaces is also an empty string).

        :getter: (:class:`str` or :any:`None`) returns the description of the object

        :setter: (:class:`str` or :any:`None`) sets the description of the object

        :default value: None

        :raise:
            :TypeError: If the set value is neither None nor an instance of str.

            :ValueError: If it is an empty string.
        """
        try:
            return self.__description

        except AttributeError:

            self.__description = type(self).__parse_description(type(self)._default_description)

            return self.__description

    @description.setter
    def description(self, value):

        next_value = self.__parse_description(value)

        current_value = self.description

        self.__description = next_value

        self._description_just_changed_callback(current_value, next_value)

    @property
    def max_length_description_repr(self):
        """
        The maximum length for the description representation. It must be greater-than-9 integer.

        :getter: (:class:`int`) returns the maximum length for the description representation on console.

        :setter: (:class:`str` or :any:`None`) sets the maximum length for the description representation on console.

        :default value: 30

        :raise:
            :TypeError: If the set value is neither None nor an instance of int.

            :ValueError: If it is less than 10.
        """
        try:
            return self.__max_length_description_repr

        except AttributeError:

            self.__max_length_description_repr = \
                type(self).__parse_max_length_description_repr(type(self)._default_max_length_description_repr)

            return self.__max_length_description_repr

    @max_length_description_repr.setter
    def max_length_description_repr(self, value):

        self.__max_length_description_repr = type(self).__parse_max_length_description_repr(value)


# ========== ========== ========== ========== ========== ========== Serialisable
class Serialisable(metaclass=ABCMeta):
    """
    Serialisable objects

    Serialisable is an abstract class designed to grant to its heirs the ability to serialise the properties that define
    their instances into a dictionary (see :meth:`_serialise`) and unserialise them reconstructing the object from the
    serialised data (see :meth:`_unserialise`). Serialisable has only one abstract method, which also happens to be a
    class method: :meth:`_get_serialisable_property_names`. This method should return a list of the property names that
    should figure in serialisation.

    .. note::
        Serialisable does not implement the properties that should be serialised, they must be implemented by its
        heirs. It just know how to serialise and unserialise them.


    :param args:

        If provided, it must be only one object (:code:`len(args) == 1`) which shall be an instance of the current
        subclass. This signature is mainly designed to perform a copy of the given object by casting. The kwargs are
        ignored.

    :param kwargs:

        The serialised properties. It is ignored if **args** is provided.

    :Subclassing and Usage:

        As an example, let's imagine the class Position which is completely determined by its ``x`` and ``y``
        properties. A serialisable implementation of Position would be

            .. code-block::
                :linenos:
                :name: serialisable-code-subclassing
                :caption: Position: a subclass of Serialisable

                class Position(Serialisable):

                    @classmethod
                    def _get_serialisable_property_names(cls):
                        return ['x', 'y']

                    @property
                    def x(self):
                        return self.__x

                    @x.setter
                    def x(self, value):
                        self.__x = value

                    @property
                    def y(self):
                        return self.__y

                    @y.setter
                    def y(self, value):
                        self.__y = value


        The class Position is ready to be instantiated and serialised:

            .. code-block::
                :linenos:
                :name: instantiate-position-Serialisable-subclass
                :caption: Instantiating Position

                >>> pos = Position(x=1)
                >>> pos._serialise()
                {'x': 1, 'y': None}

        It is worth noting that the method :meth:`_serialise` is protected. That is because it is designed to be accessed
        internally and not like it was in :ref:`instantiate-position-Serialisable-subclass`. In addition, if a key is not
        provided during the initialisation, then it is set to :any:`None`. Serialisable objects also know how to copy (using
        the method :meth:`copy` or conveniently by casting the object) and compare themselves:

            .. code-block::
                :linenos:
                :name: copy-and-compare-position-Serialisable-subclass
                :caption: Copying and comparing positions

                >>> pos_A = Position(x=1, y=-5)
                >>> pos_B = pos_A.copy()
                >>> pos_B == pos_A
                True
                >>> pos_C = Position(pos_B)
                >>> pos_C == pos_A
                True

    .. seealso::

        :class:`jangada.primitives.Taggable`

    |
    """

    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    def __init__(self, *args, **kwargs):
        if not args:
            # if it reaches here, then it is trying to initialise the object with data
            self._unserialise(kwargs)

        elif len(args) == 1 and isinstance(args[0], type(self)):
            # if it reaches here, then it's performing a copy
            self._unserialise(args[0]._serialise())

        else:
            error = "Given args do not match any available signature for initialising the Serialisable interface"
            raise ValueError(error)

    def __eq__(self, other):
        """
        Implements the :any:`==` comparison of two serialisable objects.

        :return: :any:`True` if all properties of both objects are equal (include the properties that are also
            serialisable objects) and :any:`False` if at least one is not.
        :rtype: :any:`bool`
        :raise TypeError: If the objects are not from the same type.
        """
        if type(other) is type(self):
            return other._serialise() == self._serialise()

        raise TypeError("Cannot compare {} with {}".format(type(self).__name__), type(other).__name__)

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    @classmethod
    @abstractmethod
    def _get_serialisable_property_names(cls):
        """


        :return:
            A list with the names of the properties to be serialised.

        :rtype:
            :any:`list` or :any:`tuple` of :any:`str`
        """
        raise NotImplementedError()

    def _serialise(self):
        """
        :return:
            The serialised properties

        :rtype:
            :any:`dict`
        """
        data = {}

        for key in type(self)._get_serialisable_property_names():
            value = getattr(self, key)

            if isinstance(value, (list, tuple)):
                data[key] = [v._serialise() if isinstance(v, Serialisable) else copy.deepcopy(v) for v in value]

            elif isinstance(value, dict):
                data[key] = {k: v._serialise() if isinstance(v, Serialisable) else copy.deepcopy(v) for k, v in
                             value.items()}

            else:
                data[key] = value._serialise() if isinstance(value, Serialisable) else copy.deepcopy(value)

        return data

    def _unserialise(self, data):
        """
        :param data:
            The serialised properties to be set in the current object

        :type data:
            :any:`dict`

        :raise:
            :TypeError:
                If the data is not a :any:`dict`.

            :ValueError:
                If data contains keys which are not serialisable properties of that object.
        """
        # data must be a dictionary
        parse_types(data, dict)

        # set the serialisable properties
        for key in type(self)._get_serialisable_property_names():
            setattr(self, key, data.pop(key, None))

        # at this point, the dictionary should be empty
        if data:
            error = "There is no signature with the keys {}"
            raise ValueError(error.format(data.keys()))

    # ========== ========== ========== ========== ========== ========== public methods
    def copy(self):
        """
        :return:
            A copy of the current object

        :rtype:
            the same of the subclass
        """
        # return type(self)(self)
        return type(self)(**self._serialise())

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== Representable
class Representable(metaclass=ABCMeta):
    """
    Objects with a nice representation on console

    Representable is an abstract class that grant to its heirs a structured representation on console. The
    representation is composed by two parts: a header and a body.

    :Subclassing:

        .. code-block::
                :linenos:
                :name: representable-code-subclassing
                :caption: Subclassing Representable

                class CustomRepresentable(Representable):

                    def _get_header(self):
                        return "REPR EXAMPLE"

                    def _get_body(self):

                        c1 = "Some Content"
                        c2 = "Some More Content"
                        c3 = "Last Content"

                        body = "{c1}\\n{{fence}}\\n{c2}\\n{{fence}}\\n{c3}".format(c1=c1, c2=c2, c3=c3)

                        return body, length



    |
    """

    # ========== ========== ========== ========== ========== ========== class attributes
    _available_colours = {
        'blue': '\033[94m{}\033[0m',
        'cyan': '\033[96m{}\033[0m',
        'darkcyan': '\033[36m{}\033[0m',
        'green': '\033[92m{}\033[0m',
        'purple': '\033[95m{}\033[0m',
        'red': '\033[91m{}\033[0m',
        'yellow': '\033[93m{}\033[0m'
    }

    # ========== ========== ========== ========== ========== ========== special methods
    def __str__(self):

        # ---------- ---------- ---------- ---------- ---------- ---------- header
        raw_header = self._get_header()

        # calculates header length
        length = len(raw_header)

        header = raw_header

        # formats header colour
        if self.__get_option('header_colour'):
            header = self.__get_colour_formatted_text(header, self.__get_option('header_colour'))

        # formats header weight
        if self.__get_option('header_bold'):
            header = self.__get_bold_formatted_text(header)

        # ---------- ---------- ---------- ---------- ---------- ---------- body
        body = self._get_body()

        # copies body
        contents = body

        # unformats contents
        for index in [0, 1, 36, 91, 92, 93, 94, 95, 96]:
            contents = contents.replace('\033[{}m'.format(index), '')

        # gets max length
        length = max(length, *[len(line) for line in contents.split('\n') if '{{fence}}' not in line])

        # ---------- ---------- ---------- ---------- ---------- ---------- create wall and fence
        wall = self.__wall(length)
        fence = self.__fence(length)

        # ---------- ---------- ---------- ---------- ---------- ---------- align header
        if Representable.__get_option('header_alignment') == 'centre':
            header = "{{:^{}s}}".format(length + len(header) - len(raw_header)).format(header)

        elif Representable.__get_option('header_alignment') == 'right':
            header = "{{:>{}s}}".format(length + len(header) - len(raw_header)).format(header)

        # ---------- ---------- ---------- ---------- ---------- ----------
        return """{{wall}}
{{header}}
{{fence}}
{body}
{{wall}}
""".format(body=body).format(header=header, wall=wall, fence=fence)

    def __repr__(self):
        return str(self)

    # ========== ========== ========== ========== ========== ========== private methods
    @staticmethod
    def __get_option(option_tag):

        settings_file_path = Path(__file__).parent.parent / "settings" / "settings.json"

        with settings_file_path.open() as file:
            return json.load(file)[option_tag]

    @staticmethod
    def __get_colour_formatted_text(text, colour):
        return Representable._available_colours[colour].format(text)

    @staticmethod
    def __get_bold_formatted_text(text):
        return '\033[1m{}\033[0m'.format(text)

    @staticmethod
    def __wall(length):

        ret = length * Representable.__get_option('wall_char')

        if Representable.__get_option('wall_colour'):
            ret = Representable.__get_colour_formatted_text(ret, Representable.__get_option('wall_colour'))

        if Representable.__get_option('wall_bold'):
            ret = Representable.__get_bold_formatted_text(ret)

        return ret

    @staticmethod
    def __fence(length):

        ret = length * Representable.__get_option('fence_char')

        if Representable.__get_option('fence_colour'):
            ret = Representable.__get_colour_formatted_text(ret, Representable.__get_option('fence_colour'))

        if Representable.__get_option('fence_bold'):
            ret = Representable.__get_bold_formatted_text(ret)

        return ret

    # ========== ========== ========== ========== ========== ========== protected methods
    @staticmethod
    def _format_as_property(text):
        """"""
        if Representable.__get_option('properties_colour'):
            text = Representable.__get_colour_formatted_text(text, Representable.__get_option('properties_colour'))

        if Representable.__get_option('properties_bold'):
            text = Representable.__get_bold_formatted_text(text)

        return text

    @staticmethod
    def _create_formatted_frame(data, columns=None, sort_values_by=None, alignment=None, index=True):
        """

        alignment = {
            'col': {'header': 'left', 'values': 'left'},
            'col': {'header': 'left', 'values': 'left'},
            'col': {'header': 'left', 'values': 'left'},
            'col': {'header': 'left', 'values': 'left'},
        }

        :param data:
        :param columns:
        :param sort_values_by:
        :param left_justified_columns:
        :return:
        """
        if columns is None:
            frame = pandas.DataFrame(data)

        else:
            frame = pandas.DataFrame(data, columns=columns)

        frame = frame.astype(str)  # TODO: Is this line really necessary?

        if sort_values_by:
            frame.sort_values(by=sort_values_by, inplace=True)

        frame.reset_index(inplace=True, drop=True)
        frame.index += 1

        # ---------- ---------- ---------- ---------- ---------- ----------

        def left_justified(column):
            def __justify(value):
                return "{{:<{}s}}".format(frame[column].str.len().max()).format(value)

            return __justify

        def centre_justified(column):
            def __justify(value):
                return "{{:^{}s}}".format(frame[column].str.len().max()).format(value)

            return __justify

        def right_justified(column):
            def __justify(value):
                return "  {{:>{}s}}".format(frame[column].str.len().max()).format(value)

            return __justify

        # ---------- ---------- ---------- ---------- ---------- ----------

        header = []

        formatters = {}

        if not alignment:
            alignment = {}

        for col in frame.columns:

            column_alignment = alignment.pop(col, None)

            if column_alignment:

                # ---------- ---------- ---------- ---------- ---------- ---------- header alignment
                header_alignment = column_alignment.pop('header', '').lower()

                if header_alignment in ['left', 'l']:
                    header.append('{{:<{}s}}'.format(frame[col].str.len().max()).format(col))

                elif header_alignment in ['centre', 'center', 'c']:
                    header.append('{{:^{}s}}'.format(frame[col].str.len().max()).format(col))

                elif header_alignment in ['', 'right', 'r']:
                    header.append('  {{:>{}s}}'.format(frame[col].str.len().max()).format(col))

                else:
                    error = "Unexpected value for header alignment: {}"
                    raise ValueError(error.format(header_alignment))

                # ---------- ---------- ---------- ---------- ---------- ---------- content alignnment
                values_alignment = column_alignment.pop('values', '').lower()

                if values_alignment in ['left', 'l']:
                    # formatters[col] = lambda value: "{{:<{}s}}".format(frame[col].str.len().max()).format(value)
                    formatters[col] = left_justified(col)

                elif values_alignment in ['centre', 'center', 'c']:
                    # formatters[col] = lambda value: "{{:^{}s}}".format(frame[col].str.len().max()).format(value)
                    formatters[col] = centre_justified(col)

                elif values_alignment in ['', 'right', 'r']:
                    # formatters[col] = lambda value: "{{:>{}s}}".format(frame[col].str.len().max()).format(value)
                    formatters[col] = right_justified(col)

                else:
                    error = "Unexpected value for header alignment: {}"
                    raise ValueError(error.format(header_alignment))

            else:
                header.append(col)

        frame = frame.to_string(header=header, formatters=formatters, index=index)

        # ---------- ---------- ---------- ---------- ---------- ----------

        lines = frame.split('\n')

        if not index:
            lines = [line.strip() for line in lines]

        lines[0] = Representable._format_as_property(lines[0])

        frame = '\n'.join(lines)

        return frame

    @staticmethod
    def _create_formatted_form(data, order=None, min_gap=4, uppercase=False, capitalise=False, capitalize=False):
        """

        :param data:
        :return:
        """

        # ---------- ---------- ---------- ---------- ---------- ---------- formatting keys

        if order is None:

            if uppercase:
                data = {Representable._format_as_property(key.upper()): value for key, value in data.items()}

            elif capitalise or capitalize:
                data = {Representable._format_as_property(key.capitalize()): value for key, value in data.items()}

            else:
                data = {Representable._format_as_property(key): value for key, value in data.items()}

        else:

            ordered_data = collections.OrderedDict()

            if uppercase:
                for key in order:
                    ordered_data[Representable._format_as_property(key.upper())] = data[key]

            elif capitalise or capitalize:
                for key in order:
                    ordered_data[Representable._format_as_property(key.capitalize())] = data[key]

            else:
                for key in order:
                    ordered_data[Representable._format_as_property(key)] = data[key]

            data = ordered_data

        # ----------  this is a nice implementation, but it doesn't work somehow due the formatting chars
        # longest_key_length = max(len(key) for key in data)
        # template = "{{key:>{max_len}s}}:{min_gap}{{value}}".format(max_len=longest_key_length, min_gap=min_gap*' ')
        # return '\n'.join(template.format(key=Representable._format_as_property(k), value=v) for k, v in data.items())

        # ---------- ---------- ---------- ---------- ---------- I didn't like this implementation, but it works
        gap = max(len(key) for key in data) + min_gap

        template = "{key}:{gap}{value}"

        return '\n'.join(
            template.format(key=key, value=value, gap=' ' * (gap - len(key))) for key, value in data.items())

    @abstractmethod
    def _get_header(self):
        """

        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_body(self):
        """

        :return:
            the body and the total length

        :rtype:
            tuple containing body: str, length: int
        """
        raise NotImplementedError()

    # ========== ========== ========== ========== ========== ========== public methods
    @staticmethod
    def parse_colour(colour):

        if colour.lower() in Representable._available_colours:
            return colour.lower()

        ValueError("There is no colour named {} available".format(colour))

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== Ownable
class Ownable(metaclass=ABCMeta):
    """
    Objects that belong to another

    Ownership is a composition relationship which is established between an instance of :class:`Ownable` and an instance
    of :class:`Owner`. The owner of an ownable object must be set and gotten through the property :py:attr:`owner`. By
    default, an ownable object has no owner and therefore :py:attr:`owner` would retrieve :any:`None`.

    Of course :class:`Ownable` is an abstract class aiming to grant the property to be owned to its heirs. Therefore, it
    must be subclassed to be used.

    :Subclassing:

        Since :class:`Ownable` has only one abstract method (see :meth:`_get_allowed_owner_types`), which also happens
        to be static, subclass it is a straightforward task. :meth:`_get_allowed_owner_types` must return the type or
        a tuple of types that may own the instances of this subclass. Of course those types must be subclasses of
        :class:`Owner`.

        .. code-block::
            :linenos:
            :name: ownable-code-subclassing
            :caption: Subclassing Ownable

            class OwnerA(Owner):
                ...


            class OwnerB(Owner):
                ...


            class CustomOwnable(Ownable):

                @staticmethod
                def _get_allowed_owner_types():
                    return OwnerA, OwnerB

                def _owner_is_about_to_change_callback(self, current_owner, next_owner):
                    ...

                def _owner_just_changed_callback(self, previous_owner, current_owner):
                    ...

        Analogously to :class:`Taggable` design, :class:`Ownable` also has two callback methods:

            * :meth:`_owner_is_about_to_change_callback` is triggered when a new owner is trying to be set and it is
              designed to provide more control to the user, who might want to raise an error or run some routine. **It
              is not an abstract method and by default it does nothing (pass).**

            * :meth:`_owner_just_changed_callback` is triggered right after a new owner has been set and it is
              designed to spread the news to whomever it concerns. **It is not an abstract method and by default it does
              nothing (pass).**

        Finally, :class:`Ownable` does not override :meth:`__init__` method from :class:`object`. Therefore, no
        initialisation is required from subclasses.

    |
    """
    # ========== ========== ========== ========== ========== ========== class attributes
    __default_owner = None

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    @classmethod
    def __parse_owner(cls, value):

        # None is always acceptable as the resetting key of tag
        if value is None:
            return

        # FIXME: this checking shouldn't be here, but in a metaclass.
        #        However I really didn't want to extend ABCmeta when I wrote this code.
        if not all(issubclass(owner_cls, Owner) for owner_cls in cls._get_allowed_owner_types()):
            error = "Owners must be subclasses of Owner"
            raise TypeError(error)

        if not isinstance(value, tuple(cls._get_allowed_owner_types())):
            error = "Instances of {} are not allowed to own instances of {}".format(type(value).__name__, cls.__name__)
            raise TypeError(error)

        return value

    # ========== ========== ========== ========== ========== ========== protected methods
    @staticmethod
    @abstractmethod
    def _get_allowed_owner_types():
        """
        :return: The classes whose instances are allowed to own the instances of the subclass.
        :rtype: a subclass or a tuple of subclasses of :class:`Owner`
        """
        raise NotImplementedError()

    def _owner_is_about_to_change_callback(self, current_owner, next_owner):
        """
        This callback is triggered when a new owner is trying to be set and it is mainly designed to provide more
        control to the user, who might want to raise an error or run some routine.

        .. note:: It is not an abstract method and by default it does nothing (pass).

        :param current_owner:

            The actual owner. It may also be accessed through ``self.owner``, but it is conveniently provided here as an
            argument.

        :type current_owner:

            :class:`Owner`

        :param next_owner:

            The owner that is trying to be set.

        :type next_owner:

            :class:`Owner`

        """
        pass

    def _owner_just_changed_callback(self, previous_owner, current_owner):
        """
        This callback is triggered is triggered right after a new owner has been set and it is designed to spread the
        news to whomever it concerns.

        .. note:: It is not an abstract method and by default it does nothing (pass).

        :param previous_owner:

            The last owner.

        :type previous_owner:

            :class:`Owner`

        :param current_owner:

            The new owner. It may also be accessed through ``self.owner``, but it is conveniently provided here as an
            argument.

        :type current_owner:

            :class:`Owner`
        """
        pass

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- read-only properties
    @property
    def branch(self):
        """
        In this ownership context, a branch is a sequence of objects where each element is owned by the next. The branch
        is recursively calculated and it stops when it reaches an element that has no owner (in this case, the last
        element of the sequence will be :any:`None`) or that is not ownable (in this case, the last element will be this
        element). The object itself is not included in the sequence, which starts with its owner.

        .. note:: This is a read-only property.

        :return: the sequence branch of owners of this object.
        :rtype: tuple of :class:`Owner`
        """

        if isinstance(self.owner, Ownable):
            return (self.owner, *self.owner.branch)

        return self.owner,

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    @property
    def owner(self):
        """
        The owner of this object. It must be an instance of :class:`Owner`.

        :getter: (:class:`Owner` or :any:`None`) returns the owner of the object

        :setter: (:class:`Owner` or :any:`None`) sets the owner of the object

        :default value: None

        :raise:
            :TypeError:
                If the set value is neither None nor an instance of the allowed owner types (see:
                :meth:`_get_allowed_owner_types`).

            Other types of exceptions may eventually be raised in subclasses that override the method
            :meth:`_owner_is_about_to_change_callback`.

        """

        try:
            return self.__owner

        except AttributeError:

            self.__owner = type(self).__parse_owner(type(self).__default_owner)

            return self.__owner

    @owner.setter
    def owner(self, value):

        # parses the given value
        next_value = type(self).__parse_owner(value)

        # saves current tag
        current_value = self.owner

        # emits the callback to verify if any other object has some problem with this value
        self._owner_is_about_to_change_callback(current_value, next_value)

        # if previous line raises no error, then the owner is good to be set
        self.__owner = next_value

        # ---------- ---------- ---------- ---------- ---------- ----------
        previous_value = current_value

        current_value = next_value

        self._owner_just_changed_callback(previous_value, current_value)


# ========== ========== ========== ========== ========== ========== Owner
class Owner:
    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- protected properties
    ...

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- public properties
    ...


# ========== ========== ========== ========== ========== ========== Quantity
class Quantity:
    # ========== ========== ========== ========== ========== ========== class attributes
    _default_unit = None
    """Default value of the unit. Override it in your subclass if it needs another value as default."""

    # ========== ========== ========== ========== ========== ========== special methods
    @classmethod
    def __parse_unit(cls, value):

        # None is always acceptable as the resetting key of unit
        if value is None:
            value = copy.deepcopy(cls._default_unit)

            # if the default value is also None, then return it
            if value is None:
                return

        # checks if the value is a string
        parse_types(value, str)

        value = value.strip()

        if not value:
            error = 'unit cannot be an empty string. If it must be unset, then set it to None'
            raise ValueError(error)

        return value

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    @property
    def unit(self):
        """
        The description. It must be a non-empty string (in this context, a string of spaces is also an empty string).

        :getter: (:class:`str` or :any:`None`) returns the description of the object

        :setter: (:class:`str` or :any:`None`) sets the description of the object

        :default value: None

        :raise:
            :TypeError: If the set value is neither None nor an instance of str.

            :ValueError: If it is an empty string.
        """
        try:
            return self.__unit

        except AttributeError:

            self.__unit = type(self).__parse_unit(type(self)._default_unit)

            return self.__unit

    @unit.setter
    def unit(self, value):
        self.__unit = type(self).__parse_unit(value)