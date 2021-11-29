"""Authentication functions for the API access."""

import requests

from settings import API_BASE_URL, CLIENT_ID, CLIENT_SECRET


def get_access_token(redis_db):
    """
    Get access token and store it in DB.

    Returns:
        return: access token.

    Args:
        redis_db: database.
    """
    access_token = redis_db.get('access_token')
    if not access_token:
        access_token, time_to_expire = get_auth_token()
        redis_db.set(
            'access_token',
            access_token,
            ex=time_to_expire,
        )

    return access_token


def get_auth_token():
    """
    Create auth data.

    Returns:
        return: access token and token expiring time.
    """
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
    }

    api_url = '{0}/oauth/access_token'.format(API_BASE_URL)
    response = requests.post(url=api_url, data=payload)
    response.raise_for_status()
    auth_data = response.json()

    return auth_data['access_token'], auth_data['expires_in']
