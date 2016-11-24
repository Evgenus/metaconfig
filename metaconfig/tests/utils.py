from fs import memoryfs 
from collections import abc

def identity(*args, **kwargs):
    return args, kwargs

def mock_filesystem(declaration):
    assert isinstance(declaration, abc.Mapping)
    def fill_directory(items, directory):
        for name, content in items.items():
            assert type(name) is str

            if isinstance(content, str):
                directory.setcontents(name, content)
            elif isinstance(content, dict):
                directory.makedir(name)
                fill_directory(contents, directory.opendir(name))
            else:
                assert False
    fs = memoryfs.MemoryFS()
    fill_directory(declaration, fs.opendir('/'))
    return fs

