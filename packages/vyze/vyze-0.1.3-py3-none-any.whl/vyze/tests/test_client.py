import datetime

import pytest

from src import vyze
from src.vyze import FormatType, FieldType, ResourceSchema, ObjectType, OperatorType, ReturnType, PrimitiveMapping, ListMapping, LayerError, ResourceList, ResourceInstance, read_layer_profile

# system_url = 'http://localhost:9131'
system_url = 'https://api.vyze.io/system'
# service_url = 'http://localhost:9150'
service_url = 'https://api.vyze.io/service'
# profile_str = 'main_read:4924ea:971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e14020004924ea00000000000000000000000062b7a8987ffffffdb0390353641be012edb68c06f3aecc4ccb0d7288;model_extend:492cea:971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e1402000492cea00000000000000000000000062b7a8987ffffffd325ef671b1031846988ea7bcd1eb7eb4bae038e9;main_full:1ffffff:971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e1402001ffffff00000000000000000000000062b7a8987ffffffdd48b8a39c5d512422bdccca56e6e506ee41fadbf'
profile_str = 'main_read:4924ea:bc68786c6142d45a141ecac2314cfc208e31725c558285480a9067c2ce183664004924ea00000000000000000000000062bcb8ac7ffffffe87a15a5993cf50fb7fd30f9d5525babb5e892fb7;model_extend:492cea:bc68786c6142d45a141ecac2314cfc208e31725c558285480a9067c2ce18366400492cea00000000000000000000000062bcb8ac7ffffffedb6b74a3c120760e209ae5420437019da58beae9;main_full:1ffffff:bc68786c6142d45a141ecac2314cfc208e31725c558285480a9067c2ce18366401ffffff00000000000000000000000062bcb8ac7ffffffe1b9fc875e313ca4470fe9dd9d5e4ba12e485deed'
test_universe = 'my_universe_1'


def test_client__get_info():
    client = vyze.SystemClient(url=system_url)

    info = client.get_info()
    assert info['api_version'] == '1.0'
    assert len(info['layers']) == 0

    client.set_layer_profile(read_layer_profile(profile_str))

    info = client.get_info()
    assert len(info['layers']) == 3


def test_client__create_and_get_object():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', access_name='main_full')
    obj = client.get_object(obj.id, access_groups=['main_read'])
    assert obj.name == 'test123'


def test_client__create_and_delete_object():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', access_name='main_full')
    client.delete_object(obj.id)
    with pytest.raises(LayerError):
        obj = client.get_object(obj.id)
    assert obj.name == 'test123'


def test_client__get_and_set_name():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', access_name='main_full')
    client.set_name(obj.id, 'test456')
    assert client.get_name(obj.id) == 'test456'


def test_client__get_and_set_data1():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', 'main_full')

    client.set_data(obj.id, bytes("hello", "utf8"), FormatType.RAW)
    assert str(client.get_data(obj.id, FormatType.RAW), "utf8") == "hello"

    client.set_data(obj.id, "hello2", FormatType.STRING)
    assert client.get_data(obj.id, FormatType.STRING) == "hello2"

    client.set_data(obj.id, 12, FormatType.INTEGER)
    assert client.get_data(obj.id, FormatType.INTEGER) == 12

    client.set_data(obj.id, -12.5, FormatType.FLOAT)
    assert client.get_data(obj.id, FormatType.FLOAT) == -12.5
    assert client.get_data(obj.id, FormatType.HEX) == '00000000000029c0'

    client.set_data(obj.id, 'aa00ff', FormatType.HEX)
    assert client.get_data(obj.id, FormatType.HEX) == 'aa00ff'
    assert client.get_data(obj.id, FormatType.BASE64) == 'qgD/'


