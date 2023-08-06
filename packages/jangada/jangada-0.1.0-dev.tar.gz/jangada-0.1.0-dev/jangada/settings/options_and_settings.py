#  -*- coding: utf-8 -*-
"""

Author: Rafael R. L. Benevides
Date: 10/03/2021

"""

import json

from warnings import warn

from pathlib import Path

from matplotlib import style

from jangada.utils import parser, parse_types

from jangada.primitives import OwnableComponent, Serialisable, Owner, Representable


class Option(OwnableComponent):
    """
    Jangada Options
    """

    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    def __init__(self, owner=None, parser=None, **kwargs):

        self.__blocked = False

        if parser is None:
            self.__parser = lambda value: value

        elif callable(parser):
            self.__parser = parser

        else:
            raise TypeError('parser must be callable')

        super(Option, self).__init__(owner=owner, **kwargs)

        self.__blocked = True

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    @classmethod
    def _get_serialisable_property_names(cls):
        return ['tag', 'description', 'default', 'value']

    def _get_header(self):
        return 'OPTION'

    def _get_body(self):
        data = {
            'tag': self.tag,
            # 'description': self._get_description_repr(),
            'description': self.description,
            'default value': self.default,
            'current value': self.value,
        }

        order = ['tag', 'description', 'default value', 'current value']

        return self._create_formatted_form(data, order, capitalise=True)

    @staticmethod
    def _get_allowed_owner_types():
        return Settings,

    # ========== ========== ========== ========== ========== ========== public methods
    def parse(self, value):
        """

        :param value:
        :return:
        """
        return self.__parser(value)

    def reset(self):
        self.value = self.default

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    @property
    def value(self):
        """

        :return:
        """
        return self.__value

    @value.setter
    def value(self, new_value):

        self.__value = self.parse(new_value)

        if self.__blocked:
            self.owner.save()

    @property
    def default(self):
        """

        :return:
        """
        return self.__default

    @default.setter
    def default(self, value):

        if self.__blocked:
            raise AttributeError("default of an option is a read-only property")

        self.__default = self.parse(value)

    @OwnableComponent.tag.setter
    def tag(self, value):

        if self.__blocked:
            raise AttributeError("tag of an option is a read-only property")

        OwnableComponent.tag.fset(self, value)

    @OwnableComponent.description.setter
    def description(self, value):

        if self.__blocked:
            raise AttributeError("description of an option is a read-only property")

        OwnableComponent.description.fset(self, value)

    @OwnableComponent.owner.setter
    def owner(self, value):

        if self.__blocked:
            raise AttributeError("owner of an option is a read-only property")

        OwnableComponent.owner.fset(self, value)


