from agents.weather import WeatherAgent
from agents.hotels import HotelAgent
from agents.attraction import AttractionAgent
from agents.budget import BudgetAgent
from agents.itinerary import ItineraryAgent
from agents.image import ImageAgent
from agents.travel import TravelAgent


class PlannerAgent:

    def __init__(self):

        self.weather_agent = WeatherAgent()

        self.hotel_agent = HotelAgent()

        self.attraction_agent = AttractionAgent()

        self.budget_agent = BudgetAgent()

        self.itinerary_agent = ItineraryAgent()

        self.image_agent = ImageAgent()

        self.travel_agent = TravelAgent()

    def run(
        self,
        city,
        days,
        total_budget,
        origin="",
        travel_date=None,
        travel_mode="all",
        travel_class="3A",
        travellers=1
    ):

        weather = self.weather_agent.run(city)

        hotels = self.hotel_agent.run(city)

        attractions = self.attraction_agent.run(city)

        # Travel is optional: only searched when an origin is given
        travel = {"options": {}, "best": None, "cost": 0}

        if origin:
            travel = self.travel_agent.run(
                origin,
                city,
                travel_date,
                travel_mode,
                travel_class,
                travellers
            )

        budget_info = self.budget_agent.run(
            days,
            total_budget,
            travel["cost"]
        )

        destination_image = self.image_agent.run(
            city
        )

        itinerary = self.itinerary_agent.run(
            city,
            days,
            attractions,
            hotels,
            weather,
            budget_info,
            travel["best"]
        )

        return {
            "weather": weather,
            "hotels": hotels,
            "travel": travel["options"],
            "best_travel": travel["best"],
            "attractions": attractions,
            "budget": budget_info,
            "itinerary": itinerary,
            "background_image": destination_image
        }

    def update_travel(self, result, travel_mode, travel_class):
        """
        Re-do ONLY the parts that depend on the travel mode:
        travel options -> budget -> itinerary.

        Weather, hotels, attractions and the destination image are
        reused from the existing result, so switching mode is quick.
        """

        inp = result["inputs"]

        travel = self.travel_agent.run(
            inp["origin"],
            inp["city"],
            inp["travel_date"],
            travel_mode,
            travel_class,
            inp["travellers"]
        )

        budget_info = self.budget_agent.run(
            inp["days"],
            result["budget"]["user_budget"],
            travel["cost"]
        )

        itinerary = self.itinerary_agent.run(
            inp["city"],
            inp["days"],
            result["attractions"],
            result["hotels"],
            result["weather"],
            budget_info,
            travel["best"]
        )

        updated = dict(result)

        updated.update(
            {
                "travel": travel["options"],
                "best_travel": travel["best"],
                "budget": budget_info,
                "itinerary": itinerary,
                "inputs": {
                    **inp,
                    "travel_mode": travel_mode,
                    "travel_class": travel_class,
                },
            }
        )

        return updated