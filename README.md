# AutoDoc

Este repositorio ahora contiene una aplicación Flask mínima.

Estructura:

```bash
app/
├── __init__.py           # Inicialización de la app y configuración de CORS
├── routes/               # Rutas de la API
│   └── services.py       # Lógica de los endpoints
└── utils/
    └── funciones.py      # Funciones auxiliares
main.py                   # Punto de entrada de la aplicación
requirements.txt          # Dependencias de Python
```

Instrucciones rápidas (Windows PowerShell):

1. Crear un entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ejecutar la aplicación localmente:

```powershell
python main.py
```

La aplicación escuchará por defecto en http://127.0.0.1:5000/ y expondrá una ruta `/` que devuelve un JSON simple.

Notas adicionales:

- CORS ya está configurado para permitir la conexión desde un frontend en http://localhost:5173 (Vite/React).
- La aplicación está preparada para extender rutas y servicios según las necesidades del proyecto.
