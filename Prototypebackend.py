from dmi_open_data import DMIOpenDataClient, Parameter

# Initialize the DMIOpenDataClient with your API key
api_key = 'e2073b52-43bb-4d7f-88aa-7627598dd294'  # Replace with your API key
client = DMIOpenDataClient(api_key)

# Function to get temperature for a specific station using an alias
def get_temperature(station_name):
    # Get all stations
    stations = client.get_stations()

    matching_station = next((station for station in stations if station['properties']['name'].lower() == station_name.lower()), None)

    if matching_station is not None:
        # Get the station ID for the selected station
        station_id = matching_station['properties']['stationId']

        # Use the station ID to get temperature observations
        observations = client.get_observations(
            parameter=Parameter.TempDry,
            station_id=station_id,
            limit=1
        )

        if observations:
            # Access the temperature value within the 'properties' field
            temperature = observations[0]['properties']['value']
            return f"{station_name}: {temperature} °C"
        else:
            return f"No temperature observations found for {station_name} station."
    else:
        return f"Station '{station_name}' not found."

# Use the following lines if you want to run the script independently
if __name__ == "__main__":
    station_name = input("Enter the station name: ")
    print(get_temperature(station_name))
