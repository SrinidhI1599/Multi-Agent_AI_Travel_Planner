from tools.hotel_tool import search_hotels


class HotelAgent:

    def run(self, city):
        return search_hotels(city)