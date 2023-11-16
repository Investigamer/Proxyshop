"""
* Handles Requests to the hexproof.io API
"""
# Third Party Imports
import requests


def get_api_key(key: str) -> str:
    """
    Get an API key from the https://api.hexproof.io server.
    @param key: Name of the API key.
    @return: API key string.
    """
    try:
        response = requests.get(f"https://api.hexproof.io/key/get/{key}", timeout=(3, 3))
        if response.status_code == 200:
            return response.json().get('key', '')
        print(response.json().get(
            'message', f"Failed to get key: '{key}'"))
    except Exception as e:
        print(e)
    return ''
