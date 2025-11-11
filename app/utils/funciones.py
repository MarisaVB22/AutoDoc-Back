import psycopg2
from app.config.config import DB_HOST, DB_NAME, DB_USER, DB_PASS

def saludo():
    return "¡Hola desde funciones.py!"

# Probar postgreSQL creando una tabla llamada clientes
def crear_tabla():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50),
            email VARCHAR(50)
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()