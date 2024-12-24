from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import os
import logging
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from api.weather_api import WeatherAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("ACCUWEATHER_API_KEY")
if not API_KEY:
    logger.error("Не удалось загрузить API-ключ AccuWeather из .env.")
    raise EnvironmentError("AccuWeather API-ключ не найден в .env")

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])

loaded_weather_data = {}
city_array = []

def create_plots(data):
    if data:
        temp_max_hist = make_subplots()
        temp_min_hist = make_subplots()
        rain_prob_hist = make_subplots()
        wind_speed_hist = make_subplots()

        for city, df in data.items():
            temp_max_hist.add_trace(
                go.Scatter(x=df['day'], y=df['temp_max'], name=f'{city} Макс. Темп.', mode='lines+markers')
            )
            temp_min_hist.add_trace(
                go.Scatter(x=df['day'], y=df['temp_min'], name=f'{city} Мин. Темп.', mode='lines+markers')
            )
            rain_prob_hist.add_trace(
                go.Scatter(x=df['day'], y=df['rain_prob'], name=f'{city} Вероятность дождя', mode='lines+markers')
            )
            wind_speed_hist.add_trace(
                go.Scatter(x=df['day'], y=df['wind_speed'], name=f'{city} Скорость ветра', mode='lines+markers')
            )

        temp_max_hist.update_layout(title_text='Максимальная температура', xaxis_title='День', yaxis_title='Температура (°C)')
        temp_min_hist.update_layout(title_text='Минимальная температура', xaxis_title='День', yaxis_title='Температура (°C)')
        rain_prob_hist.update_layout(title_text='Вероятность дождя', xaxis_title='День', yaxis_title='Процент')
        wind_speed_hist.update_layout(title_text='Скорость ветра', xaxis_title='День', yaxis_title='м/с')

        return temp_max_hist, temp_min_hist, rain_prob_hist, wind_speed_hist
    else:
        return {}, {}, {}, {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather/multiple', methods=['POST'])
def get_multiple_weather():
    global loaded_weather_data
    data = request.json
    cities = data.get("cities", [])
    days = data.get("days", 5)

    if not cities:
        return jsonify({"error": "Не указаны города"}), 400

    weather_client = WeatherAPI(api_key=API_KEY, language="ru-ru")

    def get_city_weather(city_name):
        autocomplete_results = weather_client.get_cities_autocomplete(city_name)
        if not autocomplete_results:
            return None
        location_key = autocomplete_results[0]["Key"]
        forecast = weather_client.get_forecast_daily(days=days, location_key=location_key)
        return {
            "day": list(range(1, len(forecast) + 1)),
            "temp_max": [day["temperature_max"] for day in forecast],
            "temp_min": [day["temperature_min"] for day in forecast],
            "rain_prob": [day["rain_probability"] for day in forecast],
            "wind_speed": [day["wind_speed"] for day in forecast]
        }

    loaded_weather_data = {}
    for city in cities:
        weather_data = get_city_weather(city)
        if weather_data:
            loaded_weather_data[city] = weather_data

    return jsonify(loaded_weather_data)

dash_app.layout = dbc.Container([
    html.H1('Прогноз погоды для городов', className='my-3 text-center'),
    dbc.Row([
        dbc.Col([
            dcc.Input(id='add-city', type='text', placeholder='Введите город', className='form-control'),
        ], md=4),
        dbc.Col([
            html.Button('Добавить город', id='add-button', className='btn btn-dark w-100'),
        ], md=2),
        dbc.Col([
            dcc.Dropdown(
                id='days-dropdown',
                options=[
                    {'label': '1 день', 'value': 1},
                    {'label': '5 дней', 'value': 5},
                    {'label': '10 дней', 'value': 10},
                    {'label': '15 дней', 'value': 15}
                ],
                value=5,
                placeholder='Выберите количество дней',
                className='form-control'
            ),
        ], md=3),
        dbc.Col([
            html.Button('Получить прогноз', id='submit-button', className='btn btn-primary w-100'),
        ], md=3),
    ], className='my-3'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='temp-max-graph'), md=6),
        dbc.Col(dcc.Graph(id='temp-min-graph'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='rain-prob-graph'), md=6),
        dbc.Col(dcc.Graph(id='wind-speed-graph'), md=6),
    ])
])

@dash_app.callback(
    [Output('temp-max-graph', 'figure'),
     Output('temp-min-graph', 'figure'),
     Output('rain-prob-graph', 'figure'),
     Output('wind-speed-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('days-dropdown', 'value')]
)
def update_graphs(n_clicks, days):
    global loaded_weather_data
    if not loaded_weather_data:
        return create_plots({})

    return create_plots(loaded_weather_data)

@dash_app.callback(
    [Output('add-city', 'value'),
     Output('cards-container', 'children')],
    [Input('add-button', 'n_clicks')],
    [State('add-city', 'value')]
)
def add_city(n_clicks, city):
    global city_array
    if city:
        city_array.append(city)
    return '', [html.P(city, className='card') for city in city_array]

if __name__ == '__main__':
    app.run(debug=True)