def test_client__set_data_chunked():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', 'main_full')

    def make_update(stats):
        def update(offset, length):
            stats['count'] = stats.get('count', 0) + 1
            assert stats.get('offset', 0) <= offset
            assert not stats.get('length') or stats['length'] == length
            stats['offset'] = offset
            stats['length'] = length

        return update

    st = {}
    client.set_data(obj.id, bytes("hello", "utf8"), FormatType.RAW, chunks=2, update=make_update(st))
    assert str(client.get_data(obj.id, FormatType.RAW), "utf8") == 'hello'
    assert st['count'] == 4
    assert st['offset'] == 5
    assert st['length'] == 5


def test_client__get_data_chunked():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', 'main_full')

    def make_update(stats):
        def update(data, offset, length):
            print(data, offset, length)
            stats['data'] = stats.get('data', bytes()) + data
            stats['count'] = stats.get('count', 0) + 1
            assert stats.get('offset', 0) <= offset
            assert not stats.get('length') or stats['length'] == length
            stats['offset'] = offset
            stats['length'] = length

        return update

    st = {}
    client.set_data(obj.id, bytes("hello", "utf8"), FormatType.RAW)
    assert str(client.get_data(obj.id, FormatType.RAW, chunks=2, update=make_update(st)), "utf8") == 'hello'
    assert st['count'] == 3
    assert st['offset'] == 4
    assert st['length'] == 5


def test_client__filtered_resource():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))

    schema = vyze.ResourceSchema()
    schema.add_object_field('id', field_type=FieldType.ID, format_type=FormatType.HEX)
    schema.add_object_field('name', field_type=FieldType.NAME, format_type=FormatType.STRING)

    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))

    obj_name = str(datetime.datetime.now())

    client.create_object(universe.resolve('base.object/'), obj_name, 'main_full')

    resource = ResourceList(universe.resolve('base.object/'), schema, ObjectType.SPECIALS)
    resource.add_filter('name', obj_name, OperatorType.EQUALS)

    assert len(client.get_resource_list(resource)) == 1


def test_client__get_specials_and_abstracts():
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(read_layer_profile(profile_str))
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    obj = client.create_object(universe.resolve('base.object/'), 'test123', 'main_full')

    assert len(client.get_specials(universe.resolve('base.object/'))) > 1
    assert len(client.get_abstracts(obj.id)) == 1


def test_client__get_targets_and_origins():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    rel1 = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel1', 'main_full')
    rel2 = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel2', 'main_full')
    rel1a = client.create_relation(obj1.id, obj2.id, rel1.id, 'rel1a', 'main_full')
    rel2a = client.create_relation(obj1.id, obj2.id, rel2.id, 'rel2a', 'main_full')

    assert len(client.get_targets(obj1.id, return_type=ReturnType.OBJECTS)) == 4
    assert len(client.get_targets(obj1.id, return_type=ReturnType.RELATIONS)) == 4
    assert len(client.get_targets(obj1.id, return_type=ReturnType.PAIRS)) == 4
    assert len(client.get_targets(obj1.id, return_type=ReturnType.MAP)) == 4

    assert len(client.get_origins(obj2.id, return_type=ReturnType.OBJECTS)) == 4
    assert len(client.get_origins(obj2.id, return_type=ReturnType.RELATIONS)) == 4
    assert len(client.get_origins(obj2.id, return_type=ReturnType.PAIRS)) == 4
    assert len(client.get_origins(obj2.id, return_type=ReturnType.MAP)) == 4


def test_client4_keyed():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    rel1 = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel1', 'main_full', key=1,
                                  key_format=FormatType.INTEGER)
    rel2 = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel2', 'main_full', key=2,
                                  key_format=FormatType.INTEGER)
    for i in range(20):
        client.create_relation(obj1.id, obj2.id, rel1.id, f'rel1_{i}', 'main_full', key=3 + i, key_format=FormatType.INTEGER)
        client.create_relation(obj1.id, obj2.id, rel2.id, f'rel2_{i}', 'main_full', key=3 + i, key_format=FormatType.INTEGER)

    vals = client.get_keyed_targets(obj1.id, rel1.id, FormatType.INTEGER, return_type=ReturnType.KEYED_PAIRS, offset=13)
    assert len(vals) == 10
    assert vals[0][0] == 13


