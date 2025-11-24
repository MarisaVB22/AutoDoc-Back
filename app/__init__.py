from flask import Flask

# Para poder conectar front y backend
from flask_cors import CORS
from .config.config import CORS_ORIGINS

# Para variables de entorno
from dotenv import load_dotenv  

# Cargar variables de entorno del .env al iniciar la app
load_dotenv()

app = Flask(__name__)
CORS(app, resources={"/*": {"origins": CORS_ORIGINS}})  # habilita CORS

# Registrar rutas
from .routes import services