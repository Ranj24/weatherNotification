import requests
import os
from datetime import datetime
from twilio.rest import Client


### Add your API_key from openweather
API_KEY=os.environ.get("WEATHER_API")
Endpoint = "https://api.openweathermap.org/data/2.5/forecast"

### Add your account_sid and auth_token from twilio
account_sid =os.environ.get("ACCOUNT_SID")
auth_token =os.environ.get("AUTH_TOKEN")

### Change lat and long for your location - I used this site to find mine - https://www.latlong.net/
weather_params = {
    "lat": "-35.368083",
    "lon": "149.081713",
    "appid": API_KEY,
    "units": "metric",
}

response=requests.get(Endpoint, params=weather_params)
data = response.json().get("list")

def get_weekday(date) -> str:
    date = datetime.date(*date)
    weekday = date.strftime("%A")
    return weekday

def is_rainy(weather_data):
    return any(condition["id"] < 700 for condition in weather_data)

def laundry_day(data) -> str:
    """Tells you when you can't do laundry."""
    bad_days = set()

    for x in range(len(data)):
        formatted_date = datetime.strptime(data[x]["dt_txt"].split(" ")[0], "%Y-%m-%d").date()
        if is_rainy(data[x]["weather"]):
            bad_days.add(formatted_date)

    new_list = [get_weekday(day) for day in bad_days]

    if len(new_list) == 0:
        return "You can do laundry ANY day in the next 5 days!"
    elif len(new_list) == 1:
        laundry = f"You can NOT do laundry on {new_list[0]}."
        return laundry
    else:
        days_str = ", ".join(new_list[:-1]) + " and " + new_list[-1]
        laundry = f"You can NOT do laundry on {days_str}."
        return laundry

def dress_today(data):
    """Runs on weekdays to suggest an outfit based on temperature and wind."""
    high_temp = float('-inf')
    avg_low_temp = 0
    total_wind = 0
    rainy = False
    for x in range(4):
        high_temp = max(high_temp, data[x]["main"]["temp_max"])
        avg_low_temp += data[x]["main"]["temp_min"]
        total_wind += data[x]["wind"]["speed"]

        rainy = is_rainy(data[x]["weather"])

    avg_temp = avg_low_temp / 4
    avg_wind = total_wind / 4

    ### Change logic here based on your personal preference.
    outfit = ""
    if high_temp >= 26:
        outfit ="Light clothes - shorts/dress"
    elif 26 > high_temp >= 20:
        outfit ="Light jacket"
    elif 15 <= avg_temp <= 19:
        outfit ="Hoodie"
    elif avg_temp <= 15:
        outfit ="Puffer jacket + Gloves"

    if avg_wind > 20:
        outfit = " + Scarf"

    if rainy:
        outfit =" + Umbrella"

    outfit = f"Recommended outfit for today: {outfit}"
    return outfit

today = datetime.today().weekday() # Monday - 0, Sunday - 6
message = []

if today == 0 or today == 3:
    message.append(laundry_day(data))

if today < 5:  #Getting outfit help on weekdays.
    message.append(dress_today(data))

    final_message = "\n".join(str(item) for item in message if item is not None)
    client = Client(account_sid, auth_token)

    ### Change the from_ (your generated number) and to (your actual number) here
    message = client.messages.create(
        body=final_message,
        from_="+19413940346",
        to=os.environ.get("MY_NUM")
    )

    print("Message sent:", message.status)








