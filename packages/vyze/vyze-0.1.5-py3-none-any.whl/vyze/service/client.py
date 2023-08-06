from typing import Union

import requests

from ..system import LayerProfile, read_layer_profile
from ..universe import load_universe, Universe


class ServiceClient:

    def __init__(self, url='https://api.vyze.io/service', timeout=300):
        self._url = url
        self._token: Union[str, None] = None
        self._timeout = timeout

    def set_token(self, token: Union[str, None]) -> None:
        self._token = token

    def resolve_universe(self, name: str) -> str:
        u = self._build_url(f'universe/resolve/{name}')
        return self.__get(u)

    def load_universe(self, universe_id: str) -> Union[Universe, None]:
        params = {
            'o': '1',
        }
        if self._token:
            params['t'] = self._token
        u = self._build_url(f'universe/{universe_id}/export', params)
        universe_def = self.__get(u, 'bytes')
        return load_universe(universe_def)

    def get_layer_profile(self, profile_id: str) -> Union[LayerProfile, None]:
        params = {}
        if self._token:
            params['t'] = self._token
        u = self._build_url(f'space/profile_tokens/{profile_id}', params)
        layer_profile_str = self.__get(u, 'text')
        return read_layer_profile(layer_profile_str)

    def _build_url(self, endpoint: str, params: Union[dict, None] = None):
        if params:
            return f'{self._url}/{endpoint}?{"&".join([k + "=" + v for k, v in params.items()])}'
        return f'{self._url}/{endpoint}'

    def __get(self, url: str, return_type: str = 'json') -> any:
        resp = requests.get(url, headers=self._get_headers(), timeout=self._timeout)
        if resp.status_code >= 300:
            raise RuntimeError(resp.text)
        if return_type == 'json':
            return resp.json()
        elif return_type == 'text':
            return resp.text
        elif return_type == 'bytes':
            return resp.content

    def _post(self, url: str, data: any) -> any:
        resp = requests.post(url, json=data, headers=self._get_headers(), timeout=self._timeout)
        return resp.json()

    def _put(self, url: str, data: any) -> any:
        resp = requests.put(url, json=data, headers=self._get_headers(), timeout=self._timeout)
        return resp.json()

    def _delete(self, url: str) -> any:
        resp = requests.delete(url, headers=self._get_headers(), timeout=self._timeout)
        return resp.json()

    def _get_headers(self, headers=None):
        if not headers:
            headers = {}
        return headers