def test_client__get_value():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    obj1a = client.create_object(obj1.id, 'obj1a', 'main_full')
    obj2a = client.create_object(obj2.id, 'obj2a', 'main_full')
    rel = client.create_relation(obj1.id, obj2.id, universe['base.object#relation/'], 'rel', 'main_full')
    rel1a = client.create_relation(obj1a.id, obj2a.id, rel.id, 'rel1a', 'main_full')

    client.set_data(obj2a.id, 12, FormatType.INTEGER)
    val = client.get_value(obj1a.id, rel.id, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping())
    assert val == 12


def test_client__set_value():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    obj1a = client.create_object(obj1.id, 'obj1a', 'main_full')
    rel = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel', 'main_full')

    client.put_value(obj1a.id, rel.id, 12, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(change='set'), 'main_full')
    client.put_value(obj1a.id, rel.id, 13, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(change='set'), 'main_full')
    client.put_value(obj1a.id, rel.id, 14, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(change='set'), 'main_full')

    val = client.get_value(obj1a.id, rel.id, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping())
    assert val == 14


def test_client__lookup_data():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')

    obj1a = client.create_object(obj1.id, 'obj1a', 'main_full')
    obj1b = client.create_object(obj1.id, 'obj1b', 'main_full')
    obj1c = client.create_object(obj1.id, 'obj1c', 'main_full')
    obj1d = client.create_object(obj1.id, 'obj1d', 'main_full')
    obj1e = client.create_object(obj1.id, 'obj1e', 'main_full')

    client.set_data(obj1a.id, 12, FormatType.INTEGER)
    client.set_data(obj1b.id, "abc", FormatType.STRING)
    client.set_data(obj1c.id, -12.5, FormatType.FLOAT)
    client.set_data(obj1d.id, True, FormatType.BOOLEAN)
    client.set_data(obj1e.id, bytes('hello', 'UTF8'), FormatType.RAW)

    assert client.lookup_data(obj1.id, 12, FormatType.INTEGER, PrimitiveMapping()) == obj1a.id
    assert obj1b.id in client.lookup_data(obj1.id, "abc", FormatType.STRING, PrimitiveMapping())
    assert client.lookup_data(obj1.id, -12.5, FormatType.FLOAT, PrimitiveMapping()) == obj1c.id
    assert client.lookup_data(obj1.id, True, FormatType.BOOLEAN, PrimitiveMapping()) == obj1d.id
    assert client.lookup_data(obj1.id, bytes('hello', 'UTF8'), FormatType.RAW, PrimitiveMapping()) == obj1e.id


def test_client__lookup_value():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    obj1a = client.create_object(obj1.id, 'obj1a', 'main_full')
    obj1b = client.create_object(obj1.id, 'obj1a', 'main_full')
    rel = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel', 'main_full')
    client.put_value(obj1a.id, rel.id, 12, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(), 'main_full')
    client.put_value(obj1b.id, rel.id, 24, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(), 'main_full')
    client.put_value(obj1b.id, rel.id, 'ababab', FieldType.DATA, FormatType.HEX, PrimitiveMapping(), 'main_full')
    client.put_value(obj1a.id, rel.id, 'ababab', FieldType.DATA, FormatType.HEX, PrimitiveMapping(), 'main_full')

    assert obj1a.id == client.lookup_value(rel.id, 12, FormatType.INTEGER, PrimitiveMapping())
    assert obj1b.id == client.lookup_value(rel.id, 24, FormatType.INTEGER, PrimitiveMapping())
    ids = client.lookup_value(rel.id, 'ababab', FormatType.HEX, ListMapping())
    assert obj1a.id in ids
    assert obj1b.id in ids


