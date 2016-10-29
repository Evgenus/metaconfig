from nose.tools import *
from io import StringIO
from textwrap import dedent

from metaconfig import Config

def test_construct_from_mapping():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_mapping
    ...

    --- !let
    value: !func
        a: 1
        c: 2
        b: 3
        d: 4
        f: 5
        e: 6
        h: 7
        g: 8
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value = config.get("value")

    assert_tuple_equal(value[0], ())
    assert_dict_equal(value[1], {"a": 1, "c": 2, "b": 3, "d": 4, "f": 5, "e": 6, "h": 7, "g": 8})

def test_construct_from_sequence():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_sequence
    ...

    --- !let
    value: !func
        - 1
        - 2
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value = config.get("value")

    assert_tuple_equal(value[0], (1, 2))
    assert_dict_equal(value[1], {})

def test_construct_from_string():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_string
    ...

    --- !let
    value1: !func "blabla"
    value2: !func 1
    value3: !func 3.14
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value1 = config.get("value1")
    assert_tuple_equal(value1[0], ("blabla",))
    assert_dict_equal(value1[1], {})

    value2 = config.get("value2")
    assert_tuple_equal(value2[0], ("1",))
    assert_dict_equal(value2[1], {})

    value3 = config.get("value3")
    assert_tuple_equal(value3[0], ("3.14",))
    assert_dict_equal(value3[1], {})

def test_construct_from_integer():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_integer
    ...

    --- !let
    value: !func 1
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value = config.get("value")
    assert_tuple_equal(value[0], (1,))
    assert_dict_equal(value[1], {})

def test_construct_from_none():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_none
    ...

    --- !let
    value: !func ~
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value = config.get("value")
    assert_tuple_equal(value[0], ())
    assert_dict_equal(value[1], {})

def test_construct_from_args_kwargs():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_args_kwargs
    ...

    --- !let
    value1: !func
        =: 
        - 1
        - 2
        a: 1
        b: 2
    value2: !func
        a: 1
        b: 2
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value1 = config.get("value1")
    assert_tuple_equal(value1[0], (1, 2))
    assert_dict_equal(value1[1], {"a": 1, "b": 2})

    value2 = config.get("value2")
    assert_tuple_equal(value2[0], ())
    assert_dict_equal(value2[1], {"a": 1, "b": 2})

def test_construct_from_value():

    source = """
    --- !declare
    func:
        type: !resolve metaconfig.tests.utils.identity
        load: !resolve metaconfig.construct_from_value
    ...

    --- !let
    value1: !func
        a: 1
        c: 2
        b: 3
        d: 4
        f: 5
        e: 6
        h: 7
        g: 8
    value2: !func
        - 1
        - 2
        - 3
    value3: !func "test"
    value4: !func 12345678
    value5: !func 3.141592
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value1 = config.get("value1")[0]
    assert_dict_equal(value1[0], {"a": 1, "c": 2, "b": 3, "d": 4, "f": 5, "e": 6, "h": 7, "g": 8})
    assert_list_equal(list(value1[0].keys()), ["a", "c", "b", "d", "f", "e", "h", "g"])
    value2 = config.get("value2")[0]
    assert_list_equal(value2[0], [1, 2, 3])

    value3 = config.get("value3")[0]
    assert_tuple_equal(value3, ("test",))

    value4 = config.get("value4")[0]
    assert_tuple_equal(value4, (12345678, ))

    value5 = config.get("value5")[0]
    assert_tuple_equal(value5, (3.141592, ))
