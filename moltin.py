import requests
from environs import Env
from slugify import slugify


env = Env()
env.read_env()

API_BASE_URL = 'https://api.moltin.com'
CLIENT_ID = env.str('CLIENT_ID')
CLIENT_SECRET = env.str('CLIENT_SECRET')


def get_access_token(redis_db):
    # it will be used in the future
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
    headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {
            'type': 'main_image',
            'id': picture_id,
        }
    }

    api_url = '{0}/v2/products/{1}/relationships/main-image'.format(
        API_BASE_URL,
        product_id,
    )
    response = requests.post(url=api_url, headers=headers, json=payload)
    response.raise_for_status()
