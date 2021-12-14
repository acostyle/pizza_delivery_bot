import requests

from geopy.distance import distance

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    return lon, lat


def min_distance(entry):
    return entry['distance']


def get_closest_entry(current_position, entries):
    result = []

    for entry in entries:
        entry_id = entry['id']
        entry_position = entry['longitude'], entry['latitude']

        distance_between_positions = distance(
            current_position,
            entry_position,
        ).km

        result.append(
            {
                'id': entry_id,
                'distance': distance_between_positions,
            }
        )

    return min(result, key=min_distance)
