import datetime

import requests


class SpaceToken:

    def __init__(self, user_id, space_id, token, perms_granted, perms_mandatory, perms_exclusive, expires):
        self.__user_id = user_id
        self.__space_id = space_id
        self.__token = token
        self.__perms_granted = int.from_bytes(bytes.fromhex(perms_granted), byteorder='little')
        self.__perms_mandatory = int.from_bytes(bytes.fromhex(perms_mandatory), byteorder='little')
        self.__perms_exclusive = int.from_bytes(bytes.fromhex(perms_exclusive), byteorder='little')

        expires_bytes = bytes.fromhex(expires)
        expires_unix = int.from_bytes(expires_bytes, byteorder='little')

        self.__expires = datetime.datetime.fromtimestamp(expires_unix)

    @property
    def user_id(self):
        return self.__user_id

    @property
    def space_id(self):
        return self.__space_id

    @property
    def permissions(self):
        return [self.__perms_granted, self.__perms_mandatory, self.__perms_exclusive]

    @property
    def token(self):
        return self.__token

    @property
    def expires(self):
        return self.__expires


class SpaceManager:

    def __init__(self):
        pass

    def request_space_token(self, request, tokens):
        return None


class UserSpaceManager(SpaceManager):

    def __init__(self, url='https://api.vyze.io/app/'):
        super().__init__()
        self.__username = None
        self.__password = None
        self.__url = url
        self.__user_id = url
        self.__refresh_token = url

    def login(self, username, password):
        self.__username = username
        self.__password = password

        resp = requests.post(f'{self.__url}user/login', json={
            'username': username,
            'password': password,
        })

        if resp.status_code != 200:
            raise RuntimeError(f"login failed: " + str(resp.content, "ascii"))

        self.__user_id = resp.json()['userId']
        self.__refresh_token = resp.json()['refreshToken']

        return self.__refresh()

    def __refresh(self):
        resp = requests.post(f'{self.__url}user/refresh', json={
            'userId': self.__user_id,
            'refreshToken': self.__refresh_token,
        })

        if resp.status_code != 200:
            return False

        login_info = resp.json()
        self.__access_token = login_info['accessToken']

        return True

    def request_space_token(self, request, tokens):
        request_s = request.split('/')
        if len(request_s) != 3:
            return None
        spaces = request_s[0]
        missing_space = None
        while len(spaces) > 0:
            space = spaces[:32]
            spaces = spaces[32:]
            if tokens.get(space):
                continue
            missing_space = space
            break
        if not missing_space:
            return None

        resp = self.__get(f'{self.__url}token/space/{missing_space}')
        if resp:
            return parse_space_token(resp.get('token', ''))

        return None

    def __get(self, url, is_json=True, **kwargs):
        resp = requests.get(url, headers={
            'Authorization': f'Baerer {self.__access_token}'
        }, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 403:
            if self.__refresh():
                return self.__get(url, is_json=is_json, **kwargs)
        return None


def parse_space_token(token):
    if len(token) != 144:
        return None
    user_id = token[0:32]
    space_id = token[32:64]
    perm_granted = token[64:72]
    perm_mandatory = token[72:80]
    perm_exclusive = token[80:88]
    expires = token[88:104]
    # seed = token[104:112]
    # checksum = token[112:144]
    return SpaceToken(user_id, space_id, token, perm_granted, perm_mandatory, perm_exclusive, expires)
