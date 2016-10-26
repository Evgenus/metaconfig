from nose.tools import *
from io import StringIO
from textwrap import dedent

from metaconfig import Config

# construct_from_none
# construct_from_args_kwargs

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
        b: 2
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    value = config.get("value")

    assert_tuple_equal(value[0], ())
    assert_dict_equal(value[1], {"a": 1, "b": 2})

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
    assert_tuple_equal(value2[0], (1,))
    assert_dict_equal(value2[1], {})
