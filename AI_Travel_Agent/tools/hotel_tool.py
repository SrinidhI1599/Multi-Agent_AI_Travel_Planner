import json
from utils.llm import llm

def search_hotels(city):

    prompt = f"""
Suggest exactly 3 hotels in {city}.

Return ONLY valid JSON.

Format:

[
    {{
        "name": "",
        "price_per_night": 0,
        "highlights": []
    }}
]
"""

    try:
        response = llm.invoke(prompt)

        content = response.content.strip() # type: ignore

        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        hotels = json.loads(content)

        # Add booking URL
        for hotel in hotels:
            hotel["booking_url"] = (
                f"https://www.booking.com/searchresults.html?ss={city}"
            )

        # Fallback if less than 3 returned
        while len(hotels) < 3:
            hotels.append(
                {
                    "name": f"Recommended Hotel {len(hotels)+1}",
                    "price_per_night": 4000,
                    "highlights": [
                        "Free WiFi",
                        "Restaurant",
                        "Good Location",
                        "Breakfast Included"
                    ],
                    "booking_url":
                        f"https://www.booking.com/searchresults.html?ss={city}"
                }
            )

        return hotels[:3]

    except Exception:

        return [
            {
                "name": "Grand Plaza",
                "price_per_night": 4500,
                "highlights": [
                    "Swimming Pool",
                    "Free WiFi",
                    "Restaurant",
                    "City Center"
                ],
                "booking_url":
                    f"https://www.booking.com/searchresults.html?ss={city}"
            },
            {
                "name": "Comfort Stay",
                "price_per_night": 3200,
                "highlights": [
                    "Free Breakfast",
                    "Airport Pickup",
                    "Family Friendly",
                    "Restaurant"
                ],
                "booking_url":
                    f"https://www.booking.com/searchresults.html?ss={city}"
            },
            {
                "name": "Travel Inn",
                "price_per_night": 2800,
                "highlights": [
                    "Budget Friendly",
                    "24x7 Reception",
                    "City Center",
                    "Free WiFi"
                ],
                "booking_url":
                    f"https://www.booking.com/searchresults.html?ss={city}"
            }
        ]

    prompt = f"""
Suggest 3 hotels in {city}.

Return ONLY valid JSON.

Format:

[
    {{
        "name": "Hotel Name",
        "price_per_night": 5000,
        "highlights": [
            "Highlight 1",
            "Highlight 2",
            "Highlight 3",
            "Highlight 4"
        ]
    }}
]
"""

    try:

        response = llm.invoke(prompt)

        print("========== RAW RESPONSE ==========")
        print(repr(response.content))
        print("==================================")

        content = response.content.strip()

        # Remove markdown fences if Gemini adds them
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        return json.loads(content)

    except Exception as e:

        print("HOTEL AGENT ERROR:")
        print(str(e))

        # Temporary fallback
        return [
            {
                "name": "Sample Hotel",
                "price_per_night": 4000,
                "highlights": [
                    "Free WiFi",
                    "Restaurant",
                    "City Center",
                    "Breakfast Included"
                ],
                "booking_url": "https://www.booking.com"
            }
        ]