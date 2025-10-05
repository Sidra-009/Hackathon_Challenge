import requests
from config import GOOGLE_API_KEY

# ---------------- NASA POWER API ----------------
def fetch_nasa_power(lat, lon, selected_date):
    """
    Fetch weather data from NASA POWER API for a given latitude, longitude, and date.
    Returns a dictionary with temperature, precipitation, wind speed, and humidity.
    """
    api_url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M,PRECTOTCORR,WS10M,RH2M"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={selected_date.strftime('%Y%m%d')}"
        f"&end={selected_date.strftime('%Y%m%d')}"
        f"&format=JSON"
    )
    
    response = requests.get(api_url)
    if response.status_code != 200:
        return None
    
    try:
        data = response.json()["properties"]["parameter"]
        temp = data["T2M"][list(data["T2M"].keys())[0]]
        rain = data["PRECTOTCORR"][list(data["PRECTOTCORR"].keys())[0]]
        wind = round(data["WS10M"][list(data["WS10M"].keys())[0]] * 3.6, 1)
        humidity = data["RH2M"][list(data["RH2M"].keys())[0]]
        return {"temp": temp, "rain": rain, "wind": wind, "humidity": humidity}
    except Exception:
        return None

# ---------------- Google Geocoding API ----------------
def get_coordinates(city_name):
    """
    Convert a city name into latitude and longitude using Google Geocoding API.
    Returns (lat, lon) tuple.
    """
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()
    
    if response["status"] == "OK":
        lat = response["results"][0]["geometry"]["location"]["lat"]
        lon = response["results"][0]["geometry"]["location"]["lng"]
        return lat, lon
    else:
        return None, None
