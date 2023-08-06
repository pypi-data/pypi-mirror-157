#  -*- coding: utf-8 -*-
"""

Author: Rafael R. L. Benevides
Date: 10/03/2021

"""


from abc import abstractmethod

from jangada.utils import parse_types

from jangada.primitives.atomic import Taggable, Describable, Serialisable, Representable, Ownable, Owner


# ========== ========== ========== ========== ========== ========== Element
class Element(Serialisable, Representable, Taggable, Describable):
    """
    Bases: :class:`Serialisable <jangada.primitives.Serialisable>`,
    :class:`Representable <jangada.primitives.Representable>`,
    :class:`Taggable <jangada.primitives.Taggable>`,
    :class:`Describable <jangada.primitives.Describable>`

    """
    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== OwnableComponent
class OwnableComponent(Element, Ownable):
    """
    Bases: :class:`Element <jangada.primitives.Element>`,
    :class:`Ownable <jangada.primitives.Ownable>`
    """
    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    def _owner_is_about_to_change_callback(self, current_owner, next_owner):
        """
        TODO
        """
        if isinstance(current_owner, Container):
            current_owner._pop(self)

        if isinstance(next_owner, Container):
            next_owner._add(self)

    def _tag_is_about_to_change_callback(self, current_value, next_value):

        if self.owner is not None:

            if next_value is None:
                error = "Objects with owners must have a tag. To set tag=None, you should first set owner=None"
                raise ValueError(error)

            if isinstance(self.owner, Container):
                self.owner._owns[next_value] = self.owner._owns.pop(current_value)

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== OwnerComponent
class OwnerComponent(Element, Owner):
    """
    Bases: :class:`Element <jangada.primitives.Element>`,
    :class:`Owner <jangada.primitives.Owner>`
    """
    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== Component
class Component(OwnableComponent, OwnerComponent):
    """
    Bases: :class:`OwnableComponent <jangada.primitives.OwnableComponent>`,
    :class:`OwnerComponent <jangada.primitives.OwnerComponent>`
    """
    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...


# ========== ========== ========== ========== ========== ========== DummyElement
class DummyElement(Serialisable, Representable):
    pass


# ========== ========== ========== ========== ========== ========== DummyOwnable
class DummyOwnable(DummyElement, Ownable):
    pass


# ========== ========== ========== ========== ========== ========== DummyOnwer
class DummyOwner(DummyElement, Owner):
    pass


# ========== ========== ========== ========== ========== ========== DummyComponent
class DummyComponent(DummyOwnable, DummyOwner):
    pass


# ========== ========== ========== ========== ========== ========== Container
class Container(DummyComponent):
    """
    Bases: :class:`Serialisable <jangada.primitives.Serialisable>`,
    :class:`Representable <jangada.primitives.Representable>`,
    :class:`Owner <jangada.primitives.Owner>`,
    :class:`Ownable <jangada.primitives.Ownable>`
    """

    # ========== ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== ========== special methods
    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

        if not self._owns:
            self._owns = self._get_default_datalist()

    def __contains__(self, item):

        parse_types(item, (self._get_containing_type(), str))

        if isinstance(item, self._get_containing_type()):
            return any(own is item for own in self._owns.values())

        if isinstance(item, str):
            return any(tag is item for tag in self._owns)

    def __getattr__(self, tag):
        try:
            return self._owns[tag]

        except KeyError:
            return super().__getattr__(tag)

    def __setattr__(self, item, value):

        if item in ['_Container__owns', '_owns']:
            super().__setattr__(item, value)

        elif item in self._owns:
            raise AttributeError('attribute {} cannot be set'.format(item))

        else:
            super().__setattr__(item, value)

    def __bool__(self):
        return bool(self.__owns)

    # ========== ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== ========== protected methods
    @staticmethod
    @abstractmethod
    def _get_containing_type():
        raise NotImplementedError()

    @abstractmethod
    def _get_default_datalist(self):
        raise NotImplementedError()

    @abstractmethod
    def _get_default_empty_data(self):
        raise NotImplementedError()

    @classmethod
    def _get_serialisable_property_names(cls):
        return ['_owns']

    def _serialise(self):

        data = super(Container, self)._serialise()

        data['_owns'] = [value for value in data['_owns'].values()]

        return data

    # ---------- ---------- ---------- ---------- ---------- ---------- protected properties
    @property
    def _owns(self):

        try:
            return self.__owns

        except AttributeError:

            self.__owns = {}

            return self.__owns

    @_owns.setter
    def _owns(self, datalist):

        if datalist is None:
            self.__owns = {}

        else:
            parse_types(datalist, list)

            if not issubclass(self._get_containing_type(), OwnableComponent):
                error = "Given containing type {} is not a subclass of OwnableComponent"
                raise TypeError(error.format(self._get_containing_type().__name__))

            self.__owns = {}

            for data in datalist:
                self._get_containing_type()(owner=self, **data)

    def _add(self, obj, overwrite=False):

        parse_types(obj, self._get_containing_type())

        if obj.tag is None:
            error = "Objects with tag = None can not figure in containers"
            raise ValueError(error)

        if obj in self and not overwrite:
            error = "There is already an object with the tag {tag} in this container." \
                    "Please consider remove it first (so you don't lose any data) or set overwrite=True"
            raise AttributeError(error.format(tag=obj.tag))

        self._owns[obj.tag] = obj

    def _pop(self, item):

        parse_types(item, (self._get_containing_type(), str))

        if isinstance(item, self._get_containing_type()):
            obj = self._owns.pop(item.tag)

        if isinstance(item, str):
            obj = self._owns.pop(item)

        # ---------- ---------- ---------- ---------- ---------- ---------- if container gets empty
        if not self._owns and self._get_default_empty_data():
            self._get_containing_type()(owner=self, **self._get_default_empty_data())

        # ---------- ---------- ---------- ---------- ---------- ----------
        return obj

    # ========== ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- ---------- properties
    ...

