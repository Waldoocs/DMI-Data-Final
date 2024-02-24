from dmi_open_data import DMIOpenDataClient, Parameter
import requests

# Initialize the DMIOpenDataClient with your API key
api_key = 'e2073b52-43bb-4d7f-88aa-7627598dd294'  # Replace with your API key
client = DMIOpenDataClient(api_key)


class WeatherBackend:
    @staticmethod
    def get_stations():
        return client.get_stations()

    @staticmethod
    def fetch_weather(station_name):
        stations = client.get_stations()
        matching_station = next(
            (station for station in stations if station['properties']['name'].lower() == station_name.lower()), None)
        if matching_station:
            station_id = matching_station['properties']['stationId']
            # Fetch observations for temperature and wind speed
            temperature_observations = client.get_observations(parameter=Parameter.TempDry, station_id=station_id,
                                                               limit=1)
            wind_speed_observations = client.get_observations(parameter=Parameter.WindSpeed, station_id=station_id,
                                                              limit=1)
            if temperature_observations and wind_speed_observations:
                temperature = temperature_observations[0]['properties']['value']
                wind_speed = wind_speed_observations[0]['properties']['value']
                return "", temperature, wind_speed  # Return temperature and wind speed
            else:
                return f"Ingen observationer fundet for {station_name} station.", None, None
        else:
            return f"Station '{station_name}' blev ikke fundet.", None, None

    @staticmethod
    def get_coordinates_from_location(location):
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json"
        }
        response = requests.get(base_url, params=params)
        if response.ok:
            data = response.json()
            if data:
                latitude = float(data[0]['lat'])
                longitude = float(data[0]['lon'])
                return latitude, longitude
        return None
