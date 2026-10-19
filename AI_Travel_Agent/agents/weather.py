from tools.weather_tool import get_weather


class WeatherAgent:

    def run(self, city):

        weather = get_weather(city)

        return f"""
Temperature: {weather['temp']}°C
Condition: {weather['condition']}
"""