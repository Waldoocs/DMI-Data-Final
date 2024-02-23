import tkinter
import tkinter.messagebox
import customtkinter
from dmi_open_data import DMIOpenDataClient, Parameter
from tkintermapview import TkinterMapView
import requests

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
        self.geometry(f"{1200}x{600}")

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

        self.weather_display = customtkinter.CTkLabel(self.sidebar_frame, text="", font=customtkinter.CTkFont(size=12))
        self.weather_display.grid(row=3, column=0, padx=20, pady=10)

        # Create map widget
        self.map_widget = TkinterMapView(self, width=800, height=600)
        self.map_widget.grid(row=0, column=1, rowspan=4, sticky="nsew")

        # Populate station combobox
        self.populate_stations()

    def populate_stations(self):
        stations = client.get_stations()
        if stations:
            station_names = sorted([station['properties']['name'] for station in stations])
            self.station_combobox.configure(values=station_names)

    def get_weather(self, *args):
        station_name = self.station_var.get()
        if station_name and station_name != "Vælg Station":
            weather_info = self.fetch_weather(station_name)
            self.weather_display.configure(text=weather_info)
            # Show location on map
            self.show_location_on_map(station_name)
        else:
            tkinter.messagebox.showwarning("Advarsel", "Venligst vælg en station.")

    def fetch_weather(self, station_name):
        stations = client.get_stations()
        matching_station = next((station for station in stations if station['properties']['name'].lower() == station_name.lower()), None)
        if matching_station:
            station_id = matching_station['properties']['stationId']
            observations = client.get_observations(parameter=Parameter.TempDry, station_id=station_id, limit=1)
            if observations:
                temperature = observations[0]['properties']['value']
                return f"Temperatur ved {station_name}: er {temperature} °C"
            else:
                return f"Ingen temperaturobservationer fundet for {station_name} station."
        else:
            return f"Station '{station_name}' blev ikke fundet."

    def show_location_on_map(self, location):
        # Convert location to coordinates (latitude, longitude)
        coordinates = self.get_coordinates_from_location(location)
        if coordinates:
            # Set map position
            self.map_widget.set_position(*coordinates)
        else:
            tkinter.messagebox.showwarning("Advarsel", "Lokation blev ikke fundet på kortet.")

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


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
