import sys
import os
import unittest
from unittest.mock import patch, MagicMock

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from app.app import app, get_db_connection, get_cache_connection


class TestApp(unittest.TestCase):

    # Test para el endpoint /health
    def test_health_check(self):
        with app.test_client() as client:
            response = client.get('/health')
            json_data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['status'], 'healthy')

    # Test para el endpoint / con conexión a base de datos y caché exitosa
    @patch('app.get_db_connection')
    @patch('app.get_cache_connection')
    def test_index_success(self, mock_get_cache, mock_get_db):
        # Simular una conexión exitosa a la base de datos y caché
        mock_get_db.return_value = MagicMock()
        mock_get_cache.return_value = MagicMock()

        with app.test_client() as client:
            response = client.get('/')
            json_data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['DB'], 'Conectado')
            self.assertEqual(json_data['Cache'], 'Conectado')

    # Test para el endpoint / con fallo en la conexión a la base de datos
    @patch('app.get_db_connection')
    @patch('app.get_cache_connection')
    def test_index_db_failure(self, mock_get_cache, mock_get_db):
        # Simular fallo en la conexión a la base de datos
        mock_get_db.return_value = None
        mock_get_cache.return_value = MagicMock()

        with app.test_client() as client:
            response = client.get('/')
            json_data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['DB'], 'No conectado')
            self.assertEqual(json_data['Cache'], 'Conectado')

    # Test para el endpoint / con fallo en la conexión al caché
    @patch('app.get_db_connection')
    @patch('app.get_cache_connection')
    def test_index_cache_failure(self, mock_get_cache, mock_get_db):
        # Simular fallo en la conexión al caché
        mock_get_db.return_value = MagicMock()
        mock_get_cache.return_value = None

        with app.test_client() as client:
            response = client.get('/')
            json_data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json_data['DB'], 'Conectado')
            self.assertEqual(json_data['Cache'], 'No conectado')

    # Test para verificar la conexión a la base de datos
    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        mock_connect.return_value = MagicMock()
        conn = get_db_connection()
        self.assertIsNotNone(conn)

    # Test para verificar fallo en la conexión a la base de datos
    @patch('psycopg2.connect')
    def test_get_db_connection_failure(self, mock_connect):
        mock_connect.side_effect = Exception("Error conexion BD")
        conn = get_db_connection()
        self.assertIsNone(conn)

    # Test para verificar la conexión al caché
    @patch('redis.StrictRedis.from_url')
    def test_get_cache_connection_success(self, mock_redis):
        mock_redis.return_value = MagicMock()
        cache = get_cache_connection()
        self.assertIsNotNone(cache)

    # Test para verificar fallo en la conexión al caché
    @patch('redis.StrictRedis.from_url')
    def test_get_cache_connection_failure(self, mock_redis):
        mock_redis.side_effect = Exception("Error conectando a la caché")
        cache = get_cache_connection()
        self.assertIsNone(cache)


if __name__ == '__main__':
    unittest.main()
