import json
from bs4 import BeautifulSoup
import requests
import os
import tkinter as tk

urlBase = "https://www.timeanddate.com/weather/"
SETTINGS_FILE = 'settings.txt'
cities = {
    "New York": "usa/new-york",
    "Boston": "usa/boston",
    "Washington DC": "usa/washington-dc",
    "Tokyo": "japan/tokyo",
    "London": "uk/london",
    "Paris": "france/paris",
    "Istanbul": "turkey/izmir",
    "Izmir": "turkey/izmir",
    "Ankara": "turkey/izmir",
    "Rome": "italy/rome",
    "Naples": "italy/naples",
    "Berlin": "germany/berlin",
    "Munich": "germany/munich"
}


class WeatherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Weather App")
        self.master.geometry("600x600")
        self.master.configure(bg="#f0f0f0")  # Set background color

        # Set modern font
        self.font_style = ("Helvetica", 12)

        # Settings
        settings = self.get_saved_settings()
        self.var = tk.StringVar(master, settings['city'])
        self.use_fahrenheit = tk.BooleanVar(master, settings['use_fahrenheit'])
        self.use_mph = tk.BooleanVar(master, settings['use_mph'])

        # Check buttons with modern styling
        self.check_fahrenheit = tk.Checkbutton(
            master, text="Use Fahrenheit", variable=self.use_fahrenheit, bg="#f0f0f0", fg="black",
            font=self.font_style
        )
        self.check_fahrenheit.pack()

        self.check_mph = tk.Checkbutton(
            master, text="Use Mph", variable=self.use_mph, bg="#f0f0f0", fg="black",
            font=self.font_style
        )
        self.check_mph.pack()

        # Tracing variable changes
        self.var.trace("w", self.update_weather_info_callback)
        self.use_fahrenheit.trace("w", self.update_weather_info_callback)
        self.use_mph.trace("w", self.update_weather_info_callback)

        # Dropdown menu with modern styling
        self.drop = tk.OptionMenu(master, self.var, *cities.keys())
        self.drop.config(bg="#f0f0f0", font=self.font_style)
        self.drop.pack()

        # Label Widgets
        self.weather_icon_label = tk.Label(master, bg="#f0f0f0")
        self.weather_icon_label.pack()

        self.weather_status = tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style)
        self.weather_status.pack()

        self.temperature = tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style)
        self.temperature.pack()

        self.feels_like = tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style)
        self.feels_like.pack()

        self.forecast = tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style)
        self.forecast.pack()

        self.wind = tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style)
        self.wind.pack()

        # Future weather info for next 3 days
        self.future_info = [tk.Label(master, bg="#f0f0f0", fg="black", font=self.font_style) for _ in range(3)]
        for label in self.future_info:
            label.pack()

        self.update_weather_info(self.var.get())

    def update_weather_info(self, value):
        try:
            url = urlBase + cities[value]
            print(f"Fetching data from: {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Weather Temperature
            temperature_div = soup.find('div', class_='h2')
            if temperature_div is not None:
                temperature = temperature_div.text.strip().split()[0]
                if self.use_fahrenheit.get():
                    temperature = (float(temperature) * 9 / 5) + 32
                    temperature = round(temperature, 2)
                    self.temperature['text'] = f"Temperature in {value} is {temperature} °F"
                else:
                    self.temperature['text'] = f"Temperature in {value} is {temperature} °C"
                print(self.temperature['text'])
            else:
                self.temperature['text'] = f"Could not find temperature data for {value}"
                print(f"No temperature data found for {value} at {url}")

            # Feels Like
            info_div = soup.find('div', id='qlook')
            if info_div:
                info_p_tags = info_div.find_all('p')
                feels_like_line = None
                for p_tag in info_p_tags:
                    if "Feels Like" in p_tag.text:
                        feels_like_line = p_tag.text
                        break
                if feels_like_line:
                    feels_like_temp = feels_like_line.split()[2]
                    if self.use_fahrenheit.get():
                        feels_like_temp = (float(feels_like_temp) * 9 / 5) + 32
                        feels_like_temp = round(feels_like_temp, 2)
                        self.feels_like['text'] = f"Temperature Feels Like: {feels_like_temp} °F"
                    else:
                        self.feels_like['text'] = f"Temperature Feels Like: {feels_like_temp} °C"
                    print(self.feels_like['text'])

            # Wind
            info_div = soup.find('div', id='qlook')
            if info_div:
                info_p_tags = info_div.find_all('p')
                wind_line = None
                for p_tag in info_p_tags:
                    contents = p_tag.contents
                    for content in contents:
                        if "Wind: " in str(content):
                            wind_line = str(content)
                            break
                if wind_line:
                    wind_speed_str = wind_line.split()[1]
                    if wind_speed_str.lower() != 'no':
                        try:
                            wind_speed = float(wind_speed_str)
                            if self.use_mph.get():
                                wind_speed *= 0.621371  # convert km/h to mph
                            self.wind[
                                'text'] = f"Wind speed in {value} is {wind_speed:.1f} {'mph' if self.use_mph.get() else 'km/h'}"
                        except ValueError:
                            self.wind['text'] = f"Invalid wind speed value for {value}"
                    else:
                        self.wind['text'] = f"No wind information available for {value}"
                else:
                    self.wind['text'] = f"No wind information available for {value}"
            else:
                self.wind['text'] = f"No wind information available for {value}"

            # Forecast
            info_div = soup.find('div', id='qlook')
            if info_div:
                info_p_tags = info_div.find_all('p')
                forecast_line = None
                for p_tag in info_p_tags:
                    span_tags = p_tag.find_all('span', title="High and low forecasted temperature today")
                    if span_tags:
                        forecast_line = span_tags[0].text
                        break
                if forecast_line:
                    forecast_temps = forecast_line.split(': ')[1]
                    if forecast_temps == 'N/A':
                        self.forecast['text'] = f"Forecast for {value} is not available"
                    else:
                        high_temp, low_temp = map(float, forecast_temps.replace('\xa0°C', '').split(' / '))
                        if self.use_fahrenheit.get():
                            high_temp = self.convert_celsius_to_fahrenheit(high_temp)
                            low_temp = self.convert_celsius_to_fahrenheit(low_temp)
                        self.forecast[
                            'text'] = f"Forecast for {value} - High: {high_temp} °{'F' if self.use_fahrenheit.get() else 'C'}, Low: {low_temp} °{'F' if self.use_fahrenheit.get() else 'C'}"

            # Weather Status
            weather_status = soup.find('p').get_text().strip()
            if weather_status:
                self.weather_status['text'] = f"Weather in {value} is {weather_status}"
                print(weather_status)
                # Set the weather icon
                icon_path = self.get_icon_name(weather_status)
                if icon_path:
                    image = tk.PhotoImage(file=icon_path)
                    self.weather_icon_label.config(image=image)
                    self.weather_icon_label.image = image  # keep a reference

            # Future weather info for next 3 days
            future_tags = soup.find_all('td', class_='wa')[1:4]
            for i in range(3):
                if i < len(future_tags) and future_tags[i]:
                    future_p_tag = future_tags[i].find('p')
                    if future_p_tag:
                        future_temps = future_p_tag.text.split(' / ')
                        if len(future_temps) == 2:
                            high_temp = int(''.join(filter(str.isdigit, future_temps[0])))
                            low_temp = int(''.join(filter(str.isdigit, future_temps[1])))
                        if self.use_fahrenheit.get():
                            high_temp = self.convert_celsius_to_fahrenheit(high_temp)
                            low_temp = self.convert_celsius_to_fahrenheit(low_temp)
                        self.future_info[i][
                            'text'] = f"Temperature in {value} after {i + 1} day will be {high_temp} / {low_temp} °{'F' if self.use_fahrenheit.get() else 'C'}"
                    else:
                        print("Unavailable data.")
                else:
                    print("Unavailable data.")

        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Error", "Cannot connect to the internet")
            print(f"Exception while connecting to the internet: {str(e)}")

    def convert_celsius_to_fahrenheit(self, celsius):
        return (celsius * 9 / 5) + 32

    def update_weather_info_callback(self, *args):
        self.update_weather_info(self.var.get())

    def get_saved_settings(self):
        if os.path.isfile(SETTINGS_FILE) and os.stat(SETTINGS_FILE).st_size != 0:
            with open(SETTINGS_FILE, 'r') as f:
                try:
                    settings = json.load(f)
                    return settings
                except json.JSONDecodeError:
                    return self.default_settings()
        else:
            return self.default_settings()

    def default_settings(self):
        return {
            'city': list(cities.keys())[0],
            'use_fahrenheit': 0,
            'use_mph': 0
        }

    def save_settings(self):
        settings = {
            'city': self.var.get(),
            'use_fahrenheit': self.use_fahrenheit.get(),
            'use_mph': self.use_mph.get()
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def get_icon_name(self, weather_status):
        # Lowercase the status and replace spaces with underscores
        icon_name = weather_status.lower().replace(" ", "_")
        # Check if the icon file exists
        if os.path.isfile(f"icons/{icon_name}.png"):  # Fix missing .png extension
            print(icon_name)
            return f"icons/{icon_name}.png"  # Fix missing .png extension


root = tk.Tk()
app = WeatherApp(root)
root.protocol("WM_DELETE_WINDOW", app.save_settings)
root.mainloop()
