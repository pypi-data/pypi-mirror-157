import datetime
from typing import List, Union


# LAYER TOKEN

class LayerToken:

    def __init__(self, token: str, user_id: str, layer_id: str,
                 perms_granted: int, perms_mandatory: int, perms_exclusive: int,
                 created: datetime.datetime, expiry: Union[datetime.timedelta, None],
                 signature: bytes, verified=False):
        self._token: str = token

        self._layer_id: str = layer_id
        self._user_id: str = user_id

        self._perms_granted: int = perms_granted
        self._perms_mandatory: int = perms_mandatory
        self._perms_exclusive: int = perms_exclusive

        self._created: datetime.datetime = created
        self._expiry: Union[datetime.timedelta, None] = expiry

        self._signature: bytes = signature

        self._verified: bool = verified

    @property
    def token(self) -> str:
        return self._token

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def layer_id(self) -> str:
        return self._layer_id

    @property
    def granted(self) -> int:
        return self._perms_granted

    @property
    def mandatory(self) -> int:
        return self._perms_mandatory

    @property
    def exclusive(self) -> int:
        return self._perms_exclusive

    @property
    def expires(self) -> datetime.datetime:
        if not self._expiry:
            return datetime.datetime(year=datetime.MAXYEAR, month=1, day=1)
        return self._created + self._expiry

    @property
    def expired(self) -> bool:
        return self.expires < datetime.datetime.now()

    @property
    def signature(self) -> bytes:
        return self._signature

    @property
    def verified(self) -> bool:
        return self._verified

    def __repr__(self):
        return f'Token [Space: {self.layer_id}, User: {self.user_id}, Verified: {self.verified}]'


def read_layer_token(token):
    if len(token) != 152:
        return None
    user_id = token[0:32]
    layer_id = token[32:64]
    perm_granted = int.from_bytes(bytes.fromhex(token[64:72]), byteorder='big')
    perm_mandatory = int.from_bytes(bytes.fromhex(token[72:80]), byteorder='big')
    perm_exclusive = int.from_bytes(bytes.fromhex(token[80:88]), byteorder='big')
    created_hex = token[88:104]
    expiry_hex = token[104:112]
    created_bytes = bytes.fromhex(created_hex)
    expiry_bytes = bytes.fromhex(expiry_hex)
    created_unix = int.from_bytes(created_bytes, byteorder='big')
    created_dt = datetime.datetime.fromtimestamp(created_unix)
    expiry_seconds = int.from_bytes(expiry_bytes, byteorder='big')
    if expiry_seconds < 0:
        expiry_td = None
    else:
        expiry_td = datetime.timedelta(seconds=expiry_seconds)
    signature = bytes.fromhex(token[120:152])
    return LayerToken(token, user_id, layer_id,
                      perm_granted, perm_mandatory, perm_exclusive,
                      created_dt, expiry_td,
                      signature, False)


# ACCESS GROUP

class AccessGroup:

    def __init__(self, name: str, permission: int):
        self._name: str = name
        self._permission: int = permission
        self._tokens: List[LayerToken] = []

    def register_layer_token(self, layer_token: LayerToken):
        if layer_token.granted & self.permissions != self.permissions:
            raise RuntimeError('insufficient permissions')
        self._tokens.append(layer_token)

    def unregister_layer_token(self, token: str):
        self._tokens = [t for t in self._tokens if t.token != token]

    @property
    def layer_id(self) -> Union[str, None]:
        if len(self._tokens) == 0:
            return None
        return self._tokens[0].layer_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def permissions(self) -> int:
        return self._permission

    @property
    def layer_tokens(self) -> List[LayerToken]:
        return list(self._tokens)

    def __str__(self):
        tokens = ','.join((t.token for t in self.layer_tokens))
        return f'{self.name}:{self.permissions:x}:{tokens}'


def read_access_group(group_string: str) -> AccessGroup:
    group_split = group_string.split(':')
    if len(group_split) != 3:
        raise RuntimeError('invalid group string')
    group_perms = int(group_split[1], 16)
    ag = AccessGroup(group_split[0], group_perms)
    token_split = group_split[2].split(',')
    for token in token_split:
        if len(token) == 0:
            continue
        ag.register_layer_token(read_layer_token(token))
    return ag


# LAYER PROFILE

class LayerProfile:

    def __init__(self):
        self._access_groups = dict()

    def add_access_group(self, name: str, permissions: int) -> AccessGroup:
        ag = self._access_groups.get(name)
        if not ag:
            ag = AccessGroup(name, permissions)
        elif ag.permissions != permissions:
            raise RuntimeError('incorrect permissions')
        return ag

    def get_access_group(self, name: str) -> Union[AccessGroup, None]:
        return self._access_groups.get(name)

    def remove_access_group(self, name) -> None:
        del self._access_groups[name]

    @property
    def access_groups(self) -> List[AccessGroup]:
        return list(self._access_groups.values())

    def __getitem__(self, item):
        return self.get_access_group(item)

    def __str__(self):
        return ';'.join((str(ag) for ag in self._access_groups.values()))


def read_layer_profile(profile_string: str) -> Union[LayerProfile, None]:
    lp = LayerProfile()
    profile_split = profile_string.split(';')
    for group_string in profile_split:
        ag = read_access_group(group_string)
        lp._access_groups[ag.name] = ag
    return lp
