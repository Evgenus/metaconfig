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

