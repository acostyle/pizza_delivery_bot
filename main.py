import json
import os
from urllib.parse import urlparse
import requests
from slugify import slugify

from moltin import get_auth_token, create_product, link_picture_to_product, create_picture


def download_picture(product):
    os.makedirs('./pictures', exist_ok=True)
    product_name = slugify(product['name'])

    picture_url = product['product_image']['url']
    parsed_url = urlparse(picture_url)
    file_extension = os.path.splitext(
        os.path.basename(parsed_url.path)
    )[-1]

    picture_name = '{0}{1}'.format(product_name, file_extension)
    picture_path = os.path.join('pictures', picture_name)

    response = requests.get(picture_url)
    response.raise_for_status()
    with open(picture_path, 'wb') as picture_file:
        picture_file.write(response.content)
    
    return picture_path


def main():
    with open('address.json', 'r') as address_file:
        addresses = json.load(address_file)

    with open('menu.json', 'r') as menu_file:
        menu = json.load(menu_file)

    access_token, expire_time = get_auth_token()
    
    product = menu[0]
    picture = download_picture(product)
    picture_id = create_picture(access_token, picture)

    product_id = create_product(access_token, product)
    link_picture_to_product(access_token, product_id, picture_id)




if __name__ == '__main__':
    main()
