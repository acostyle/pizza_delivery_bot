"""Functions for flow actions."""

import requests
from slugify import slugify

from .settings import API_BASE_URL


def create_flow(access_token, name, description):
    """
    Create flow.

    Args:
        access_token: required to get access to the API.
        name: specifies the name of the flow.
        description: specifies the description for the flow.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'flow',
            'name': name,
            'slug': slugify(name),
            'description': description,
            'enabled': True,
        },
    }

    api_url = '{0}/v2/flows'.format(API_BASE_URL)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()


def create_flow_field(access_token, name, description, flow_id):
    """
    Create flow fields.

    Args:
        access_token: required to get access to the API.
        name: specifies the name of the field.
        description: specifies the description for this field.
        flow_id: id for the flow to create the field.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'field',
            'name': name,
            'slug': slugify(name),
            'field_type': 'string',
            'description': description,
            'required': True,
            'default': '',
            'enabled': True,
            'relationships': {
                'flow': {
                    'data': {
                        'type': 'flow',
                        'id': flow_id,
                    },
                },
            },
        },
    }

    api_url = '{0}/v2/fields'.format(API_BASE_URL)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()


def create_entry(access_token, entry_data, flow_slug):
    """
    Create entries in flow.

    Args:
        access_token: required to get access to the API.
        entry_data: piece of information to create entry with needed data.
        flow_slug: slug for the flow to create an entry.
    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'entry',
            'address': entry_data['address']['full'],
            'alias': entry_data['alias'],
            'longitude': entry_data['coordinates']['lon'],
            'latitude': entry_data['coordinates']['lat'],
        },
    }

    api_url = '{0}/v2/flows/{1}/entries'.format(API_BASE_URL, flow_slug)
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()


def get_entries(access_token, flow_slug):
    """
    Get all entries of chosen flow.

    Returns:
        return: data about all entries.

    Args:
        access_token: required to get access to the API.
        flow_slug: specifies the slug of the flow.

    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/flows/{1}/entries'.format(API_BASE_URL, flow_slug)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_entry(access_token, flow_slug, entry_id):
    """
    Get one entry of chosen flow.

    Returns:
        return: data about entry.

    Args:
        access_token: required to get access to the API.
        flow_slug: specifies the slug of the flow.
        entry_id: specifies an entry to return data.

    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/flows/{1}/entries/{2}'.format(
        API_BASE_URL,
        flow_slug,
        entry_id,
    )
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_flow(access_token, flow_id):
    """
    Get flow.

    Returns:
        return: data about flow.

    Args:
        access_token: required to get access to the API.
        flow_id: specifies the id of the flow.

    """
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
    }

    api_url = '{0}/v2/flows/{1}'.format(API_BASE_URL, flow_id)
    response = requests.get(url=api_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']
