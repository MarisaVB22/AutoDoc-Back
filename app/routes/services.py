from flask import jsonify
from app import app
from app.utils.funciones import saludo, crear_tabla

# Ruta principal
@app.route("/", methods=["GET"])
def index():
    return jsonify({"saludo": "Hola desde la aplicación Flask de AutoDoc"})

# Llamada a la función saludo desde funciones.py
@app.route("/saludo", methods=["GET"])
def saludo_route():
    data = saludo()
    return jsonify({"saludo": data})

# Ruta para crear la tabla clientes en la base de datos
@app.route("/crear_tabla", methods=["GET"])
def ruta_crear_tabla():
    try:
        crear_tabla()
        return "Tabla creada correctamente", 200
    except Exception as e:
        return str(e), 500