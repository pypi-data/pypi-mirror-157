from typing import List, Dict, Iterator, TypedDict, Union

from .types import MappingType, OperatorType, FormatType, FieldType, ObjectType


class ResourceField:

    def __init__(self, name: str, field_type: FieldType, format_type: FormatType):
        self._name = name
        self._field_type: FieldType = field_type
        self._format_type: FormatType = format_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def field_type(self) -> FieldType:
        return self._field_type

    @property
    def format_type(self) -> FormatType:
        return self._format_type

    @property
    def object(self) -> dict:
        return {}


class ResourceObjectField(ResourceField):

    def __init__(self, name: str, field_type: FieldType, format_type: FormatType):
        super().__init__(name, field_type, format_type)

    @property
    def object(self) -> dict:
        return {
            'name': self._name,
            'field': self._field_type.value,
            'format': self._format_type.value,
        }


class ResourceRelationField(ResourceField):

    def __init__(self, name: str, relation_id: str,
                 field_type: FieldType, format_type: FormatType,
                 mapping_type: MappingType):
        super().__init__(name, field_type, format_type)
        self._relation_id: str = relation_id
        self._mapping_type: MappingType = mapping_type

    @property
    def relation_id(self) -> str:
        return self._relation_id

    @property
    def mapping_type(self) -> MappingType:
        return self._mapping_type

    @property
    def object(self) -> dict:
        return {
            'name': self._name,
            'relation': self.relation_id,
            'field': self._field_type.value,
            'format': self._format_type.value,
            'mapping': self.mapping_type.type.value,
            'mappingParams': self.mapping_type.params,
        }


class ResourceSchema:

    def __init__(self):
        self.__fields: Dict[str, ResourceField] = {}

    def add_object_field(self, name: str, field_type: FieldType, format_type: FormatType):
        self.__fields[name] = ResourceObjectField(name, field_type, format_type)
        return self

    def add_relation_field(self, name: str, relation_id: str,
                           field_type: FieldType, format_type: FormatType, mapping_type: MappingType):
        self.__fields[name] = ResourceRelationField(name, relation_id, field_type, format_type, mapping_type)
        return self

    def get_field(self, name: str) -> Union[ResourceField, None]:
        return self.__fields.get(name)

    @property
    def fields(self) -> List[ResourceField]:
        return list(self.__fields.values())

    @property
    def object(self):
        return {
            'fields': list([field.object for field in self.__fields.values()]),
        }

    def copy(self):
        cpy = ResourceSchema()
        cpy.__fields = self.__fields.copy()
        return cpy

    def __add__(self, other):
        new_schema = ResourceSchema()
        for k in other.__fields:
            new_schema.__fields[k] = other.__fields[k]
        for k in self.__fields:
            new_schema.__fields[k] = self.__fields[k]
        return new_schema

    def __repr__(self):
        return f'Schema {self.__fields}'


class ResourceFilter:
    class E(TypedDict):
        name: str
        value: any
        operator: str

    def __init__(self):
        self._filters: List[ResourceFilter.E] = []

    def add_filter(self, name: str, value, operator_type: OperatorType) -> 'ResourceFilter':
        self._filters.append({
            'name': name,
            'value': value,
            'operator': operator_type.value,
        })
        return self

    @property
    def object(self):
        return self._filters

    def __len__(self):
        return len(self._filters)

    def __getitem__(self, item) -> E:
        return self._filters[item]

    def __iter__(self) -> Iterator[E]:
        return (i for i in self._filters)

    def __reversed__(self) -> Iterator[E]:
        return (i for i in reversed(self._filters))

    def __copy__(self):
        cpy = ResourceFilter()
        cpy._filters = self._filters.copy()
        return cpy


class ResourceOrder:
    class E(TypedDict):
        name: str
        ascending: bool

    def __init__(self):
        self._orders: List[ResourceOrder.E] = []

    def add_order(self, name: str, ascending=True) -> 'ResourceOrder':
        self._orders.append({
            'name': name,
            'ascending': ascending,
        })
        return self

    @property
    def object(self):
        return self._orders

    def __len__(self):
        return len(self._orders)

    def __getitem__(self, item) -> E:
        return self._orders[item]

    def __iter__(self) -> Iterator[E]:
        return (i for i in self._orders)

    def __reversed__(self) -> Iterator[E]:
        return (i for i in reversed(self._orders))

    def __copy__(self):
        cpy = ResourceOrder()
        cpy._orders = self._orders.copy()
        return cpy


class Resource:

    def __init__(self, object_id: str, schema: ResourceSchema, object_type: ObjectType):
        self._object_id = object_id
        self._schema = schema
        self._object_type = object_type

    @property
    def object_id(self) -> str:
        return self._object_id

    @property
    def schema(self) -> ResourceSchema:
        return self._schema

    @property
    def object_type(self) -> ObjectType:
        return self._object_type

    def to_request(self):
        pass


class ResourceInstance(Resource):

    def __init__(self, object_id: str, schema: ResourceSchema, object_type: ObjectType):
        super().__init__(object_id, schema, object_type)

    def to_request(self):
        return {
            'objectId': self._object_id,
            'schema': self._schema.object,
            'object': self._object_type.value,
        }


class ResourceList(Resource):

    def __init__(self, object_id: str,
                 schema: ResourceSchema,
                 object_type: ObjectType):
        super().__init__(object_id, schema, object_type)
        self._filter: ResourceFilter = ResourceFilter()
        self._order: ResourceOrder = ResourceOrder()
        self._offset: Union[int, None] = None
        self._limit: Union[int, None] = None

    @property
    def order(self) -> ResourceOrder:
        return self._order

    def set_order(self, order: ResourceOrder) -> 'ResourceList':
        self._order = order
        return self

    def add_order(self, name: str, ascending=True) -> 'ResourceList':
        if self._schema.get_field(name) is not None:
            self._order.add_order(name, ascending)
        return self

    @property
    def filter(self) -> ResourceFilter:
        return self._filter

    def set_filter(self, filter: ResourceFilter) -> 'ResourceList':
        self._filter = filter
        return self

    def add_filter(self, name, value, operator_type=OperatorType.EQUALS) -> 'ResourceList':
        if self._schema.get_field(name) is not None:
            self._filter.add_filter(name, value, operator_type)
        return self

    @property
    def offset(self) -> Union[int, None]:
        return self._offset

    def set_offset(self, offset) -> 'ResourceList':
        self._offset = offset
        return self

    @property
    def limit(self) -> Union[int, None]:
        return self._limit

    def set_limit(self, limit) -> 'ResourceList':
        self._limit = limit
        return self

    def to_request(self):
        req = {
            'objectId': self._object_id,
            'schema': self._schema.object,
            'object': self._object_type.value,
        }
        if self._filter is not None:
            req['filter'] = self._filter.object
        if self._order is not None:
            req['order'] = self._order.object
        if self._offset is not None:
            req['offset'] = self._offset
        if self._limit is not None:
            req['limit'] = self._limit
        return req
