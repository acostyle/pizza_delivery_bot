"""Customer functions for Moltin API."""

import requests
from .settings import API_BASE_URL


def create_customer(access_token, chat_id, email):
    """
    Create customer.

    Returns:
        return: returns data about created customer.

    Args:
        access_token: required to get access to the API.
        chat_id: ID for the customer.
        email: the customer email.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }
    payload = {
        'data': {
            'type': 'customer',
            'name': chat_id,
            'email': email,
        },
    }
    api_url = '{0}/v2/customers/'.format(API_BASE_URL)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()['data']['id']


def create_customer_address(access_token, customer_position, cart_id):
    """
    Create customer address.

    Args:
        access_token: required to get access to the API.
        customer_position: location of customer.
        cart_id: ID for the customer's cart.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    longitude, latitude = customer_position
    payload = {
        'data': {
            'type': 'entry',
            'longitude': longitude,
            'latitude': latitude,
            'cart-id': cart_id,
        }
    }
    api_url = '{0}/v2/flows/customer-address/entries'.format(API_BASE_URL)

    response = requests.post(url=api_url, headers=headers, data=payload)
    response.raise_for_status()
