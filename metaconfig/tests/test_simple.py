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
