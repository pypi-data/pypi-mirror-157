import requests

from src.vyze.universe import load_universe


def load_universe_from_api(universe_name, url='https://api.vyze.io/app/'):
    """
    Loads a universe, its models, fields and values from the VYZE API.

    Args:
        universe_name: Name of the universe.
        url: URL of the VYZE API.

    Returns:
        A universe object if successful or `None` otherwise.
    """

    resp = requests.get(f'{url}universe/resolve/{universe_name}')
    if resp.status_code != 200:
        return None
    universe_id = resp.json()
    resp = requests.get(f'{url}universe/{universe_id}/export?o=1')
    if resp.status_code != 200:
        return None
    universe_def = resp.content
    return load_universe(universe_def)
