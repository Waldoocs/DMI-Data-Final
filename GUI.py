import PySimpleGUI as sg
from latest_temperature import get_temperature, client  # Assuming your existing code is in a file named latest_temperature.py

# PySimpleGUI layout
layout = [
    [sg.Text("Enter the station name:"), sg.InputText(key='station_name', enable_events=True), sg.Listbox(values=[], size=(20, 5), key='-LIST-', enable_events=True)],
    [sg.Button('Get Weather'), sg.Button('Exit')],
    [sg.Text(size=(40, 1), key='output')],
]

# Create the window
window = sg.Window('Weather App', layout)

# Event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Get Weather':
        station_name = values['station_name']
        weather_info = get_temperature(station_name)
        window['output'].update(weather_info)
    elif event == 'station_name':
        # Update autocomplete suggestions based on the current input
        current_input = values['station_name']
        suggestions_set = set()

        for station in client.get_stations():
            station_name_lower = station['properties']['name'].lower()
            # Check if the current input matches the beginning of the station name
            if station_name_lower.startswith(current_input.lower()):
                suggestions_set.add(station['properties']['name'])

        suggestions = list(suggestions_set)
        window['-LIST-'].update(values=suggestions)

    elif event == '-LIST-':
        # If a suggestion is clicked, update the input field
        selected_suggestion = values['-LIST-'][0]
        window['station_name'].update(value=selected_suggestion)

# Close the window
window.close()
