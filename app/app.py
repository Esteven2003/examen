import os
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

# Configuración mediante variables de entorno
APP_NAME = os.getenv("APP_NAME", "Flask Devops")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    """Inicializa la base de datos creando la tabla e insertando datos de prueba."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Crear tabla productos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL
            );
        ''')
        
        # Verificar si ya existen registros
        cur.execute("SELECT COUNT(*) FROM productos;")
        if cur.fetchone()[0] == 0:
            productos_iniciales = [
                ('Laptop Dell', 899.99, 15),
                ('Mouse Logi', 25.50, 50),
                ('Teclado Mecánico', 75.00, 30),
                ('Monitor 24"', 150.00, 20),
                ('Audífonos Gamer', 45.99, 40)
            ]
            cur.executemany(
                "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s);",
                productos_iniciales
            )
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")

# Inicializar DB al arrancar
init_db()

@app.route('/')
def index():
    db_status = "Conectado exitosamente"
    try:
        conn = get_db_connection()
        conn.close()
    except OperationalError:
        db_status = "Error de conexión"

    return render_template('index.html', app_name=APP_NAME, version=APP_VERSION, db_status=db_status)

@app.route('/productos')
def productos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Formatear datos para la plantilla
        lista_productos = []
        for row in rows:
            lista_productos.append({
                "id": row[0],
                "nombre": row[1],
                "precio": row[2],
                "stock": row[3]
            })
        return render_template('productos.html', productos=lista_productos)
    except Exception as e:
        return f"Error al obtener productos: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)