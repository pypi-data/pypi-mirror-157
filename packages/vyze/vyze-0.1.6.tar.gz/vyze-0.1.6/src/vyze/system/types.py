from enum import Enum
from typing import Dict, Union
from ..util import JSONVal


class FieldType(Enum):
    ID = 'id'  # Requires format_type = HEX or BASE64
    NAME = 'name'  # Requires format_type = STRING
    SIZE = 'size'  # Requires format_type = INTEGER
    CREATED = 'created'  # Requires format_type = INTEGER
    USER = 'user'  # Requires format_type = HEX or BASE64
    DATA = 'data'


class FormatType(Enum):
    RAW = 'raw'
    HEX = 'hex'
    BASE64 = 'base64'
    STRING = 'string'
    INTEGER = 'integer'
    FLOAT = 'float'
    BOOLEAN = 'boolean'


class ObjectType(Enum):
    SPECIALS = 'specials'
    INSTANCE = 'instance'


class ValueType(Enum):
    PRIMITIVE = 'primitive'
    LIST = 'list'
    SUMMARY = 'summary'


class MappingType:

    def __init__(self, **kwargs):
        self._value_type: Union[ValueType, None] = None
        self._value_params: Dict[str, JSONVal] = {}
        for k in kwargs:
            self._value_params[k] = kwargs[k]

    @property
    def type(self) -> Union[ValueType, None]:
        return self._value_type

    @property
    def params(self) -> Dict[str, JSONVal]:
        return dict(self._value_params)

    def set(self, key: str, value: JSONVal):
        self._value_params[key] = value
        return self

    def set_params(self, params: Dict[str, JSONVal]):
        params['mapping'] = self._value_type.value
        for k in self._value_params:
            params[f'mp_{k}'] = self._value_params[k]

    def __setitem__(self, key, value):
        self.set(key, value)


class PrimitiveMapping(MappingType):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._value_type = ValueType.PRIMITIVE


class ListMapping(MappingType):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._value_type = ValueType.LIST


class OperatorType(Enum):
    EQUALS = 'eq'
    NOT_EQUALS = 'ne'
    GREATER = 'gt'
    LESS = 'lt'
    GREATER_OR_EQUAL = 'ge'
    LESS_OR_EQUAL = 'le'


class ReturnType(Enum):
    """
    Specifies how related object IDs and their relation IDs and keys should be formatted.
    """

    OBJECTS = 'objects'
    """
    Object IDs.

    Example: ``["<object ID>", ...]``
    """

    RELATIONS = 'relations'
    """
    Relation IDs.

    Example: ``["<relation ID>", ...]``
    """

    PAIRS = 'pairs'
    """
    Pairs of relation ID and object ID.

    Example: ``[["<relation ID>", "<object ID>"], ...]``
    """

    MAP = 'map'
    """
    Map with relation IDs as keys and object IDs as values.

    Example: ``{"<relation ID>": "<object ID>", ...}``
    """

    KEYED_OBJECT = 'keyed_objects'
    """
    Relation keys and object IDs.

    Example: ``[[<relation key>, "<object ID>"], ...]``
    """

    KEYED_RELATIONS = 'keyed_relations'
    """
    Relation keys and IDs.

    Example: ``[[<relation key>, "<relation ID>"], ...]``
    """

    KEYED_PAIRS = 'keyed_pairs'
    """
    Relation keys, relation IDs and object IDs.

    Example: ``[[<relation key>, "<relation ID>", "<object ID>"], ...]``
    """
