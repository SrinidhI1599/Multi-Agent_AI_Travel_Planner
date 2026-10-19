import requests


def get_weather(city):

    try:

        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data["current_condition"][0]

        return {
            "temp": current["temp_C"],
            "condition": current["weatherDesc"][0]["value"]
        }

    except Exception as e:

        print(f"Weather API Error: {e}")

        return {
            "temp": "N/A",
            "condition": "Weather data unavailable"
        }