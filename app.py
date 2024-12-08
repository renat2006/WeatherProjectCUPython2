from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, current_app
import os
import logging
import requests
from api.weather_api import WeatherAPI
from models.weather_model import check_bad_weather

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("ACCUWEATHER_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
if not API_KEY:
    logger.error("Не удалось загрузить API-ключ AccuWeather из .env.")
    raise EnvironmentError("AccuWeather API-ключ не найден в .env")
if not UNSPLASH_API_KEY:
    logger.error("Не удалось загрузить API-ключ Unsplash из .env.")
    raise EnvironmentError("Unsplash API-ключ не найден в .env")

app = Flask(__name__)
app.config["API_KEY"] = API_KEY
app.config["UNSPLASH_API_KEY"] = UNSPLASH_API_KEY


def get_city_image(city_name):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": city_name,
        "client_id": current_app.config["UNSPLASH_API_KEY"],
        "per_page": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
    except Exception as e:
        logger.error(f"Не удалось получить изображение для {city_name}: {e}")
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    city = data.get("city")

    if not city:
        return jsonify({"error": "Не указан город"}), 400

    weather_client = WeatherAPI(api_key=current_app.config["API_KEY"], language="ru-ru")

    try:
        autocomplete_results = weather_client.get_cities_autocomplete(city)
        if not autocomplete_results:
            return jsonify({"error": "Город не найден"}), 404

        location_key = autocomplete_results[0]["Key"]
        forecast = weather_client.get_forecast_daily(days=5, location_key=location_key, details=True)
        image_url = get_city_image(city)

        return jsonify({"forecast": forecast, "image_url": image_url})
    except Exception as e:
        return jsonify({"error": "Не удалось получить данные", "details": str(e)}), 500


@app.route('/api/weather/multiple', methods=['POST'])
def get_multiple_weather():
    data = request.json
    start_city = data.get("start_city")
    end_city = data.get("end_city")

    if not start_city or not end_city:
        return jsonify({"error": "Не указаны оба города"}), 400

    weather_client = WeatherAPI(api_key=current_app.config["API_KEY"], language="ru-ru")

    def get_city_weather(city_name):
        autocomplete_results = weather_client.get_cities_autocomplete(city_name)
        if not autocomplete_results:
            return None
        location_key = autocomplete_results[0]["Key"]
        forecast = weather_client.get_forecast_daily(days=1, location_key=location_key)[0]
        image_url = get_city_image(city_name)
        return {
            "name": city_name,
            "temperature_max": forecast["temperature_max"],
            "temperature_min": forecast["temperature_min"],
            "humidity": forecast["humidity"],
            "wind_speed": forecast["wind_speed"],
            "rain_probability": forecast["rain_probability"],
            "condition": check_bad_weather(
                temperature_max=forecast["temperature_max"],
                temperature_min=forecast["temperature_min"],
                humidity=forecast["humidity"],
                wind_speed=forecast["wind_speed"],
                rain_probability=forecast["rain_probability"],
            ),
            "image_url": image_url
        }

    start_city_data = get_city_weather(start_city)
    end_city_data = get_city_weather(end_city)

    if not start_city_data or not end_city_data:
        return jsonify({"error": "Не удалось получить данные для одного из городов"}), 500

    return jsonify({"start_city": start_city_data, "end_city": end_city_data})


if __name__ == '__main__':
    logger.info("Запуск приложения...")
    app.run(debug=True)
