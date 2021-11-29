import os
from urllib.parse import urlparse

import requests
from slugify import slugify


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


def main():
    pass


if __name__ == '__main__':
    main()
