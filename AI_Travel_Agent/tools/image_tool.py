import os
import requests

from dotenv import load_dotenv

load_dotenv()


def search_destination_image(city):

    access_key = os.getenv(
        "UNSPLASH_ACCESS_KEY"
    )

    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": f"{city} tourist attraction",
        "per_page": 1
    }

    headers = {
        "Authorization":
        f"Client-ID {access_key}"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    if response.status_code != 200:
        return None

    data = response.json()

    if data["results"]:

        return data["results"][0]["urls"]["regular"]

    return None