from src.vyze import ResourceSchema, FormatType, FieldType, ListMapping, PrimitiveMapping


def test_resource_add():
    schema1 = ResourceSchema()
    schema1.add_object_field('id', field_type=FieldType.ID, format_type=FormatType.HEX)
    schema1.add_object_field('name', field_type=FieldType.NAME, format_type=FormatType.STRING)
    schema1.add_relation_field('target_obj1', relation_id='rel1', mapping_type=ListMapping(),
                               field_type=FieldType.ID, format_type=FormatType.STRING)

    schema2 = ResourceSchema()
    schema2.add_object_field('id', field_type=FieldType.ID, format_type=FormatType.HEX)
    schema2.add_object_field('name', field_type=FieldType.NAME, format_type=FormatType.STRING)
    schema2.add_relation_field('target_obj2', relation_id='rel1', mapping_type=ListMapping(),
                               field_type=FieldType.ID, format_type=FormatType.STRING)

    schema3 = schema1 + schema2

    assert len(schema3.object['fields']) == 4


def test_mapping_params():
    pm = PrimitiveMapping(a='1')
    pm.set('b', '2')
    pm['c'] = '3'
    assert len(pm.params) == 3
    assert pm.params['a'] == '1'
    assert pm.params['b'] == '2'
    assert pm.params['c'] == '3'
