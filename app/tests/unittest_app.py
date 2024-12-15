import unittest
from unittest.mock import patch
from app import app, get_db_connection, get_cache_connection


class TestApp(unittest.TestCase):

    @patch("psycopg2.connect")
    def test_db_connection_success(self, mock_connect):
        # Simular que la conexión a la base de datos es exitosa
        mock_connect.return_value = True
        conn = get_db_connection()
        self.assertIsNotNone(conn)

    @patch("psycopg2.connect")
    def test_db_connection_failure(self, mock_connect):
        # Simular que la conexión a la base de datos falla
        mock_connect.side_effect = Exception("Error de conexión")
        conn = get_db_connection()
        self.assertIsNone(conn)

    @patch("redis.StrictRedis.from_url")
    def test_cache_connection_success(self, mock_redis):
        # Simular que la conexión al caché es exitosa
        mock_redis.return_value.ping.return_value = True
        cache = get_cache_connection()
        self.assertIsNotNone(cache)

    @patch("redis.StrictRedis.from_url")
    def test_cache_connection_failure(self, mock_redis):
        # Simular que la conexión al caché falla
        mock_redis.return_value.ping.side_effect = Exception("Error conexión")
        cache = get_cache_connection()
        self.assertIsNone(cache)


@patch("app.get_db_connection")
@patch("app.get_cache_connection")
def test_index(self, mock_get_cache, mock_get_db):
    # Simular respuestas para el endpoint '/'
    mock_get_db.return_value = True
    mock_get_cache.return_value = True  # Simula que el caché está conectado

    # Realizar una petición GET al endpoint
    with app.test_client() as client:
        response = client.get('/')
        json_data = response.get_json()

        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            json_data["Database"],
            "Conectado"
        )
        self.assertEqual(
            json_data["Cache"],
            "Conectado"
        )


if __name__ == '__main__':
    unittest.main()
