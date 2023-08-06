import datetime
import json
import requests

from typing import Callable, List, Union, Dict

from .access import LayerToken, AccessGroup, LayerProfile
from .types import ReturnType, FormatType, MappingType, ObjectType, FieldType
from .resource import ResourceSchema, ResourceFilter, ResourceOrder, ResourceInstance, ResourceList, Resource
from ..util import JSONVal


class LayerError(RuntimeError):

    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return f'Missing permission: {self.msg}'


class Object:

    def __init__(self, id, name, user, created_at):
        self._id = id
        self._name = name
        self._user = user
        self._created_at = created_at

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def user(self) -> str:
        return self._user

    @property
    def created_at(self) -> str:
        return self._created_at

    def __repr__(self):
        if self.name:
            return f'Object {self.id} ({self.name})'
        return f'Object {self.id}'


class SystemClient:

    def __init__(self, url='https://api.vyze.io/system', timeout=300):
        self._url = url
        self._layer_profile: LayerProfile = LayerProfile()
        self._timeout = timeout
        self._default_options = {}

    def set_default_options(self, **kwargs):
        for k in kwargs:
            self._default_options[k] = kwargs[k]

    def get_default_options(self) -> dict:
        return self._default_options

    @property
    def layer_profile(self) -> LayerProfile:
        return self._layer_profile

    def set_layer_profile(self, layer_profile: LayerProfile) -> None:
        self._layer_profile = layer_profile

    def __fetch_layer_id(self, access_group: Union[str, None]) -> str:
        layer_id: Union[str, None] = None
        if access_group:
            ag = self.layer_profile[access_group]
            if ag:
                layer_id = ag.layer_id
        if not layer_id:
            raise RuntimeError("no matching layer found")
        return layer_id

    # General

    def get_info(self, **kwargs) -> Union[dict, None]:
        endpoint = self._build_url('info')
        response = self._get(endpoint, **kwargs)
        if not response:
            return None
        return {
            'api_version': response['apiVersion'],
            'server_version': response['serverVersion'],
            'unix_time': response['unixTime'] / 1000 / 1000,
            'layers': response['layers'],
        }

    def verify_token(self, token: str) -> Union[LayerToken, None]:
        endpoint = self._build_url('token', {'token': token})
        response = self._get(endpoint)
        if not response:
            return None
        if response['expiry'] == -1:
            expires = (datetime.datetime.now() + datetime.timedelta(days=365)).timestamp()
        else:
            expires = response['expiry'] / 1000 / 1000
        user_id = response['user']
        layer_id = response['layer']
        perms_granted = response['granted']
        perms_mandatory = response['mandatory']
        perms_exclusive = response['exclusive']
        signature = response['signature']
        return LayerToken(token, user_id, layer_id, perms_granted, perms_mandatory, perms_exclusive, expires, signature, verified=True)

    # Objects

    def get_object(self, object_id: str, **kwargs) -> Union[Object, None]:
        endpoint = self._build_url(f'object/{object_id}')
        response = self._get(endpoint, **kwargs)
        if not response:
            return None
        return Object(response['id'], response.get('name', ''), response['user'], response['created'])

    def create_object(self, abstract_ids, name, access_name: str, **kwargs) -> Union[Object, None]:
        layer_id = self.__fetch_layer_id(access_name)

        if not isinstance(abstract_ids, list):
            abstract_ids = [abstract_ids]

        endpoint = self._build_url('object')
        response = self._post(endpoint, {
            'abstracts': abstract_ids,
            'name': name,
            'layer': layer_id,
        }, **kwargs)
        if not response:
            return None
        return Object(response['id'], response.get('name', ''), response['user'], response['created'])

    def delete_object(self, object_id, **kwargs) -> None:
        endpoint = self._build_url(f'object/{object_id}')
        self._delete(endpoint, True, **kwargs)

    # Name

    def get_name(self, object_id: str, **kwargs) -> Union[str, None]:
        endpoint = self._build_url(f'object/{object_id}/name')
        response = self._get(endpoint, True, **kwargs)

        return response

    def set_name(self, object_id: str, name: str, **kwargs) -> None:
        endpoint = self._build_url(f'object/{object_id}/name')
        self._post(endpoint, name, True, **kwargs)

    # Data

    def get_data(self, object_id: str, format_type: FormatType, chunks: Union[int, None] = None, update: Union[Callable[[bytes, int, int], None], None] = None, **kwargs):
        if chunks:
            if format_type != FormatType.RAW:
                raise RuntimeError('chunked data requires raw format')
            endpoint = self._build_url(f'object/{object_id}/data', {'format': format_type.value})
            offset = 0
            response_bytes = bytes()
            while True:
                response = self._get(endpoint, headers={
                    'Range': f'bytes={offset}-{offset + chunks}',
                }, return_response=True, **kwargs)
                byte_range = response.headers.get('content-range')
                if not byte_range:
                    raise RuntimeError('expected byte range')
                byte_ranges = byte_range.split('/')
                if len(byte_ranges) != 2:
                    raise RuntimeError('unexpected byte range')
                length = int(byte_ranges[1])
                if update:
                    update(response.content, offset, length)
                response_bytes += response.content
                offset = len(response_bytes)
                if offset >= length:
                    break
            return response_bytes
        else:
            endpoint = self._build_url(f'object/{object_id}/data', {'format': format_type.value})
            response = self._get(endpoint, format_type != FormatType.RAW, **kwargs)
            return response

    def set_data(self, object_id: str, data: any, format_type: FormatType, chunks: Union[int, None] = None, update: Union[Callable[[int, int], None], None] = None, **kwargs) -> None:
        if not chunks:
            endpoint = self._build_url(f'object/{object_id}/data', {'format': format_type.value})
            self._post(endpoint, data, format_type != FormatType.RAW, **kwargs)
            if update:
                update(0, len(data))
        else:
            offset = 0
            while True:
                if update:
                    update(offset, len(data))
                data_chunk = data[offset:min(offset + chunks, len(data))]
                endpoint = self._build_url(f'object/{object_id}/data', {'append': '1', 'format': format_type.value})
                response = self._post(endpoint, data_chunk, format_type != FormatType.RAW, **kwargs)
                if response is False:
                    return
                offset += chunks
                if offset >= len(data):
                    if update:
                        update(len(data), len(data))
                    return

    def delete_data(self, object_id: str, **kwargs) -> None:
        endpoint = self._build_url(f'object/{object_id}/data')
        self._delete(endpoint, True, **kwargs)

    # Hierarchy

    def get_abstracts(self, object_id: str, include_self=False, include_direct=True, include_indirect=True, **kwargs):
        endpoint = self._build_url(f'object/{object_id}/abstracts', {
            'self': '1' if include_self else '0',
            'direct': '1' if include_direct else '0',
            'transitive': '1' if include_indirect else '0',
        })
        response = self._get(endpoint, True, **kwargs)

        return response

    def get_specials(self, object_id: str, include_self=False, include_direct=True, include_indirect=True, **kwargs):
        endpoint = self._build_url(f'object/{object_id}/specials', {
            'self': '1' if include_self else '0',
            'direct': '1' if include_direct else '0',
            'transitive': '1' if include_indirect else '0',
        })
        response = self._get(endpoint, True, **kwargs)

        return response

    # Relations

    def get_targets(self, object_id: str, return_type=ReturnType.OBJECTS, **kwargs):
        endpoint = self._build_url(f'object/{object_id}/targets', {'return': return_type.value})
        response = self._get(endpoint, True, **kwargs)

        return response

    def get_keyed_targets(self, object_id: str, abstract_id: str, key_format: FormatType,
                          offset: Union[int, None] = None, limit: Union[int, None] = None,
                          return_type: ReturnType = ReturnType.OBJECTS, **kwargs):
        params = {'return': return_type.value, 'format': key_format.value}
        if offset:
            params['offset'] = json.dumps(offset)
        if limit:
            params['limit'] = str(limit)
        endpoint = self._build_url(f'object/{object_id}/targets/{abstract_id}', params)
        response = self._get(endpoint, True, **kwargs)

        return response

    def get_origins(self, object_id: str, return_type: ReturnType = ReturnType.OBJECTS, **kwargs):
        endpoint = self._build_url(f'object/{object_id}/origins', {'return': return_type.value})
        response = self._get(endpoint, True, **kwargs)

        return response

    def get_keyed_origins(self, object_id: str, abstract_id: str, key_format: FormatType,
                          offset: Union[int, None] = None, limit: Union[int, None] = None,
                          return_type: ReturnType = ReturnType.OBJECTS, **kwargs):
        params = {'return': return_type.value, 'format': key_format.value}
        if offset:
            params['offset'] = json.dumps(offset)
        if limit:
            params['limit'] = str(limit)
        endpoint = self._build_url(f'object/{object_id}/origins/{abstract_id}', params)
        response = self._get(endpoint, True, **kwargs)

        return response

    def create_relation(self, origin_id: str, target_id: str, abstract_ids: str | list[str], name: str, access_name: str, key: any = None, key_format: Union[FormatType, None] = None, **kwargs):
        layer_id = self.__fetch_layer_id(access_name)

        if not isinstance(abstract_ids, list):
            abstract_ids = [abstract_ids]

        endpoint = self._build_url('relation')

        options = {
            'abstracts': abstract_ids,
            'name': name,
            'origin': origin_id,
            'target': target_id,
            'layer': layer_id,
        }
        if key:
            options['key'] = key
        if key_format:
            options['keyFormat'] = key_format.value

        response = self._post(endpoint, options, **kwargs)
        if not response:
            return None

        return Object(response['id'], response.get('name', ''), response['user'], response['created'])

    # Values

    def get_value(self, origin_id: str, relation_id: str, field_type: FieldType, format_type: FormatType, mapping_type: MappingType, **kwargs):
        if format_type == FormatType.RAW:
            raise RuntimeError('raw is not allowed')
        params = {
            'relation': relation_id,
            'field': field_type.value,
            'format': format_type.value,
        }
        mapping_type.set_params(params)
        endpoint = self._build_url(f'object/{origin_id}/value', params)
        if format_type != FormatType.RAW:
            return self._get(endpoint, **kwargs)
        else:
            return self._get(endpoint, is_json=False, **kwargs)

    def put_value(self, origin_id: str, relation_id: str, value: any, field_type: FieldType, format_type: FormatType, mapping_type: MappingType, access_name: str, key: any = None, **kwargs):
        layer_id = self.__fetch_layer_id(access_name)

        if format_type == FormatType.RAW:
            raise RuntimeError('raw is not allowed')

        params = {
            'relation': relation_id,
            'field': field_type.value,
            'format': format_type.value,
            'layer': layer_id,
        }
        mapping_type.set_params(params)
        if key:
            params['key'] = json.dumps(key)
        endpoint = self._build_url(f'object/{origin_id}/value', params)
        return self._post(endpoint, value, **kwargs)

    # Lookup

    def lookup_data(self, abstract_id: str, data: any, format_type: FormatType, mapping_type: MappingType, **kwargs):
        params = {
            'format': format_type.value,
        }
        mapping_type.set_params(params)
        endpoint = self._build_url(f'lookup/data/{abstract_id}', params)
        if format_type == FormatType.RAW:
            return self._post(endpoint, data, is_json=False, return_json=True, **kwargs)
        else:
            return self._post(endpoint, data, **kwargs)

    def lookup_value(self, relation_id: str, data: any, format_type: FormatType, mapping_type: MappingType, **kwargs):
        params = {
            'format': format_type.value,
        }
        mapping_type.set_params(params)
        endpoint = self._build_url(f'lookup/value/{relation_id}', params)
        if format_type == FormatType.RAW:
            return self._post(endpoint, data, is_json=False, return_json=True, **kwargs)
        else:
            return self._post(endpoint, data, **kwargs)

    # Resource

    def get_resource_instance(self, resource: ResourceInstance, **kwargs):
        endpoint = self._build_url(f'resource/get')
        return self._post(endpoint, resource.to_request(), **kwargs)

    def get_resource_list(self, resource: ResourceList, **kwargs):
        endpoint = self._build_url(f'resource/get')
        return self._post(endpoint, resource.to_request(), **kwargs)

    def _put_resource(self, resource: Resource, value: any, access_name: str, **kwargs):
        layer_id = self.__fetch_layer_id(access_name)

        endpoint = self._build_url(f'resource/put')
        options = {
            'objectId': resource._object_id,
            'object': resource._object_type.value,
            'schema': resource._schema.object,
            'value': value,
            'layer': layer_id,
        }
        return self._post(endpoint, options, **kwargs)

    def put_resource_instance(self, resource: ResourceInstance, value: any, access_name: str, **kwargs) -> Union[str, None]:
        return self._put_resource(resource, value, access_name, **kwargs)

    def put_resource_list(self, resource: ResourceList, value: List[any], access_name: str, **kwargs) -> Union[List[str], None]:
        return self._put_resource(resource, value, access_name, **kwargs)

    # API helpers

    def _build_url(self, endpoint: str, params: Union[dict, None] = None):
        if params:
            return f'{self._url}/v1/{endpoint}?{"&".join([k + "=" + v for k, v in params.items()])}'
        return f'{self._url}/v1/{endpoint}'

    def _get(self, url, is_json=True, headers=None, return_response=False, access_groups: Union[List[str], None] = None, **kwargs) -> Union[JSONVal, bytes, requests.Response]:
        resp = requests.get(url, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        if return_response:
            return resp
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 206:
            return resp.content
        self._handle_error(resp)

    def _post(self, url, data, is_json=True, return_json=None, headers=None, return_response=False, access_groups: Union[List[str], None] = None, **kwargs) -> Union[JSONVal, bytes, requests.Response]:
        if return_json is None:
            return_json = is_json
        if is_json:
            resp = requests.post(url, json=data, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        else:
            resp = requests.post(url, data=data, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        if return_response:
            return resp
        if resp.status_code == 200:
            return resp.json() if return_json else resp.content
        elif resp.status_code == 206:
            return resp.content
        self._handle_error(resp)

    def _put(self, url, data, is_json=True, headers=None, return_response=False, access_groups: Union[List[str], None] = None, **kwargs) -> Union[JSONVal, bytes, requests.Response]:
        if is_json:
            resp = requests.post(url, json=data, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        else:
            resp = requests.post(url, data=data, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        if return_response:
            return resp
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 206:
            return resp.content
        self._handle_error(resp)

    def _delete(self, url, is_json=True, headers=None, return_response=False, access_groups: Union[List[str], None] = None, **kwargs) -> Union[JSONVal, bytes, requests.Response]:
        resp = requests.delete(url, headers=self._get_headers(headers, access_groups=access_groups), timeout=self._timeout, **kwargs)
        if return_response:
            return resp
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 206:
            return resp.content
        self._handle_error(resp)

    def _handle_error(self, resp):
        if resp.status_code == 403:
            raise LayerError(resp.content)
        vy_code = resp.headers.get("x-vy-code")
        vy_message = resp.headers.get("x-vy-message")
        if vy_code and vy_message:
            raise RuntimeError(f'HTTP Error <{resp.status_code}> / Vyze Error <{resp.headers.get("x-vy-code")}> {resp.headers.get("x-vy-message")}')
        else:
            raise RuntimeError(f'HTTP Error <{resp.status_code}> / {resp.content}')

    def _get_headers(self, headers=None, cached=False, access_groups: Union[List[str], None] = None):
        if not headers:
            headers = {}
        tokens = []
        if access_groups is not None:
            for n in access_groups:
                ag = self.layer_profile[n]
                if not ag:
                    continue
                for t in ag.layer_tokens:
                    tokens.append(t.token)
        else:
            for ag in self.layer_profile.access_groups:
                for t in ag.layer_tokens:
                    tokens.append(t.token)
        headers['x-vy-layers'] = ','.join(tokens)
        if not cached:
            headers['x-vy-bypass-cache'] = '1'
        return headers