def test_client__get_resource__id():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))
    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    client.create_object(obj1.id, 'obj1a', 'main_full')
    client.create_object(obj1.id, 'obj1b', 'main_full')
    client.create_object(obj1.id, 'obj1c', 'main_full')
    resource = ResourceList(obj1.id, ResourceSchema().add_object_field('id', FieldType.ID, FormatType.HEX),
                            ObjectType.SPECIALS)
    vals = client.get_resource_list(resource)
    assert len(vals) == 3


def test_client__get_resource():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    rel = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel', 'main_full')
    obj1a = client.create_object(obj1.id, 'obj1a', 'main_full')
    obj1b = client.create_object(obj1.id, 'obj1b', 'main_full')
    obj1c = client.create_object(obj1.id, 'obj1c', 'main_full')

    client.put_value(obj1a.id, rel.id, 1, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(), 'main_full')
    client.put_value(obj1b.id, rel.id, 2, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(), 'main_full')
    client.put_value(obj1c.id, rel.id, 3, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping(), 'main_full')

    schema = ResourceSchema()
    schema.add_object_field('id', FieldType.ID, FormatType.HEX)
    schema.add_object_field('name', FieldType.NAME, FormatType.STRING)
    schema.add_relation_field('val', rel.id, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping())
    schema.add_relation_field('vals', rel.id, FieldType.DATA, FormatType.INTEGER, ListMapping())

    res = ResourceList(obj1.id, schema, ObjectType.SPECIALS)
    res.add_filter('val', 1, OperatorType.NOT_EQUALS)
    res.add_order('val', False)

    vals = client.get_resource_list(res)
    assert len(vals) == 2
    val = client.get_resource_instance(ResourceInstance(obj1b.id, schema, ObjectType.INSTANCE))
    assert val


def test_client__get_resource__limit():
    client = vyze.SystemClient(url=system_url)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))
    client.set_layer_profile(read_layer_profile(profile_str))

    obj1 = client.create_object(universe.resolve('base.object/'), 'obj1', 'main_full')
    obj2 = client.create_object(universe.resolve('base.object/'), 'obj2', 'main_full')
    rel = client.create_relation(obj1.id, obj2.id, universe.resolve('base.object#relation/'), 'rel', 'main_full')

    schema = ResourceSchema()
    schema.add_object_field('id', FieldType.ID, FormatType.HEX)
    schema.add_object_field('name', FieldType.NAME, FormatType.STRING)
    schema.add_object_field('created', FieldType.CREATED, FormatType.INTEGER)
    schema.add_object_field('user', FieldType.USER, FormatType.HEX)
    schema.add_relation_field('val', rel.id, FieldType.DATA, FormatType.INTEGER, PrimitiveMapping())

    res = ResourceList(obj1.id, schema, ObjectType.SPECIALS)

    for i in range(20):
        val = {
            'name': f'test_{i}',
            'val': i,
        }
        client.put_resource_list(res, [val], 'main_full')

    vals = client.get_resource_list(res)
    assert len(vals) == 20

    res = ResourceList(obj1.id, schema, ObjectType.SPECIALS)
    res.add_filter('val', 5, OperatorType.EQUALS)
    res.add_order('val', False)

    vals = client.get_resource_list(res)
    assert len(vals) == 1
    assert vals[0]['name'] == 'test_5'

    res = ResourceList(obj1.id, schema, ObjectType.SPECIALS)
    res.add_filter('val', 5, OperatorType.GREATER_OR_EQUAL)
    vals = client.get_resource_list(res)
    assert len(vals) == 15

    res = ResourceList(obj1.id, schema, ObjectType.SPECIALS)
    res.add_filter('val', 5, OperatorType.GREATER_OR_EQUAL)
    res.add_order('val', False)
    res.set_limit(10)
    vals = client.get_resource_list(res)
    assert len(vals) == 10