class Settings(Serialisable, Representable, Owner):
    """
    Jangada Global Settings



    """

    # ========== ========== ========== ========== ========== ========== parsers
    @staticmethod
    def styles_file_parser(value):

        if value is None:
            return

        path = Path(value)

        if not path.is_file():
            error = 'The path "{}" does not point to a file'
            raise FileNotFoundError(error.format(value))

        return str(path)

    @staticmethod
    def style_parser(value):

        value = parse_types(value, str)

        if value not in [*style.available, 'default']:
            error = "Given value is not an available style. Check available styles by running matplotlib.style.available"
            raise ValueError(error)

        return value

    @staticmethod
    def char_parser(value):
        if isinstance(value, str) and len(value) == 1:
            return value

        error = "Expected a character. Given {}".format(value)
        raise ValueError(error)

    @staticmethod
    def colour_parser(value):

        if value is None:
            return

        value = parse_types(value, str).lower()

        if value not in Representable._available_colours:
            error = "{} is not an available color".format(value)
            raise ValueError(error)

        return value

    @staticmethod
    def alignment_parser(value):

        value = parse_types(value, str).lower()

        if value in ['left', 'l']:
            return 'left'

        if value in ['centre', 'center', 'c']:
            return 'centre'

        if value in ['right', 'r']:
            return 'right'

        error = "The allowed alignments are 'left', 'l', 'centre', 'center', 'c', 'right', 'r'"
        raise ValueError(error)

    # ========== ========== ========== ========== ========== ========== class attributes
    _options = {
        "styles_file": {
            "tag": "styles_file",
            "description": "Path to a custom styles file",
            "parser": styles_file_parser.__func__,
            "default": None
        },
        "style": {
            "tag": "style",
            "description": "Matplotlib style for global use in Jangada",
            "parser": style_parser.__func__,
            "default": "default"
        },
        "wall_char": {
            "tag": "wall_char",
            "description": "[COR] Character of the wall",
            "parser": char_parser.__func__,
            "default": "="
        },
        "fence_char": {
            "tag": "fence_char",
            "description": "[COR] Character of the fence",
            "parser": char_parser.__func__,
            "default": "-"
        },
        "header_colour": {
            "tag": "header_colour",
            "description": "[COR] Header colour",
            "parser": colour_parser.__func__,
            "default": "yellow"
        },
        "header_alignment": {
            "tag": "header_alignment",
            "description": "[COR] Header Alignment",
            "parser": alignment_parser.__func__,
            "default": "centre"
        },
        "properties_colour": {
            "tag": "properties_colour",
            "description": "[COR] Properties/column names colour",
            "parser": colour_parser.__func__,
            "default": None
        },
        "header_bold": {
            "tag": "header_bold",
            "description": "[COR] Set header font to bold",
            "parser": parser(bool),
            "default": False
        },
        "properties_bold": {
            "tag": "properties_bold",
            "description": "[COR] Set properties/column names font to bold",
            "parser": parser(bool),
            "default": True
        },
        "wall_colour": {
            "tag": "wall_colour",
            "description": "[COR] Colour of the wall",
            "parser": colour_parser.__func__,
            "default": None
        },
        "fence_colour": {
            "tag": "fence_colour",
            "description": "[COR] Colour of the fence",
            "parser": colour_parser.__func__,
            "default": None
        },
        "wall_bold": {
            "tag": "wall_bold",
            "description": "[COR] Set wall font to bold",
            "parser": parser(bool),
            "default": False
        },
        "fence_bold": {
            "tag": "fence_bold",
            "description": "[COR] Set fence font to bold",
            "parser": parser(bool),
            "default": False
        }
    }

    _instance = None

    _settings_file_path = Path(__file__).parent / 'settings.json'

    # ========== ========== ========== ========== ========== ========== special methods
    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):

        if self._settings_file_path.is_file():

            try:
                with self._settings_file_path.open() as settings_file:
                    settings = json.load(settings_file)

            except json.decoder.JSONDecodeError:

                warn('settings.json seems to be corrupted. Another file with default values will be created.')

                settings = {tag: option['default'] for tag, option in Settings._options.items()}

                with self._settings_file_path.open('w') as settings_file:
                    json.dump(settings, settings_file, indent=4)

            else:

                if len(settings) != len(Settings._options):

                    warn('settings.json seems to be corrupted. Another file with default values will be created.')

                    settings = {tag: option['default'] for tag, option in Settings._options.items()}

                    with self._settings_file_path.open('w') as settings_file:
                        json.dump(settings, settings_file, indent=4)

        else:
            settings = {tag: option['default'] for tag, option in Settings._options.items()}

            with self._settings_file_path.open('w') as settings_file:
                json.dump(settings, settings_file, indent=4)

        # ---------- ---------- ---------- ---------- ---------- ----------
        for tag, value in settings.items():
            Settings._options[tag]['value'] = value

        self._unserialise(Settings._options)

    def __getattr__(self, item):
        # try:
        #     return super().__getattr__(self, item)
        #
        # except AttributeError as error:
        #
        #     try:
        #         return self.__options[item]
        #
        #     except KeyError:
        #
        #         raise error
        return self.__options[item]

    def __setattr__(self, item, value):

        if item in Settings._options:
            self.__options[item].value = value

        elif item == '_Settings__options':
            super().__setattr__(item, value)

        else:
            raise AttributeError()

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    def _serialise(self):
        return {tag: option.value for tag, option in self.__options.items()}

    def _unserialise(self, data):
        # data must be a dictionary
        parse_types(data, dict)

        self.__options = {tag: Option(owner=self, **option) for tag, option in data.items()}

    @classmethod
    def _get_serialisable_property_names(cls):
        raise NotImplementedError()

    def _get_header(self):
        return "JANGADA GLOBAL SETTINGS"

    def _get_body(self):

        # ---------- ---------- ---------- ---------- ---------- ---------- frame
        data = [{
            'tag': option.tag,
            'description': option.description,
            'default value': option.default,
            'current value': option.value
        } for option in self.__options.values()]

        columns = ['tag', 'description', 'default value', 'current value']

        alignment = {
            'tag': {'header': 'left', 'values': 'left'},
            'description': {'header': 'centre', 'values': 'left'},
            'default value': {'header': 'right', 'values': 'right'},
            'current value': {'header': 'right', 'values': 'right'},
        }

        frame = self._create_formatted_frame(data, columns=columns, alignment=alignment, sort_values_by='tag')

        # ---------- ---------- ---------- ---------- ---------- ---------- form
        form = self._create_formatted_form({'COR': 'Console Object Representation'})

        return "{frame}\n{{fence}}\n{form}".format(frame=frame, form=form)

    # ========== ========== ========== ========== ========== ========== public methods
    def save(self):

        with self._settings_file_path.open('w') as settings_file:
            json.dump(self._serialise(), settings_file, indent=4)

    def reset(self):

        for option in self.__options.values():
            option.reset()

    def load(self, settings_source):

        if isinstance(settings_source, dict):

            for tag, value in settings_source.items():
                self.__options[tag].value = value

        elif isinstance(settings_source, (str, Path)):
            with Path(settings_source).open() as file:
                self.load(json.load(file))

        else:
            error = "source type does not match any signature for load method. Expected dict, str or Path. Given {}"
            raise TypeError(error.format(settings_source.__class__.__name__))

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...
