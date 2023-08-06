dict8
=====

features
--------

- No boilerplate: just a, b, path and some code.
- Enables you to define a specific merge behavior for every part of the tree.
- Merge into datclasses or attrs.


internal
--------

The default machinery converts all input data to a Mapper. If **a** and **b** are
mappable, the new, common and old values are taken to a custom function to
decide upon the value precedence. Returning :code:`missing` will omit this key
from the intermediate result. The chosen mapper will decide how to incorporate
the latter.

dict8.merge
-----------

.. code-block:: python

    import dict8


    @dict8.ion(DataclassMapper)
    def merge(
        a: t.Any,
        b: t.Any,
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
        :param keep_type: b must have similar type like a
        """
        ...

custom merger
-------------

.. code-block:: python

    import dict8


    @dict8.ion
    def merge(a, b, path, /, **kv):
        try:
            # try descent into sub mappings
            return merge(
                a,
                b,
                path,
                **kv,
            )
        except dict8.UnMappable:
            # take b else a
            return b if b is not dict8.missing else a


    assert (
        merge(
            {
                1: 2,
                3: {4: 5},
            },
            {
                3: {4: 2, 5: 1},
            },
        )
        == {1: 2, 3: {4: 2, 5: 1}}
    )

merge into attrs and dataclasses
--------------------------------

.. code-block:: python

    import typing as t
    import dataclasses as dc

    import dict8

    @dc.dataclass
    class Foo:
        my_value: int
        some: str = "default"

    @dc.dataclass
    class Bar:
        foo: Foo
        baz: t.Optional[int] = None

    bar = dict8.merge(Bar, {"foo": {"my_value": 123}})

    assert bar == Bar(foo=Foo(my_value=123, some="default"), baz=None)



license
=======

This is public domain.
