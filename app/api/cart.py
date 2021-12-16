"""Functions for manipulating with Carts in Moltin API."""

import requests

from .settings import API_BASE_URL


def get_or_create_cart(access_token, cart_id):
    """
    Get or create a cart.

    Returns:
        return: data about the cart.

    Args:
        access_token: required to get access to the API.
        cart_id: ID for the cart that the customer created.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/carts/{1}'.format(API_BASE_URL, cart_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()


def add_product_to_cart(access_token, cart_id, product_id, product_amount):
    """
    Add product to a cart.

    Returns:
        return: data about the cart.

    Args:
        access_token: required to get access to the API.
        cart_id: ID for the cart that the customer created.
        product_id: ID of the product you want to add to cart.
        product_amount: number of products to add to the cart.
    """
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
    """
    Get all items from the cart.

    Returns:
        return: data about the cart items.

    Args:
        access_token: required to get access to the API.
        cart_id: ID for the cart that the customer created.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/carts/{1}/items'.format(API_BASE_URL, cart_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()


def delete_product_from_cart(access_token, cart_id, product_id):
    """
    Remove items from cart.

    Returns:
        return: returns cart items.

    Args:
        access_token: required to get access to the API.
        cart_id: ID for the cart that the customer created.
        product_id: ID of the product you want to remove from cart.
    """
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
