from flask import jsonify
from app import app
from app.utils.funciones import saludo

# Ruta principal
@app.route("/", methods=["GET"])
def index():
    return jsonify({"saludo": "Hola desde la aplicación Flask de AutoDoc"})

# Llamada a la función saludo desde funciones.py
@app.route("/saludo", methods=["GET"])
def saludo_route():
    data = saludo()
    return jsonify({"saludo": data})