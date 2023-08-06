# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>
import abc
import dataclasses as dc
import functools as ft
import itertools as it
import traceback
import types
import typing as t
from inspect import isclass

import attr
import typing_inspect as ti

NoneType = type(None)


class Missing:
    def __bool__(self):
        return False

    def __repr__(self):
        return f"{__name__}.missing"


missing = Missing()


class IsDataclass(t.Protocol):
    __dataclass_fields__: t.Dict


class IsAttrs(t.Protocol):
    __attrs_attrs__: t.Tuple


Key = t.Union[str, int]
Path = t.Tuple[Key, ...]
MappingType = t.Type["Mapping"]
IndexableType = t.Type["Indexable"]
KeyValues = t.Iterable[t.Tuple[Key, "Item"]]
T = t.TypeVar("T", t.Mapping, IsDataclass, IsAttrs)


class Unmappable(Exception):
    ...


@dc.dataclass(frozen=True)
class Item:
    value: t.Any = missing
    key: t.Union[Key, Missing] = missing
    type: t.Optional[t.Type] = None

    def __post_init__(self):
        # auto update type
        if self.type is None and not self.value_is_missing:
            object.__setattr__(self, "type", type(self.value))

    def __bool__(self):
        # all defined items have a type
        return self.type is not None

    def __eq__(self, other):
        return self.value == other

    def replace(self, **kwargs):
        return dc.replace(self, **kwargs)

    @ft.cached_property
    def value_is_missing(self):
        return self.value is missing


@dc.dataclass
class Indexable(t.Generic[T], metaclass=abc.ABCMeta):
    value: T
    generic_origin: t.Optional[t.Type] = None
    is_type: bool = False

    def __post_init__(self):
        self.is_type = isinstance(self.value, type)
        if ti.is_generic_type(self.value):
            self.generic_origin = ti.get_origin(self.value)

        # refuse instantiation on failing test
        if not self.test(self.value):
            raise Unmappable(self.value)

    @classmethod
    @abc.abstractclassmethod
    def test(cls, value: t.Any) -> bool:
        ...  # pragma: no cover

    @abc.abstractmethod
    def value_pairs(self, other: "Indexable") -> t.Iterator[KeyValues]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def create_from_key_values(self, kv):
        ...  # pragma: no cover


@dc.dataclass
class Mapping(Indexable):
    @classmethod
    def test(cls, value: t.Any) -> bool:
        return isinstance(value, t.Mapping)

    def keys(self) -> t.Set[Key]:
        return set(self.value.keys())

    def __getitem__(self, key):
        value = self.value[key]
        return Item(value=value, key=key, type=type(value))

    def value_pairs(self, other: "Mapping") -> t.Iterator[KeyValues]:
        a_keys, b_keys = self.keys(), other.keys()
        old, common, new = a_keys - b_keys, a_keys & b_keys, b_keys - a_keys
        return (
            (k, v)
            for values in (
                ((k, (self[k], Item(key=k))) for k in old),
                ((k, (self[k], other[k])) for k in common),
                ((k, (Item(key=k), other[k])) for k in new),
            )
            for k, v in values
            # we skip missing values
            # dataclasses and attrs must implement a default
            if v is not missing
        )

    def create_from_key_values(self, kv):
        return dict(kv)


@dc.dataclass
class List(Indexable):
    @classmethod
    def test(cls, value: t.Any) -> bool:
        origin = ti.get_origin(value)
        if origin:
            return issubclass(origin, t.List)

        return isinstance(value, t.List)

    def __iter__(self):
        for i, value in enumerate(self.value):
            yield Item(value=value, key=i, type=type(value))

    def value_pairs(self, other: "List") -> t.Iterator[KeyValues]:
        # mock value for generic List
        if self.generic_origin:
            (item_value,) = ti.get_args(self.value)
            value = list(
                Item(value=item_value, key=i, type=item_value)
                for i in range(len(other.value))
            )
        else:
            value = list(Item(value=v, key=i) for i, v in enumerate(self.value))

        def make_missing_item(i, ab):
            a, b = ab
            return i, (
                Item(key=i) if a is missing else a,
                Item(key=i) if b is missing else b,
            )

        return it.starmap(
            make_missing_item,
            enumerate(it.zip_longest(value, other, fillvalue=missing)),
        )

    def create_from_key_values(self, kv):
        return list(v for _, v in kv)


class Field(Item):
    field: t.Union[dc.Field, attr.Attribute, NoneType]


@dc.dataclass(frozen=True)
class DataclassField(Field):
    field: t.Optional[dc.Field] = None


@dc.dataclass(frozen=True)
class AttrsField(Field):
    field: t.Optional[attr.Attribute] = None


class WithFields(Mapping, metaclass=abc.ABCMeta):
    fields: t.Dict[str, t.Union[dc.Field, attr.Attribute]] = dc.field(
        default_factory=dict
    )

    @abc.abstractclassmethod
    def get_fields(cls, value):
        ...  # pragma: no cover

    def __post_init__(self):
        super().__post_init__()
        self.fields.update(self.get_fields(self.value))

    def keys(self):
        return set(self.fields.keys())

    def create_from_key_values(self, kv):
        cls = self.value if self.is_type else type(self.value)
        # omit unknown keys and missing value to take field default
        kwargs = {k: v for k, v in kv if v is not missing and k in self.fields}
        try:
            return cls(**kwargs)
        except TypeError as ex:
            raise Unmappable(ex, cls, kwargs)


