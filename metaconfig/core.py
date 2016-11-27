from functools import reduce, partial
from collections import OrderedDict
from pathlib import Path
from io import IOBase

import yaml
from zope.dottedname.resolve import resolve

from .constructors import (
    construct_from_mapping,
    construct_from_string
    )

__all__ = [
    'Config',
]

if yaml.__with_libyaml__:
    BaseLoader = yaml.CLoader
else:
    BaseLoader = yaml.Loader

class Loader(BaseLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

def _create_core(frame, names):
    class TypesTable(object):
        _frame = frame
        def __init__(self, **types):
            for name, declaration in types.items():
                self.register(name, **declaration)

        def register(self, _name, type, load):
            loader = partial(load, type)
            if _name.startswith("tag:"):
                tag = _name
            else:
                tag = "!" + _name
            self._frame.loader.add_constructor(tag, loader)

    frame.loader.add_constructor("!" + names["declare"], partial(construct_from_mapping, TypesTable))
    frame.loader.add_constructor("!" + names["get"], partial(construct_from_string, frame.get))
    frame.loader.add_constructor("!" + names["let"], partial(construct_from_mapping, frame.add))
    frame.loader.add_constructor("!" + names["resolve"], partial(construct_from_string, frame.resolve))

class ConfigStackFrame(object):
    def __init__(self, filepath, root, names):
        self._filepath = None if filepath is None else Path(filepath)
        self._root = Path(root)
        self._dependencies = {}
        self._resolved = {}
        self._data = None
        self._empty_names = set()
        class FrameLoader(Loader): pass
        self._loader = FrameLoader
        _create_core(self, names=names)

    @property
    def filename(self):
        return self._filepath

    @property
    def dirpath(self):
        return self._root

    def get(self, name): 
        return self._dependencies[name]

    def add(self, **deps): 
        self._dependencies.update(deps)

    def grab(self, frame):
        for name, con in frame._loader.yaml_constructors.items():
            if name in self._empty_names: continue
            self._loader.add_constructor(name, con)
        self._dependencies.update(frame._dependencies)

    def resolve(self, dotted):
        if dotted not in self._resolved:
            self._resolved[dotted] = resolve(dotted)
        return self._resolved[dotted]

    @property
    def loader(self):
        return self._loader

    @property
    def data(self):
        return self._data

    def load(self, stream):
        self._empty_names = set(self._loader.yaml_constructors)
        self._data = list(yaml.load_all(stream, Loader=self._loader))

DEFAULT_NAMES = {
    "declare": "declare",
    "get": "get",
    "let": "let",
    "resolve": "resolve",
    "load": "load"
}

class Config(object):
    def __init__(self, names=None):
        names_mix = dict(DEFAULT_NAMES)
        if names is not None:
            names_mix.update(names)
        self._files = []
        self._frames = {}
        self._names = names_mix
        self._results = {}
        self._stack = [ConfigStackFrame(None, self.root, self._names)]

    def peek_frame(self):
        return self._stack[-1]

    @property
    def root(self):
        return Path.cwd()

    def push_frame(self, frame):
        self._stack.append(frame)

    def pop_frame(self):
        top = self._stack.pop()
        self._stack[-1].grab(top)
        return top

    def get_frame(self, filename):
        if filename is None:
            return None
        return self._frames.get(Path(filename))

    def get_path(self, relative):
        frame = self.peek_frame()
        return frame.dirpath.joinpath(relative).resolve()

    def open_file(self, path):
        return Path(path).open("rt", encoding="utf-8")

    def push_file(self, relative):
        path = None if relative is None else Path(relative)
        self._files.append(path)
        root = self.root if path is None else path.parent
        frame = ConfigStackFrame(path, root, self._names)
        self._frames[path] = frame
        self.push_frame(frame)

    def pop_file(self):
        return self.pop_frame().dirpath

    def get(self, name): 
        return self.peek_frame().get(name)

    @property
    def extra_files(self):
        return self._files

    def log(self, text):
        print(text)

    def _load_config(self, stream, filename):
        frame = self.get_frame(filename)
        if frame is not None:
            self.push_frame(frame)
            self.pop_frame()            
        else:
            self.push_file(filename)
            frame = self.peek_frame()
            frame.loader.add_constructor("!" + self._names["load"], partial(construct_from_string, self.load))
            self.log("Loading config: {}".format(filename))
            frame.load(stream)
            self.pop_file()
        return frame.data

    def load(self, filename_or_stream):
        filename = None
        if isinstance(filename_or_stream, (str, Path)):
            path = self.get_path(filename_or_stream)
            filename = str(path)
            with self.open_file(path) as stream:
                return self._load_config(stream, filename)
        elif isinstance(filename_or_stream, IOBase):
            if hasattr(filename_or_stream, "name"):
                filename = filename_or_stream.name
            return self._load_config(filename_or_stream, filename)
        else:
            raise ValueError("Invalid parameter {0}".format(filename_or_stream))
