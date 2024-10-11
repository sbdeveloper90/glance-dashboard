from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime

def json_to_html_wttr(json_str):
    # Load the JSON string into a Python object
    data = json.loads(json_str)

    # Start HTML string
    html = "<div id=container_wttr>"

    # Nearest Area
    html += "<h2 class='color-primary'>Nearest Area</h2><table border='1'><thead><tr><th>Area</th><th>Country</th><th>Region</th><th>Latitude</th><th>Longitude</th><th>Population</th></tr></thead>"
    html += "<tbody>"
    for area in data.get('nearest_area', []):
        html += f"<tr><td>{area['areaName'][0]['value']}</td><td>{area['country'][0]['value']}</td><td>{area['region'][0]['value']}</td><td>{area['latitude']}</td><td>{area['longitude']}</td><td>{area['population']}</td></tr>"
    html += "</tbody></table><br>"

    # Current Condition
    html += "<h2 class='color-primary'>Current Condition</h2><table border='1'><thead><tr><th>Temp (C)</th><th>Feels Like (C)</th><th>Weather</th><th>Humidity</th><th>Pressure</th><th>Wind</th></tr></thead>"
    html += "<tbody>"
    for condition in data.get('current_condition', []):
        html += f"<tr><td>{condition['temp_C']}°C</td><td>{condition['FeelsLikeC']}°C</td><td>{condition['weatherDesc'][0]['value']}</td><td>{condition['humidity']}%</td><td>{condition['pressure']} hPa</td><td>{condition['windspeedKmph']} km/h {condition['winddir16Point']}</td></tr>"
    html += "</tbody></table><br>"

    # Weather Forecasts
    html += "<h2 class='color-primary'>Weather Forecast</h2>"
    for forecast in data.get('weather', []):
        html += f"<h3>Date: {forecast['date']}</h3>"
        html += f"<p>Max Temp: {forecast['maxtempC']}°C, Min Temp: {forecast['mintempC']}°C, Sun Hours: {forecast['sunHour']}h</p>"
        html += "<table border='1'><thead><tr><th>Time</th><th>Temp (C)</th><th>Feels Like (C)</th><th>Weather</th><th>Wind</th><th>Humidity</th><th>Pressure</th></tr></thead>"
        html += "<tbody>"
        for hourly in forecast.get('hourly', []):
            html += f"<tr><td>{hourly['time']}h</td><td>{hourly['tempC']}°C</td><td>{hourly['FeelsLikeC']}°C</td><td>{hourly['weatherDesc'][0]['value']}</td><td>{hourly['windspeedKmph']} km/h {hourly['winddir16Point']}</td><td>{hourly['humidity']}%</td><td>{hourly['pressure']} hPa</td></tr>"
        html += "</tbody></table><br>"

    # Astronomy Information
    html += "<h2 class='color-primary'>Astronomy Information</h2>"
    html += "<tbody>"
    for forecast in data.get('weather', []):
        for astronomy in forecast.get('astronomy', []):
            html += f"<h3>Date: {forecast['date']}</h3>"
            html += "<table border='1'><thead><tr><th>Sunrise</th><th>Sunset</th><th>Moonrise</th><th>Moonset</th><th>Moon Phase</th></tr></thead>"
            html += f"<tr><td>{astronomy['sunrise']}</td><td>{astronomy['sunset']}</td><td>{astronomy['moonrise']}</td><td>{astronomy['moonset']}</td><td>{astronomy['moon_phase']}</td></tr>"
            html += "</tbody></table><br>"

    # End HTML string
    html += "</div>"

    return html

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the query parameters from the URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # To access the "flag" parameter:
        flag = query_params.get('flag', [''])[0]    # Default to empty string if 'flag' is not present
        if flag == "wttr":
            location_value = query_params.get('location', [''])[0]

            # Use the location_value in the logic
            url = f'https://wttr.in/{location_value}?format=j1'

            try:
                # Perform the GET request
                response = requests.get(url)
                response_data = response.text

                # Respond to the client with the fetched data
                self.send_response(200)
                self.send_header('Widget-Title', 'wttr.in')
                self.send_header('Widget-Content-Type', 'html')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                html_response = json_to_html_wttr(response_data)
                self.wfile.write(html_response.encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        elif flag == 'iss':
            url_iss = f'http://api.open-notify.org/iss-now.json'
            url_astros = f'http://api.open-notify.org/astros.json'

            try:
                # Perform the GET request
                response_iss = requests.get(url_iss)
                response_iss_data = response_iss.text
                data_iss = json.loads(response_iss_data)

                response_astros = requests.get(url_astros)
                response_astros_data = response_astros.text
                data_astros = json.loads(response_astros_data)

                # Respond to the client with the fetched data
                self.send_response(200)
                self.send_header('Widget-Title', 'iss')
                self.send_header('Widget-Content-Type', 'html')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                html_response = f'''
                <h2 class="color-primary">ISS Position</h2>
                <table border="1">
                    <thead><tr><th>Datetime</th><th>Message</th><th>Latitude</th><th>Longitude</th></tr></thead>
                    <tbody><tr><td>{datetime.fromtimestamp(data_iss.get("timestamp", []))}</td><td>{data_iss.get("message", [])}</td><td>{data_iss.get("iss_position", []).get("latitude", [])}</td><td>{data_iss.get("iss_position", []).get("longitude", [])}</td></tr></tbody>
                </table><br>

                <h2 class="color-primary">People In Space Now: {data_astros.get("number", [])}</h2>
                <table border='1'><thead><tr><th>Name</th><th>Craft</th></tr></thead><tbody>
                '''

                for astronaut in data_astros.get("people", []):
                    html_response += f'<tr><td>{astronaut["name"]}</td><td>{astronaut["craft"]}</td></tr>'

                html_response += f'''
                </tbody></table><br>
                '''
                self.wfile.write(html_response.encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"WARNING! No 'flag' set.".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=12345):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