@dc.dataclass
class Dataclass(WithFields):
    fields: t.Dict[str, dc.Field] = dc.field(default_factory=dict)

    @classmethod
    def test(cls, value) -> bool:
        return dc.is_dataclass(value)

    @classmethod
    def get_fields(cls, value):
        return ((f.name, f) for f in dc.fields(value))

    def __getitem__(self, key) -> DataclassField:
        field = self.fields[key]
        return DataclassField(
            # if we deal with a type, value contains it
            value=missing if self.is_type else getattr(self.value, key),
            key=key,
            type=field.type,
            field=field,
        )


@dc.dataclass
class Attrs(WithFields):
    fields: t.Dict[str, attr.Attribute] = dc.field(default_factory=dict)

    @classmethod
    def test(cls, value) -> bool:
        return attr.has(value)

    @classmethod
    def get_fields(cls, value):
        if not isclass(value):
            value = type(value)
        return ((f.name, f) for f in attr.fields(value))

    def __getitem__(self, key) -> AttrsField:
        field = self.fields[key]
        return AttrsField(
            # if we deal with a type, value contains it
            value=missing if self.is_type else getattr(self.value, key),
            key=key,
            type=field.type,
            field=field,
        )


@dc.dataclass
class Merger:
    func: t.Callable
    mapper: t.Tuple[IndexableType, ...]

    def map(self, value: t.Any) -> Mapping:
        """:raises: Unmappable if no mapper test passes."""
        errors = {}
        for mapper in self.mapper:
            try:
                mapped = mapper(value)
                return mapped
            except Exception as ex:
                errors[mapper] = (ex, traceback.format_exc())
        raise Unmappable(value, errors)

    @t.overload
    def __call__(self, a: t.List, b: t.Any, /, **kv: t.Any) -> t.List:
        ...  # pragma: no cover

    @t.overload
    def __call__(self, a: t.Mapping, b: t.Any, /, **kv: t.Any) -> t.Mapping:
        ...  # pragma: no cover

    @t.overload
    def __call__(self, a: t.Type[T], b: t.Any, /, **kv: t.Any) -> T:
        ...  # pragma: no cover

    @t.overload
    def __call__(self, a: T, b: t.Any, /, **kv: t.Any) -> T:
        ...  # pragma: no cover

    def __call__(self, a, b, /, **kv: t.Any) -> t.Any:
        # create mapper
        ma, mb = self.map(a), self.map(b)
        return self.merge(ma, mb, **kv)

    def merge(
        self,
        a: Indexable[T],
        b: Indexable,
        path: Path = (),
        /,
        factory: t.Optional[t.Callable] = None,
        **kv: t.Any,
    ) -> T:
        def descent():
            for k, (a_item, b_item) in a.value_pairs(b):
                assert isinstance(a_item, Item), a_item
                assert isinstance(b_item, Item), b_item
                # inspect item a for union type
                if a_item.type is not missing and ti.is_union_type(a_item.type):
                    # patch item type
                    typed_a_items = (
                        a_item.replace(type=type)
                        for type in ti.get_args(a_item.type, evaluate=True)
                    )
                else:
                    typed_a_items = (a_item,)

                for typed_a_item in typed_a_items:
                    try:
                        ma_item, mb_item = self.map(
                            typed_a_item.value or typed_a_item.type
                        ), self.map(b_item.value)
                        value = self.merge(
                            ma_item, mb_item, path + (k,), factory=factory, **kv
                        )
                    except Unmappable:
                        value = self.func(typed_a_item, b_item, path + (k,), **kv)

                    if value is not missing:
                        yield k, value
                        break

        merged = (factory and factory(a, b, path, **kv) or a.create_from_key_values)(
            descent()
        )
        return merged


def ion(*mapper: IndexableType) -> t.Callable:
    """Create a new merger subclass taking the decorated function as the merge tool."""

    def wrapper(func: t.Callable) -> Merger:
        return create_merger(func, mapper=mapper)

    return wrapper


def create_merger(
    func: t.Callable, /, mapper: t.Tuple[IndexableType, ...] = ()
) -> Merger:
    """Create a new Merger subclass, to have a proper doc string and annotations."""
    f = Merger.__call__
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = ft.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    g.__doc__ = func.__doc__
    g.__annotations__ = func.__annotations__

    NewMerger = dc.make_dataclass(
        func.__name__,
        [(f.name, f.type, f) for f in dc.fields(Merger)],
        bases=(Merger,),
        namespace={"__call__": g},
    )
    return NewMerger(func, mapper=mapper)


@ion(Mapping, List, Dataclass, Attrs)
def merge(
    a: Item,
    b: Item,
    path: Path = (),
    /,
    override: t.Optional[t.Callable] = None,
    nothing_new: bool = False,
    remove_old: bool = False,
    keep_type: bool = False,
    **kv: t.Any,
) -> t.Any:
    """Merge two mappable objects into one.

    :param a: object a
    :param b: object b
    :param path: the path of keys
    :param override: a function to override b
    :param nothing_new: skip new keys if they ar not in a
    :param remove_old: skip old keys if they are not in b
    :param keep_type: b must have similar type as a
    """
    if callable(override):
        b = override(a, b, path, **kv)
    value = (
        a.value
        if (nothing_new and not a)
        else b.value
        if (not b and remove_old)
        or (b and (not keep_type or a and issubclass(b.type, a.type)))
        else a.value
    )
    return value
