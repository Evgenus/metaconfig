from nose.tools import *
from io import StringIO
from textwrap import dedent

from metaconfig import Config

def test_declare_empty():

    source = """
    --- !declare {}
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

def test_declare_resolve():

    source = """
    --- !declare
    type:
        type: !resolve builtins.type
        load: !resolve metaconfig.construct_from_sequence
    ...

    --- !let
    integer: !type 
        - 0
    string: !type 
        - ""
    float: !type 
        - 1.0
    "null": !type
        - ~
    ...
    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    assert_is(int, config.get("integer"))
    assert_is(str, config.get("string"))
    assert_is(float, config.get("float"))
    assert_is(type(None), config.get("null"))

def test_declare_get():

    source = """
    --- !declare
    type:
        type: !resolve builtins.type
        load: !resolve metaconfig.construct_from_sequence
    tuple:
        type: !resolve builtins.tuple
        load: !resolve metaconfig.construct_from_value
    ...

    --- !let
    MyInteger: !type 
        - MyInteger
        - !tuple
            - !resolve builtins.int
        -
            one: 1
    ...

    --- !declare
    MyInteger:
        type: !get MyInteger
        load: !resolve metaconfig.construct_from_integer
    ...

    --- !let
    value: !MyInteger 10
    ...

    """

    config = Config()

    with StringIO(dedent(source)) as stream:
        config.load(stream)

    assert_equals(10, config.get("value"))
    assert_is_instance(config.get("value"), int)
    assert_equals(1, config.get("value").one)
