from nose.tools import *
from utils import mock_filesystem
import fs.path
from textwrap import dedent
from pathlib import Path
import yaml

from metaconfig import Config

filesystem = """
simple.yaml: |
    --- !let
    test: ok
    ...
"""

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

def test_self_check():
    fs = mock_filesystem(yaml.load(filesystem))
    ok_(fs.exists("simple.yaml"))
    ok_(fs.exists("/simple.yaml"))
    with fs.open("simple.yaml") as stream:
        ok_(len(stream.read()) > 0)

def test_simple():
    fs = mock_filesystem(yaml.load(filesystem))
    config = MockedFSConfig(fs)
    config.load("simple.yaml")
    ok_(config.get("test"))
