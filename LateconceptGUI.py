import tkinter as tk
import tkinter.messagebox
import customtkinter
from dmi_open_data import DMIOpenDataClient, Parameter
from tkintermapview import TkinterMapView
import requests
import threading
from tkdial import ScrollKnob

# Initialize the DMIOpenDataClient with your API key
api_key = 'e2073b52-43bb-4d7f-88aa-7627598dd294'  # Replace with your API key
client = DMIOpenDataClient(api_key)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "green" (standard), "green", "dark-blue"


class WeatherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DMI Vejr App")
        self.geometry(f"{1200}x600")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DMI Vejr", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create a ComboBox for station selection
        self.station_var = customtkinter.StringVar(value="Vælg Station")
        self.station_combobox = customtkinter.CTkComboBox(self.sidebar_frame, values=[], command=self.get_weather, variable=self.station_var)
        self.station_combobox.grid(row=1, column=0, padx=20, pady=10)

        self.get_weather_button = customtkinter.CTkButton(self.sidebar_frame, text="Få Vejr", command=self.get_weather)
        self.get_weather_button.grid(row=2, column=0, padx=20, pady=10)

        self.weather_display = customtkinter.CTkLabel(self.sidebar_frame, text="", font=customtkinter.CTkFont(size=30))  # Increased font size
        self.weather_display.grid(row=3, column=0, padx=20, pady=10)

        # Add label above the ScrollKnob
        self.scrollknob_label = customtkinter.CTkLabel(self.sidebar_frame, text="Lavere procent = mere magelig", font=customtkinter.CTkFont(size=12, weight="normal"))
        self.scrollknob_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        self.temperature_knob = ScrollKnob(self.sidebar_frame, start=0, end=50, steps=1)
        self.temperature_knob.grid(row=5, column=0, padx=20, pady=(0, 10))

        # Create map widget
        self.map_widget = TkinterMapView(self, width=800, height=600)
        self.map_widget.grid(row=0, column=1, rowspan=4, sticky="nsew")

        # Hide main window until loading is done
        self.withdraw()

        # Populate station combobox and show map in background threads
        self.populate_stations_thread = threading.Thread(target=self.populate_stations_and_show_map)
        self.populate_stations_thread.start()

    def populate_stations_and_show_map(self):
        # Load stations
        stations = client.get_stations()
        valid_stations = []  # List to store unique and valid stations
        seen_stations = set()  # Set to keep track of seen station names
        for station in stations:
            station_name = station['properties']['name']
            if station_name not in seen_stations:
                seen_stations.add(station_name)
                valid_stations.append(station_name)
        if valid_stations:
            self.station_combobox.configure(values=sorted(valid_stations))

        # Load map
        self.show_map()

        # Once loading is done, show main window
        self.deiconify()

    def show_map(self):
        # Simulate loading time for the map
        import time
        time.sleep(2)  # Adjust this value as needed for your loading time

    def get_weather(self, *args):
        station_name = self.station_var.get()
        if station_name and station_name != "Vælg Station":
            error_message, temperature, wind_speed = self.fetch_weather(station_name)
            if temperature is not None and wind_speed is not None:  # Check if both temperature and wind speed are not None
                self.weather_display.configure(text=f" {temperature} °C\n {wind_speed} m/s")
                self.temperature_knob.set(temperature)
            else:
                tkinter.messagebox.showwarning("Advarsel", error_message)
            # Show location on map
            self.show_location_on_map(station_name)
        else:
            tkinter.messagebox.showwarning("Advarsel", "Venligst vælg en station.")

    def fetch_weather(self, station_name):
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

    def show_location_on_map(self, location):
        # Convert location to coordinates (latitude, longitude)
        coordinates = self.get_coordinates_from_location(location)
        if coordinates:
            # Set map position
            self.map_widget.set_position(*coordinates)
        else:
            # Attempt to get coordinates based on station name
            coordinates = self.get_coordinates_from_location_based_on_name(location)
            if coordinates:
                # Set map position based on station name
                self.map_widget.set_position(*coordinates)
            else:
                # If neither coordinates nor station name coordinates are found, display a warning
                tkinter.messagebox.showwarning("Warning", f"Location '{location}' not found on the map.")

    def get_coordinates_from_location(self, location):
        # Use a geocoding service to get coordinates from the station name
        # Here, I'm using the OpenStreetMap Nominatim API as an example
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json"
        }
        response = requests.get(base_url, params=params)
        if response.ok:
            data = response.json()
            if data:
                # Assuming the first result is the correct one
                latitude = float(data[0]['lat'])
                longitude = float(data[0]['lon'])
                return latitude, longitude
        return None

    def get_coordinates_from_location_based_on_name(self, location):
        # Attempt to get coordinates from station name directly
        stations = client.get_stations()
        matching_station = next(
            (station for station in stations if station['properties']['name'].lower() == location.lower()), None)
        if matching_station:
            latitude = float(matching_station['geometry']['coordinates'][1])
            longitude = float(matching_station['geometry']['coordinates'][0])
            return latitude, longitude
        return None


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
