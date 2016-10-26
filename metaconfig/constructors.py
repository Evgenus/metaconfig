import yaml.nodes

__all__ = [
    'construct_from_mapping',
    'construct_from_sequence',
    'construct_from_string',
    'construct_from_integer',
    'construct_from_any',
    'construct_from_none',
    'construct_from_args_kwargs',
]

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

def construct_from_any(cls, loader, node):
    if isinstance(node, yaml.nodes.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.nodes.SequenceNode):
        value = loader.construct_sequence(node, True)
    elif isinstance(node, yaml.nodes.MappingNode):
        value = loader.construct_mapping(node, True)
    return cls(value)

def construct_from_none(cls, loader, node):
    assert loader.construct_yaml_null(node) is None
    return cls()

def construct_from_args_kwargs(cls, loader, node):
    mapping = loader.construct_mapping(node, True)
    args = mapping.pop("=", ())
    return cls(*args, **mapping)
