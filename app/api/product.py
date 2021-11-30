"""Functions for product actions."""

import requests
from slugify import slugify

from .settings import API_BASE_URL


def create_product(access_token, product):
    """
    Create a product with the defined attributes.

    Returns:
        return: ID of the product.

    Args:
        access_token: required to get access to the API.
        product: piece of information about for the product.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'product',
            'name': product['name'],
            'slug': slugify(product['name']),
            'sku': str(product['id']),
            'description': product['description'],
            'manage_stock': False,
            'price': [
                {
                    'amount': product['price'],
                    'currency': 'RUB',
                    'includes_tax': True,
                },
            ],
            'status': 'live',
            'commodity_type': 'physical',
        },
    }

    api_url = '{0}/v2/products'.format(API_BASE_URL)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()['data']['id']


def link_picture_to_product(access_token, product_id, picture_id):
    """
    Create product relationship to the picture.

    Args:
        access_token: required to get access to the API.
        product_id: the ID of the product you want to relate to the image.
        picture_id: the ID of the image.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'main_image',
            'id': picture_id,
        },
    }

    api_url = '{0}/v2/products/{1}/relationships/main-image'.format(
        API_BASE_URL,
        product_id,
    )
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()


def get_all_products(access_token):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'content-type': 'application/json',
    }
    api_url = '{0}/v2/products'.format(API_BASE_URL)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()
    products_data = response.json()

    products = [product for product in products_data['data']]

    return products


def get_product_by_id(access_token, product_id):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }
    api_url = '{0}/v2/products/{1}'.format(API_BASE_URL, product_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_product_photo_by_id(access_token, product_id):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }
    api_url = '{0}/v2/files/{1}'.format(API_BASE_URL, product_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']['link']['href']
