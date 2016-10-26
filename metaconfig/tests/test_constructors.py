from nose.tools import *
from io import StringIO
from textwrap import dedent

from metaconfig import Config

# construct_from_mapping
# construct_from_sequence
# construct_from_string
# construct_from_integer
# construct_from_any
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