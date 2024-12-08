from api.base_client import BaseClient
from typing import List, Dict, Union


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
                "humidity": day_forecast["Day"]["RelativeHumidity"]["Average"],
                "wind_speed": day_forecast["Day"]["Wind"]["Speed"]["Value"],
                "rain_probability": day_forecast["Day"]["PrecipitationProbability"],
            }
            forecast_data.append(day_data)

        return forecast_data
