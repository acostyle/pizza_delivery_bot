"""Functions for manipulating files."""

import requests

from settings import API_BASE_URL


def create_picture(access_token, picture):
    """
    Create picture for the product.

    Returns:
        return: ID of the picture.

    Args:
        access_token: required to get access to the API.
        picture: the picture you want to upload.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    files = {
        'file': open(picture, 'rb'),
        'public': True,
    }

    api_url = '{0}/v2/files'.format(API_BASE_URL)
    response = requests.post(url=api_url, headers=headers, files=files)
    response.raise_for_status()

    return response.json()['data']['id']
