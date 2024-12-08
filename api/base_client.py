import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = timeout

    def _build_url(self, endpoint):
        return f"{self.base_url}/{endpoint}"

    def get(self, endpoint, params=None, headers=None):
        url = self._build_url(endpoint)
        logger.info(f"Отправка GET-запроса на {url} с параметрами: {params} и заголовками: {headers}")
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            self._handle_response(response)
            logger.info(f"GET-запрос на {url} выполнен успешно. Статус: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при выполнении GET-запроса на {url}: {e}")
            raise

    def post(self, endpoint, data=None, headers=None):
        url = self._build_url(endpoint)
        logger.info(f"Отправка POST-запроса на {url} с данными: {data} и заголовками: {headers}")
        try:
            response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            self._handle_response(response)
            logger.info(f"POST-запрос на {url} выполнен успешно. Статус: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при выполнении POST-запроса на {url}: {e}")
            raise

    def _handle_response(self, response):
        if response.ok:
            logger.debug(f"Успешный ответ: {response.status_code} - {response.text}")
        else:
            logger.error(f"Ошибка API: {response.status_code} - {response.text}")
            raise Exception(f"Ошибка API: {response.status_code} - {response.text}")
