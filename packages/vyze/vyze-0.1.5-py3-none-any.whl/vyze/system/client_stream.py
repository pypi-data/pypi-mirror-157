import json
import threading
from concurrent.futures import Future
from typing import Dict, Callable, List, Generic, TypeVar, Union

from websocket import create_connection

from .access import LayerToken, LayerProfile
from .resource import ResourceList, ResourceInstance, ResourceField, ResourceObjectField, ResourceRelationField
from .types import ValueType
from ..util import new_id


class ResourceValue:

    def __init__(self, **kwargs):
        self._value: Dict[str, any] = kwargs

    def __getitem__(self, item):
        return self._value.get(item)

    def __setitem__(self, key, value):
        self._value[key] = value

    def __str__(self):
        return str(self._value)

    def __iter__(self):
        return dict(self._value)


class SystemSubject:

    def __init__(self):
        self.callbacks: Dict[str, Callable[[str, any], None]] = {}

    def subscribe(self, callback: Callable[[str, any], None]) -> str:
        cb_id = new_id()
        self.callbacks[cb_id] = callback
        return cb_id

    def unsubscribe(self, cb_id):
        del self.callbacks[cb_id]

    def next(self, *args):
        cbs = list(self.callbacks.items())
        for cb_id, cb in cbs:
            cb(cb_id, *args)


T = TypeVar('T')


class ValueSubject(SystemSubject, Generic[T]):

    def __init__(self):
        super().__init__()
        self._value: Union[T, None] = None

    @property
    def value(self) -> Union[T, None]:
        return self._value

    def _set_value(self, value: Union[T, None]):
        self._value = value


class ResourceStreamInstance(ValueSubject[ResourceValue]):

    def __init__(self, resource: ResourceInstance):
        super().__init__()
        self._resource: ResourceInstance = resource

    @property
    def resource(self) -> ResourceInstance:
        return self._resource


class ResourceStreamList(SystemSubject):

    def __init__(self, resource: ResourceList):
        super().__init__()
        self._values: List[ResourceValue] = []
        self._value_ids: Dict[ResourceValue, str] = {}
        self._value_indexes: Dict[str, int] = {}
        self._resource: ResourceList = resource

    @property
    def resource(self) -> ResourceList:
        return self._resource

    def reorder(self) -> None:
        pass

    @property
    def values(self) -> List[ResourceValue]:
        return self._values

    def get_index(self, value_id: str) -> int:
        return self._value_indexes.get(value_id, -1)

    def get_value(self, value_id: str) -> Union[ResourceValue, None]:
        idx = self.get_index(value_id)
        if idx == -1:
            return None
        return self._values[idx]

    def _put_value(self, value_id: str) -> ResourceValue:
        inst = self.get_value(value_id)
        if inst is None:
            inst = ResourceValue()
            self._value_indexes[value_id] = len(self._values)
            self._value_ids[inst] = value_id
            self._values.append(inst)
        return inst

    def _set_value(self, value_id: str, value: ResourceValue) -> None:
        idx = self._value_indexes[value_id]
        if idx == -1:
            return
        self._values[idx] = value

    def _remove_value(self, value_id: str) -> None:
        idx = self.get_index(value_id)
        if idx == -1:
            return
        val = self._values[idx]
        del self._value_ids[val]
        for i in range(idx + 1, len(self._values)):
            post_id = self._value_ids[self._values[i]]
            if not post_id:
                continue
            self._value_indexes[post_id] = i - 1
        del self._values[idx]
        del self._value_indexes[value_id]


def update_new_value(fields: List[ResourceField], value: dict, new_value: Union[any, None]):
    if not new_value:
        return value
    for field in fields:
        new_field_value = new_value.get(field.name)
        if new_field_value is None:
            continue
        if isinstance(field, ResourceObjectField) or (isinstance(field, ResourceRelationField) and field.mapping_type.type == ValueType.PRIMITIVE):
            if new_field_value is not None:
                value[field.name] = new_field_value
            elif value[field.name] is not None:
                del value[field.name]
        else:
            if not isinstance(new_field_value, list):
                continue
            values: List[any] = value.get(field.name)
            if values is None:
                values = list(new_field_value)
            else:
                values.extend(new_field_value)
            value[field.name] = values
    return value


def update_old_value(fields: List[ResourceField], value: dict, old_value: Union[any, None]):
    if not old_value:
        return value
    for field in fields:
        old_field_value = old_value.get(field.name)
        if old_field_value is None:
            continue
        if isinstance(field, ResourceObjectField) or (isinstance(field, ResourceRelationField) and field.mapping_type.type == ValueType.PRIMITIVE):
            continue
        if not isinstance(old_field_value, list):
            continue
        values: List[any] = value.get(field.name)
        if values is None:
            continue
        for rem_val in old_field_value:
            try:
                idx = values.index(rem_val)
                del values[idx]
            except ValueError:
                continue
    return value


