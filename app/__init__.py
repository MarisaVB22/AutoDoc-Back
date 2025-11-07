from flask import Flask

app = Flask(__name__)

# Registrar rutas - TODO: Ver si se puede automatizar
from .routes import services