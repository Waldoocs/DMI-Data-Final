import tkinter as tk
import tkinter.messagebox
import customtkinter
from tkintermapview import TkinterMapView
import threading
from tkdial import ScrollKnob
from backend import WeatherBackend

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "green" (standard), "green", "dark-blue"


class WeatherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Set the title and geometry of the window
        self.title("DMI Vejr App")
        self.geometry(f"{1200}x600")

        # Set the application icon
        self.iconbitmap('weathericon.ico')

        # Configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DMI Vejr", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.station_var = customtkinter.StringVar(value="Vælg Station")
        self.station_combobox = customtkinter.CTkComboBox(self.sidebar_frame, values=[], command=self.get_weather, variable=self.station_var)
        self.station_combobox.grid(row=1, column=0, padx=20, pady=10)

        self.get_weather_button = customtkinter.CTkButton(self.sidebar_frame, text="Få Vejr", command=self.get_weather)
        self.get_weather_button.grid(row=2, column=0, padx=20, pady=10)

        self.weather_display = customtkinter.CTkLabel(self.sidebar_frame, text="", font=customtkinter.CTkFont(size=30))
        self.weather_display.grid(row=3, column=0, padx=20, pady=10)

        self.scrollknob_label = customtkinter.CTkLabel(self.sidebar_frame, text="Lavere procent = mere magelig", font=customtkinter.CTkFont(size=12, weight="normal"))
        self.scrollknob_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        self.temperature_knob = ScrollKnob(self.sidebar_frame, start=0, end=50, steps=1)
        self.temperature_knob.grid(row=5, column=0, padx=20, pady=(0, 10))

        self.map_widget = TkinterMapView(self, width=800, height=600)
        self.map_widget.grid(row=0, column=1, rowspan=4, sticky="nsew")

        self.withdraw()

        self.populate_stations_thread = threading.Thread(target=self.populate_stations_and_show_map)
        self.populate_stations_thread.start()

    def populate_stations_and_show_map(self):
        stations = WeatherBackend.get_stations()
        valid_stations = []
        seen_stations = set()
        for station in stations:
            station_name = station['properties']['name']
            if station_name not in seen_stations and self.is_station_in_denmark(station):
                seen_stations.add(station_name)
                valid_stations.append(station_name)
        if valid_stations:
            self.station_combobox.configure(values=sorted(valid_stations))
        self.show_map()
        self.deiconify()

    def show_map(self):
        # Set initial map position to Denmark
        denmark_coordinates = (56, 10)  # Latitude and longitude for Denmark
        self.map_widget.set_position(*denmark_coordinates)
        # Set initial zoom level to show the whole of Denmark
        self.map_widget.set_zoom(7)  # Adjust the zoom level as needed
        # Simulate loading time for the map
        import time
        time.sleep(2)

    def get_weather(self, *args):
        station_name = self.station_var.get()
        if station_name and station_name != "Vælg Station":
            error_message, temperature, wind_speed = WeatherBackend.fetch_weather(station_name)
            if temperature is not None and wind_speed is not None:
                self.weather_display.configure(text=f" {temperature} °C\n {wind_speed} m/s")
                self.temperature_knob.set(temperature)
            else:
                tkinter.messagebox.showwarning("Advarsel", error_message)
            self.show_location_on_map(station_name)
        else:
            tkinter.messagebox.showwarning("Advarsel", "Venligst vælg en station.")

    def show_location_on_map(self, location):
        coordinates = WeatherBackend.get_coordinates_from_location(location)
        if coordinates:
            self.map_widget.set_position(*coordinates)
        else:
            coordinates = WeatherBackend.get_coordinates_from_location_based_on_name(location)
            if coordinates:
                self.map_widget.set_position(*coordinates)
            else:
                tkinter.messagebox.showwarning("Warning", f"Location '{location}' not found on the map.")

    def is_station_in_denmark(self, station):
        latitude = float(station['geometry']['coordinates'][1])
        longitude = float(station['geometry']['coordinates'][0])
        if 54.5 <= latitude <= 57.8 and 8 <= longitude <= 15:
            return True
        else:
            return False


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
