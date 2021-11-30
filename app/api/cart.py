import requests

from .settings import API_BASE_URL


def get_or_create_cart(access_token, cart_id):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/carts/{1}'.format(API_BASE_URL, cart_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()


def add_product_to_cart(access_token, cart_id, product_id, product_amount):

    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-type': 'application/json',
        'X-MOLTIN-CURRENCY': 'RUB',
    }

    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': product_amount,
        },
    }
    
    api_url = '{0}/v2/carts/{1}/items'.format(API_BASE_URL, cart_id)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def get_cart_items(access_token, cart_id):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/carts/{1}/items'.format(API_BASE_URL, cart_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()


def delete_product_from_cart(access_token, cart_id, product_id):
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }
    api_url = '{0}/v2/carts/{1}/items/{2}'.format(
        API_BASE_URL,
        cart_id,
        product_id,
    )
    response = requests.delete(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()
