"""Functions for manipulating files."""

import os
from urllib.parse import urlparse

import requests
from slugify import slugify

from .settings import API_BASE_URL


def download_picture(product):
    """
    Download picture for the product.

    Returns:
        return: path for the picture file.

    Args:
        product: piece of information about for the product.
    """
    os.makedirs('./pictures', exist_ok=True)
    product_name = slugify(product['name'])

    picture_url = product['product_image']['url']
    parsed_url = urlparse(picture_url)
    file_extension = os.path.splitext(
        os.path.basename(parsed_url.path),
    )[-1]

    picture_name = '{0}{1}'.format(product_name, file_extension)
    picture_path = os.path.join('pictures', picture_name)

    response = requests.get(picture_url)
    response.raise_for_status()
    with open(picture_path, 'wb') as picture_file:
        picture_file.write(response.content)

    return picture_path


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
