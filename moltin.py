import requests
from environs import Env
from slugify import slugify


env = Env()
env.read_env()

API_BASE_URL = 'https://api.moltin.com'
CLIENT_ID = env.str('CLIENT_ID')
CLIENT_SECRET = env.str('CLIENT_SECRET')


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
