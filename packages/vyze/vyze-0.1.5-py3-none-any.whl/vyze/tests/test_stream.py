import time

from src import vyze
from src.vyze import FieldType, FormatType, ResourceList, ObjectType, read_layer_profile, ResourceInstance
from src.vyze.tests.test_client import profile_str, service_url, system_url, test_universe

# stream_url = 'ws://localhost:9131'
stream_url = 'wss://api.vyze.io/system'


def test_stream_client__connect():
    stream_client = vyze.SystemStreamClient(url=stream_url)
    stream_client.connect()
    stream_client.disconnect()


def test_stream_client__get_info():
    stream_client = vyze.SystemStreamClient(url=stream_url)
    stream_client.connect()
    info = stream_client.get_info().result()
    assert info
    stream_client.disconnect()


def test_stream_client__get_space_tokens():
    layer_profile = read_layer_profile(profile_str)
    stream_client = vyze.SystemStreamClient(url=stream_url)
    stream_client.connect()
    for ag in layer_profile.access_groups:
        for tk in ag.layer_tokens:
            stream_client.register_layer_token(tk)
    tokens = stream_client.get_layer_tokens().result()
    assert len(tokens) == 3
    stream_client.disconnect()


def test_stream_client__get_resource():
    layer_profile = read_layer_profile(profile_str)
    client = vyze.SystemClient(url=system_url)
    client.set_layer_profile(layer_profile)
    service = vyze.ServiceClient(url=service_url)
    universe = service.load_universe(service.resolve_universe(test_universe))

    schema = vyze.ResourceSchema()
    schema.add_object_field('id', FieldType.ID, FormatType.HEX)
    schema.add_object_field('name', FieldType.NAME, FormatType.STRING)

    obj = client.create_object(universe.resolve('base.object/'), 'obj', 'main_full')

    res_list = ResourceList(obj.id, schema, ObjectType.SPECIALS)

    ids = client.put_resource_list(res_list, [{'name': f'obj {i}'} for i in range(10)], 'main_full')
    assert len(ids) == 10

    objs = client.get_resource_list(res_list)
    assert len(objs) == 10

    stream_client = vyze.SystemStreamClient(url=stream_url)
    stream_client.connect()
    stream_client.register_layer_profile(layer_profile)

    res_inst = ResourceInstance(ids[0], schema, ObjectType.INSTANCE)

    sub1 = client.get_resource_instance(res_inst)
    subi = stream_client.get_resource_instance(res_inst, instant=True)
    time.sleep(1)
    assert subi.value['id'] == sub1['id'] == ids[0]

    sublsys = client.get_resource_list(res_list)
    assert len(sublsys) == 10
    subl = stream_client.get_resource_list(res_list, instant=True)
    def cb(_, message):
        if message['type'] != 'add':
            return
        val = subl.get_value(message['id'])
    subl.subscribe(cb)
    time.sleep(1)
    assert len(subl.values) == 10

    stream_client.disconnect()
