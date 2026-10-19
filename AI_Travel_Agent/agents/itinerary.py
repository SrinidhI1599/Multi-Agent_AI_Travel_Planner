from utils.llm import llm


class ItineraryAgent:

    def run(
        self,
        city,
        days,
        attractions,
        hotels,
        weather,
        budget,
        travel=None
    ):

        hotel_text = "\n".join(
            [
                f"""
Hotel: {hotel['name']}
Cost Per Night: ₹{hotel['price_per_night']}
Highlights: {', '.join(hotel['highlights'])}
"""
                for hotel in hotels
            ]
        )

        if travel:
            travel_text = (
                f"{travel['mode'].title()}: {travel['name']} "
                f"{travel['number']}, "
                f"{travel['departure']} -> {travel['arrival']} "
                f"(about ₹{travel['fare']} "
                f"{'per vehicle' if travel.get('per_vehicle') else 'per person'}"
                f", one way)"
            )
        else:
            travel_text = "Not searched"

        prompt = f"""
Create a detailed {days}-day travel itinerary.

Destination:
{city}

Recommended Hotels:

{hotel_text}

Chosen Travel Option (lowest total cost found):
{travel_text}

Weather:
{weather}

Tourist Attractions:
{', '.join(attractions)}

Budget Details:

User Budget:
₹{budget['user_budget']}

Estimated Trip Cost:
₹{budget['estimated_total']}

Budget Status:
{"Exceeded" if budget["exceeded"] else "Within Budget"}

Instructions:

1. Select the best hotel from the hotel list.
2. Explain why that hotel is recommended.
3. Mention its approximate cost per night.
4. Mention key hotel highlights.
5. Create a detailed day-wise itinerary.
6. Include food recommendations.
7. Include local transportation suggestions.
8. Include travel tips.
9. Mention whether the trip stays within budget.
10. Provide an estimated expense summary.
11. If a travel option is given, mention how to reach the destination with it.

Format the response with clear headings.
"""

        response = llm.invoke(prompt)

        return response.content