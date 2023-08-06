import requests

from src.vyze.system import SpaceManager, parse_space_token


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
