import unittest
from utils import mock_filesystem
import fs.path
from textwrap import dedent
from pathlib import Path
import yaml
import inspect

from metaconfig import Config

class MockedFSConfig(Config):
    def __init__(self, fs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fs = fs

    @property
    def fs(self):
        return self._fs

    @property
    def root(self):
        return Path("/")

    def open_file(self, path):
        path = fs.path.ospath(str(path))
        return self.fs.open(path, "rt", encoding="utf-8")

    def get_path(self, relative):
        frame = self.peek_frame()
        path = frame.dirpath.joinpath(relative)
        return Path(fs.path.abspath(str(path)))

class DocFileSystemMixin:
    def setUp(self):
        self.fs = mock_filesystem(yaml.load(inspect.getdoc(self)))

class TestSimple(DocFileSystemMixin, unittest.TestCase):
    """
    simple.yaml: |
        --- !let
        test: ok
        ...
    multifile1.yaml: |
        --- !load simple.yaml
    """
    def test_self_check(self):
        self.assertTrue(self.fs.exists("simple.yaml"))
        self.assertTrue(self.fs.exists("/simple.yaml"))
        with self.fs.open("simple.yaml") as stream:
            self.assertGreater(len(stream.read()), 0)

    def test_simple(self):
        config = MockedFSConfig(self.fs)
        config.load("simple.yaml")
        self.assertTrue(config.get("test"))

    def test_multifile1(self):
        config = MockedFSConfig(self.fs)
        config.load("multifile1.yaml")
        self.assertTrue(config.get("test"))

class TestMultiple(DocFileSystemMixin, unittest.TestCase):
    """
    dependency1.yaml: |
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
            - {}
        ...

        --- !declare
        MyInteger:
            type: !get MyInteger
            load: !resolve metaconfig.construct_from_integer
        ...

        --- !let
        value: !MyInteger 111
        ...
    dependency2.yaml: |
        --- !load dependency1.yaml

        --- !let
        value1: !MyInteger 222
        other1: !get value
        ...
    dependency3.yaml: |
        --- !load dependency1.yaml

        --- !let
        value2: !MyInteger 333
        other2: !get value
        ...
    multifile2.yaml: |
        --- !load dependency2.yaml
        --- !load dependency3.yaml
    """

    def test_multifile2(self):
        config = MockedFSConfig(self.fs)
        config.load("multifile2.yaml")
        self.assertIs(config.get("other1"), config.get("other2"))
        self.assertIs(type(config.get("value1")), type(config.get("value2")))