class SystemStreamClient:

    def __init__(self, url: str = 'ws://api.vyze.io/system'):
        self._url: str = url
        self._websocket = None
        self._subscriptions: Dict[str, ValueSubject] = dict()
        self._thread = None

    def connect(self):
        self._websocket = create_connection(f'{self._url}/v1/stream')
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def disconnect(self):
        self._websocket.close()

    def get_info(self):
        fut = Future()
        message_id = new_id()

        def handle_response(cb_id, message):
            self._unsubscribe_message(message_id, cb_id)
            fut.set_result(message)

        self._subscribe_message(message_id, handle_response)
        self._send({
            'command': 'info',
            'messageId': message_id,
        })

        return fut

    def register_layer_token(self, token: LayerToken):
        message_id = new_id()
        self._send({
            'command': 'registerLayerTokens',
            'messageId': message_id,
            'payload': {
                'tokens': [token.token],
            }
        })

    def register_layer_profile(self, profile: LayerProfile):
        message_id = new_id()
        tokens: List[str] = []
        for ag in profile.access_groups:
            for tk in ag.layer_tokens:
                tokens.append(tk.token)
        self._send({
            'command': 'registerLayerTokens',
            'messageId': message_id,
            'payload': {
                'tokens': tokens,
            }
        })

    def get_layer_tokens(self):
        fut = Future()
        message_id = new_id()

        def handle_response(cb_id, message):
            self._unsubscribe_message(message_id, cb_id)
            fut.set_result(message.get('tokens'))

        self._subscribe_message(message_id, handle_response)
        self._send({
            'command': 'getLayerTokens',
            'messageId': message_id,
        })

        return fut

    def get_resource_instance(self, resource: ResourceInstance, instant=True) -> ResourceStreamInstance:
        sub = ResourceStreamInstance(resource)
        message_id = new_id()

        def update_value(update):
            if update['type'] == 'remove':
                sub._set_value(None)
            else:
                value = sub.value if sub.value else {}
                try:
                    value = update_old_value(resource.schema.fields, value, update['removed'])
                    value = update_new_value(resource.schema.fields, value, update['added'])
                except BaseException as e:
                    print(e)
                sub._set_value(value)

        sub.subscribe(lambda _, message: update_value(message))

        def handle_response(cb_id, message):
            print(message)
            sub.next(message)

        self._subscribe_message(message_id, handle_response)
        self._send({
            'command': 'subscribe',
            'messageId': message_id,
            'payload': {
                'event': 'resource',
                'params': {
                    'object': resource.object_id,
                    'params': resource.to_request(),
                    'specials': False,
                    'payload': True,
                    'instant': instant,
                },
            },
        })

        return sub

    def get_resource_list(self, resource: ResourceList, instant=True) -> ResourceStreamList:
        sub = ResourceStreamList(resource)
        message_id = new_id()

        def update_value(update):
            if update['type'] == 'remove':
                sub._remove_value(update['id'])
            else:
                value = sub._put_value(update['id'])
                try:
                    value = update_old_value(resource.schema.fields, value, update['removed'])
                    value = update_new_value(resource.schema.fields, value, update['added'])
                except BaseException as e:
                    print(e)
                sub._set_value(update['id'], value)

        sub.subscribe(lambda _, message: update_value(message))

        def handle_response(cb_id, message):
            sub.next(message)

        self._subscribe_message(message_id, handle_response)
        self._send({
            'command': 'subscribe',
            'messageId': message_id,
            'payload': {
                'event': 'resource',
                'params': {
                    'object': resource.object_id,
                    'params': resource.to_request(),
                    'specials': False,
                    'payload': True,
                    'instant': instant,
                },
            },
        })

        return sub

    def _run(self):
        while True:
            try:
                msg = self._websocket.recv()
                self._handle(msg)
            except BaseException as e:
                print(e)
                break

    def _handle(self, msg):
        print('handle', msg)
        msg = json.loads(msg)
        ref_id = msg['referenceId']
        cbs = self._subscriptions.get(ref_id)
        if not cbs:
            return
        cbs.next(msg['payload'])

    def _send(self, msg):
        if not self._websocket:
            return
        self._websocket.send(json.dumps(msg))

    def _subscribe_message(self, ref_id: str, callback: Callable[[any], None]) -> str:
        cbs = self._subscriptions.get(ref_id)
        if cbs is None:
            cbs = ValueSubject()
            self._subscriptions[ref_id] = cbs
        return cbs.subscribe(callback)

    def _unsubscribe_message(self, ref_id: str, cb_id: str):
        subs = self._subscriptions.get(ref_id)
        if not subs:
            return
        subs.unsubscribe(cb_id)
