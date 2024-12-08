def check_bad_weather(
    temperature_max: float,
    temperature_min: float,
    humidity: float,
    wind_speed: float,
    rain_probability: float
) -> str:
    """
    Оценивает погодные условия на основе доступных параметров.

    :param temperature_max: Максимальная температура в градусах Цельсия.
    :param temperature_min: Минимальная температура в градусах Цельсия.
    :param humidity: Влажность в процентах.
    :param wind_speed: Скорость ветра в км/ч.
    :param rain_probability: Вероятность дождя в процентах.
    :return: "bad" (плохая погода) или "good" (хорошая погода).
    """
    if temperature_max > 35 or temperature_min < -10:
        return "bad"
    if wind_speed > 50:
        return "bad"
    if rain_probability > 80:
        return "bad"
    if humidity > 90:
        return "bad"

    moderate_conditions = 0
    if temperature_max > 30 or temperature_min < 0:
        moderate_conditions += 1
    if wind_speed > 30:
        moderate_conditions += 1
    if rain_probability > 60:
        moderate_conditions += 1
    if humidity > 70:
        moderate_conditions += 1


    if moderate_conditions >= 2:
        return "bad"


    return "good"
