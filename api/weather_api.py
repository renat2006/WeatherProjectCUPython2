from api.base_client import BaseClient
from typing import List, Dict, Union
import plotly.graph_objs as go
from io import BytesIO

class WeatherAPI(BaseClient):
    ALLOWED_FORECAST_DAYS = {1, 5, 10, 15}

    def __init__(self, api_key: str, language: str):
        """
        Инициализация клиента для работы с API погоды.

        :param api_key: Ключ API для аутентификации.
        :param language: Язык данных, например "ru-ru".
        """
        super().__init__(base_url="http://dataservice.accuweather.com")
        self.api_key = api_key
        self.language = language

    def get_cities_autocomplete(self, city: str) -> List[Dict]:
        """
        Метод для получения списка городов с автодополнением.

        :param city: Название города (или его часть) для поиска.
        :return: Список словарей с данными о городах, которые совпадают с запросом.
        """
        params = {
            "q": city,
            "language": self.language,
            "apikey": self.api_key
        }
        response = self.get(endpoint="locations/v1/cities/autocomplete", params=params)
        return response

    def get_forecast_daily(
        self, days: int, location_key: str, details: bool = True, metric: bool = True
    ) -> Union[Dict, None]:
        """
        Получение прогноза погоды на заданное количество дней и выделение нужных данных.

        :param days: Количество дней прогноза (1, 5, 10, 15).
        :param location_key: Уникальный ключ местоположения (LocationKey).
        :param details: Флаг для получения более детализированного прогноза.
        :param metric: Флаг для получения данных в метрической системе (True — Цельсий, False — Фаренгейт).
        :return: Словарь с необходимыми данными прогноза (температура, влажность, ветер, дождь).
        :raises ValueError: Если значение days не является допустимым.
        """
        if days not in self.ALLOWED_FORECAST_DAYS:
            raise ValueError(
                f"Некорректное значение для параметра 'days': {days}. "
                f"Допустимые значения: {self.ALLOWED_FORECAST_DAYS}."
            )

        params = {
            "language": self.language,
            "details": details,
            "metric": metric,
            "apikey": self.api_key
        }

        endpoint = f"forecasts/v1/daily/{days}day/{location_key}"
        response = self.get(endpoint=endpoint, params=params)

        forecast_data = []
        for day_forecast in response.get("DailyForecasts", []):
            day_data = {
                "date": day_forecast["Date"],
                "temperature_max": day_forecast["Temperature"]["Maximum"]["Value"],
                "temperature_min": day_forecast["Temperature"]["Minimum"]["Value"],
                "humidity": day_forecast["Day"]["RelativeHumidity"],
                "wind_speed": day_forecast["Day"]["Wind"]["Speed"]["Value"],
                "rain_probability": day_forecast["Day"]["PrecipitationProbability"],
            }
            forecast_data.append(day_data)

        return forecast_data

    def generate_combined_graph(self, city1_data, city2_data, city1_name, city2_name):
        """
        Создает комбинированный график для двух городов.

        :param city1_data: Прогноз для первого города.
        :param city2_data: Прогноз для второго города.
        :param city1_name: Название первого города.
        :param city2_name: Название второго города.
        :return: Буфер изображения графика.
        """
        dates = [entry["date"][:10] for entry in city1_data]
        city1_temps = [entry["temperature_max"] for entry in city1_data]
        city2_temps = [entry["temperature_max"] for entry in city2_data]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=city1_temps, mode='lines+markers',
            name=f'{city1_name} Температура', line=dict(color='red')
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=city2_temps, mode='lines+markers',
            name=f'{city2_name} Температура', line=dict(color='blue')
        ))

        fig.update_layout(
            title="Сравнительный график температуры",
            xaxis_title="Дата",
            yaxis_title="Температура (°C)",
            legend_title="Города"
        )

        buffer = BytesIO()
        fig.write_image(buffer, format='png')
        buffer.seek(0)
        return buffer

    def generate_single_graph(self, city_data, city_name):
        """
        Создает график для одного города.

        :param city_data: Прогноз для города.
        :param city_name: Название города.
        :return: Буфер изображения графика.
        """
        dates = [entry["date"][:10] for entry in city_data]
        temps = [entry["temperature_max"] for entry in city_data]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=temps, mode='lines+markers',
            name=f'{city_name} Температура', line=dict(color='green')
        ))

        fig.update_layout(
            title=f"График температуры для {city_name}",
            xaxis_title="Дата",
            yaxis_title="Температура (°C)",
            legend_title="Параметры"
        )

        buffer = BytesIO()
        fig.write_image(buffer, format='png')
        buffer.seek(0)
        return buffer
