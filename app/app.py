import os
import socket
from flask import Flask, jsonify, render_template, request
import psycopg2
import redis
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__, static_folder="/app/static",template_folder="templates")


# Configurar Prometheus
metrics = PrometheusMetrics(app)

# Agregar información sobre la aplicación como un ejemplo
metrics.info('app_info', 'Application Information', version='1.0')


# Métricas personalizadas
db_up = metrics.gauge('database_up', 'Status database connection')
cache_up = metrics.gauge('cache_up', 'Status cache connection')


def get_db_connection():
    db_url = os.getenv('DATABASE_URL')
    print("DATABASE_URL:", db_url)
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None


def get_cache_connection():
    cache_url = os.getenv('CACHE_URL')
    print("CACHE_URL:", cache_url)
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

def create_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()

@app.route('/db/create', methods=['POST'])
def create_item():
    data = request.json
    name = data.get('name')
    description = data.get('description')

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO items (name, description)
        VALUES (%s, %s) RETURNING id
        """, (name, description))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"id": new_id, "name": name, "description": description}), 201
    return jsonify({"error": "Unable to connect to the database"}), 500

@app.route('/db/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Elimina un elemento de la base de datos basado en su ID.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
        deleted_id = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if deleted_id:
            return jsonify({"message": f"Item with ID {item_id} deleted successfully"}), 200
        else:
            return jsonify({"error": f"Item with ID {item_id} not found"}), 404
    return jsonify({"error": "Unable to connect to the database"}), 500

@app.route('/db/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM items")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        items = [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]
        return jsonify(items), 200
    return jsonify({"error": "Unable to connect to the database"}), 500

@app.route('/cache/set', methods=['POST'])
def set_cache():
    data = request.json
    key = data.get('key')
    value = data.get('value')

    cache = get_cache_connection()
    if cache:
        cache.set(key, value)
        return jsonify({"key": key, "value": value}), 200
    return jsonify({"error": "Unable to connect to the cache"}), 500

@app.route('/cache/get/<key>', methods=['GET'])
def get_cache(key):
    cache = get_cache_connection()
    if cache:
        value = cache.get(key)
        if value:
            return jsonify({"key": key, "value": value.decode('utf-8')}), 200
        return jsonify({"error": f"No value found for key {key}"}), 404
    return jsonify({"error": "Unable to connect to the cache"}), 500

@app.route('/cache/delete/<key>', methods=['DELETE'])
def delete_cache(key):
    cache = get_cache_connection()
    if cache:
        result = cache.delete(key)
        if result == 1:
            return jsonify({"message": f"Key {key} deleted"}), 200
        return jsonify({"error": f"Key {key} not found"}), 404
    return jsonify({"error": "Unable to connect to the cache"}), 500



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

    # Si la petición proviene de los tests, devolver JSON
    if request.headers.get("Accept") == "application/json":
        return jsonify({"DB": db_status, "Cache": cache_status})

    return render_template("index.html", db_status=db_status, cache_status=cache_status, instance_name=instance_name)


# Nuevo endpoint de health-check
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy"
    })


if __name__ == '__main__':
    create_table()
    app.run(
        host='0.0.0.0',
        port=5000
    )
