import os
from flask import Flask, jsonify
import psycopg2
import redis
from prometheus_flask_exporter import PrometheusMetrics
import socket

app = Flask(__name__, static_folder="/app/static")

# Configurar Prometheus
metrics = PrometheusMetrics(app)

# Agregar información sobre la aplicación como un ejemplo
metrics.info('app_info', 'Application Information', version='1.0')

# Métricas personalizadas
db_up = metrics.gauge('database_up', 'Status of the database connection')
cache_up = metrics.gauge('cache_up', 'Status of the cache connection')

def get_db_connection():
    db_url = os.getenv('DATABASE_URL')
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def get_cache_connection():
    cache_url = os.getenv('CACHE_URL')
    if cache_url and cache_url != 'none':
        try:
            cache = redis.StrictRedis.from_url(cache_url)
            # Probar conexión
            cache.ping()
            return cache
        except Exception as e:
            print(f"Error conectando a la caché: {e}")
            return None
    return None

@app.route('/')
def index():
    # Estado de la base de datos
    conn = get_db_connection()
    db_status = "Conectado" if conn else "No conectado"
    if conn:
        conn.close()
    
    # Estado de la caché
    cache = get_cache_connection()
    cache_status = "Conectado" if cache else "No conectado"
    
    # Obtener el nombre del host de la instancia
    instance_name = socket.gethostname()

    return jsonify({
        "Database": db_status,
        "Cache": cache_status,
        "Instance": instance_name  # Añadir el nombre de la instancia
    })

# Nuevo endpoint de health-check
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)