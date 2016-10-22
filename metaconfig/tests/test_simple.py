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

    eq_(int, config.get("integer"))
    eq_(str, config.get("string"))
    eq_(float, config.get("float"))
    eq_(type(None), config.get("null"))
