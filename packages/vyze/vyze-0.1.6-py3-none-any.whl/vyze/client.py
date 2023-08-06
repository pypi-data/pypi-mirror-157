import requests


class SpaceError(RuntimeError):

    def __init__(self, request):
        self.request = request

    def __repr__(self):
        return f'Missing permission: {self.request}'


class Client:

    def __init__(self, url='https://api.vyze.io/system/', timeout=300):
        self.__url = url

        self.__space = None

        self.__space_tokens = {}

        self.__space_manager = None

        self.__abstract_cache = {}
        self.__special_cache = {}
        self.__targets_cache = {}
        self.__origins_cache = {}

        self.__timeout = timeout

    # Access

    def register_space_token(self, token, use_space=True):
        if use_space:
            self.__space = token.space_id
        self.__space_tokens[token.space_id] = token
        return token

    def set_space(self, space_id):
        self.__space = space_id

    def set_space_manager(self, space_manager):
        self.__space_manager = space_manager

    # Objects

    def create_object(self, abstracts, name='', space=None, dependent=False):
        if not isinstance(abstracts, list):
            abstracts = [abstracts]
        if not space:
            if not self.__space:
                raise RuntimeError('no space selected')
            space = self.__space

        return self.__post(f'{self.__url}objects', {
            'abstracts': abstracts,
            'space': space,
            'name': name,
            'dependent': dependent,
        })['object']

    def get_object(self, id: str):
        return self.__get(f'{self.__url}objects/{id}')['object']

    def delete_object(self, id: str):
        return self.__delete(f'{self.__url}objects/{id}')

    def delete_objects(self, ids: list):
        for id in ids:
            self.delete_object(id)

    # Name

    def get_name(self, id: str):
        return self.__get(f'{self.__url}objects/{id}/name')

    def set_name(self, id: str, name: str):
        self.__post(f'{self.__url}objects/{id}/name', {
            'name': name,
        })

    # Data

    def get_data(self, id: str) -> bytes:
        return self.__get(f'{self.__url}objects/{id}/data', is_json=False)

    def set_data(self, id: str, data: bytes, chunks=None, update=None):
        if not chunks:
            return self.__post(f'{self.__url}objects/{id}/data', data, is_json=False) is not False
        else:
            offset = 0
            while True:
                if update:
                    update(offset, len(data))
                data_chunk = data[offset:min(offset + chunks, len(data))]
                if self.__post(f'{self.__url}objects/{id}/data?a=1', data_chunk, is_json=False) is False:
                    return False
                offset += chunks
                if offset >= len(data):
                    if update:
                        update(len(data), len(data))
                    return True

    # Hierarchy

    def get_abstracts(self, id: str, include_self=False, include_direct=True, include_transitive=False):
        return self.__get_hierarchy(id, include_self, include_direct, include_transitive, 'abstracts', self.__abstract_cache)

    def get_specials(self, id: str, include_self=False, include_direct=True, include_transitive=False):
        return self.__get_hierarchy(id, include_self, include_direct, include_transitive, 'specials', self.__special_cache)

    # Relations

    def create_relation(self, origin_id, target_id, abstracts, name='', space=None):
        if not isinstance(abstracts, list):
            abstracts = [abstracts]
        if not space:
            if not self.__space:
                raise RuntimeError('no space selected')
            space = self.__space

        body = {
            'origin': origin_id,
            'target': target_id,
            'abstracts': abstracts,
            'space': space,
            'name': name
        }

        return self.__post(f'{self.__url}relations', body)['relation']

    def get_targets(self, id: str) -> dict:
        return self.__get_relations(id, 'targets', self.__targets_cache)

    def get_origins(self, id: str) -> dict:
        return self.__get_relations(id, 'origins', self.__origins_cache)

    # Private

    def __get_hierarchy(self, id: str, include_self: bool, include_direct: bool, include_transitive: bool, name: str, cache: dict):
        ck = f'{id}_{"1" if include_self else "0"}{"1" if include_direct else "0"}{"1" if include_transitive else "0"}'
        hier = cache.get(ck)
        if not hier:
            hier = self.__get(
                f'{self.__url}objects/{id}/{name}'
                f'?self={"1" if include_self else "0"}'
                f'&direct={"1" if include_direct else "0"}'
                f'&transitive={"1" if include_transitive else "0"}')['ids']
            cache[ck] = hier
        return hier

    def __get_relations(self, id: str, name: str, cache: dict) -> dict:
        ck = f'{id}'
        rel = cache.get(ck)
        if not rel:
            resp = self.__get(f'{self.__url}objects/{id}/{name}')
            if resp:
                rel = resp['idPairs']
                cache[ck] = rel
        return rel

    def __request_permission(self, request):
        if not self.__space_manager:
            raise SpaceError(request)
        token = self.__space_manager.request_space_token(request, self.__space_tokens)
        if not token:
            raise SpaceError(request)
        self.register_space_token(token, False)

    def __get(self, url, is_json=True, **kwargs):
        resp = requests.get(url, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 403:
            self.__request_permission(resp.text)
            return self.__get(url, is_json, **kwargs)
        return None

    def __post(self, url, data, is_json=True, **kwargs):
        if is_json:
            resp = requests.post(url, json=data, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        else:
            resp = requests.post(url, data=data, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 403:
            self.__request_permission(resp.text)
            return self.__post(url, data, is_json, **kwargs)
        else:
            return False

    def __put(self, url, data, is_json=True, **kwargs):
        if is_json:
            resp = requests.post(url, json=data, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        else:
            resp = requests.post(url, data=data, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 403:
            self.__request_permission(resp.text)
            return self.__put(url, data, is_json, **kwargs)
        return None

    def __delete(self, url, is_json=True, **kwargs):
        resp = requests.delete(url, headers=self.__get_headers(), timeout=self.__timeout, **kwargs)
        if resp.status_code == 200:
            return resp.json() if is_json else resp.content
        elif resp.status_code == 403:
            self.__request_permission(resp.text)
            return self.__delete(url, is_json, **kwargs)
        return None

    def __get_headers(self, cached=False):
        headers = {
            'x-vy-spaces': ','.join([v.token for (k, v) in self.__space_tokens.items()]),
        }
        if not cached:
            headers['x-vy-bypass-cache'] = '1'
        return headers
