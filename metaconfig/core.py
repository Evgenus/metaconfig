from functools import reduce, partial
from collections import UserDict
from pathlib import Path

import yaml
from zope.dottedname.resolve import resolve

__all__ = [
    'construct_from_mapping',
    'construct_from_sequence',
    'construct_from_string',
    'construct_from_integer',
    'resolve_builtin',
    'Config',
]

if yaml.__with_libyaml__:
    class Loader(yaml.CLoader): pass
else:
    class Loader(yaml.Loader): pass

def construct_from_mapping(cls, loader, node):
    mapping = loader.construct_mapping(node, True)
    return cls(**mapping)

def construct_from_sequence(cls, loader, node):
    sequence = loader.construct_sequence(node, True)
    return cls(*sequence)

def construct_from_string(cls, loader, node):
    scalar = str(loader.construct_scalar(node))
    return cls(scalar)

def construct_from_integer(cls, loader, node):
    scalar = int(loader.construct_scalar(node))
    return cls(scalar)

def resolve_builtin(loader, node):
    scalar = loader.construct_scalar(node)
    return resolve(scalar)
Loader.add_constructor("!resolve", resolve_builtin)

def _create_core(frame):
    class TypesTable(object):
        def __init__(self, **types):
            for name, declaration in types.items():
                self.register(name, **declaration)

        @property
        def loader(self):
            return frame.loader

        def register(self, _name, type, load):
            loader = partial(load, type)
            if _name.startswith("tag:"):
                tag = _name
            else:
                tag = "!" + _name
            self.loader.add_constructor(tag, loader)

    frame.loader.add_constructor("!TypesTable", partial(construct_from_mapping, TypesTable))
    frame.loader.add_constructor("!get_dependency", partial(construct_from_string, frame.get))
    frame.loader.add_constructor("!add_dependencies", partial(construct_from_mapping, frame.add))

class ConfigStackFrame(object):
    def __init__(self, filepath, back):
        self._filepath = filepath
        self._back = back
        self._dependencies = {}
        class FrameLoader(Loader): pass
        self._loader = FrameLoader
        _create_core(self)

    @property
    def dirpath(self):
        if self._filepath is not None:
            return Path(self._filepath).parent
        else:
            return Path.cwd()

    def get(self, name): 
        return self._dependencies[name]

    def add(self, **deps): 
        self._dependencies.update(deps)

    def grab(self, frame):
        for name, con in frame._loader.yaml_constructors.items():
            self._loader.add_constructor(name, con)
        self._dependencies.update(frame._dependencies)

    @property
    def loader(self):
        return self._loader

class Config(object):
    def __init__(self):
        self._files = []
        self._root = ConfigStackFrame(None, None)
        self._head = self._root
        loader  = self._root.loader
        loader.add_constructor("!load_config", partial(construct_from_string, self.load))

    def peek_frame(self):
        return self._head

    def push_frame(self, frame):
        self._head = frame

    def pop_frame(self):
        top = self._head
        self._head = self._head._back
        self._head.grab(top)
        return top

    def get_path(self, relative):
        return self.peek_frame().dirpath / relative

    def push_file(self, relative):
        self._files.append(relative)
        frame = ConfigStackFrame(relative, self._head)
        self.push_frame(frame)

    def pop_file(self):
        return self.pop_frame().dirpath

    def get_dependency(self, name): 
        return self.peek_frame().get(name)

    def extra_files(self):
        return self._files

    def log(self, text):
        print(text)

    def load(self, filename_or_stream):
        if isinstance(filename_or_stream, str):
            path = self.get_path(filename_or_stream)
            filename = str(path)
            stream = path.open("rt", encoding="utf-8")
        else:
            stream = filename_or_stream
            if hasattr(stream, "name"):
                filename = stream.name
            else:
                filename = None
        
        self.push_file(filename)
        loader = self.peek_frame().loader
        self.log("Loading config: {}".format(filename))
        data = list(yaml.load_all(stream, Loader=loader))
        self.pop_file()
        return data
