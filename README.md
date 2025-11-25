# AutoDoc

Este repositorio contiene una aplicación Flask mínima conectada a PostgreSQL usando Docker, con inicialización automática de la base de datos y pgAdmin para gestión visual.

---

## Stack del proyecto

### Frontend
- **React** → Interfaz de usuario.

### Backend
- **Flask** → API y endpoints.
- **Docker + PostgreSQL** → Desarrollo local.
  - La base de datos local se ejecuta en contenedores Docker y se inicializa automáticamente desde `data.sql`.
  - En el futuro:
    - La base de datos se migrará a un **servidor de Desarrollo**.
    - Finalmente, se desplegará en **Producción**.

---

## Estructura del proyecto:

```powershell
app/
│
├── __init__.py
├── routes/
│   └── services.py
└── utils/
    └── funciones.py
└── db/
    └── postgres/
        └── data.sql # Script de inicialización de la base de datos      
    └── queries.py
main.py
<<<<<<< HEAD
```
=======
docker-compose.yml
requirements.txt
>>>>>>> andrea

---

## Instrucciones rápidas (Windows PowerShell):

### 1. Crear un entorno virtual e instalar dependencias (opcional si quieres correr Flask localmente):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Levantar la base de datos y pgAdmin con Docker:

```
docker-compose up -d
```

Esto levantará:
- PostgreSQL (postgres_db) en el puerto 5432 y creará automáticamente:
    - Usuario user
    - Base de datos autodoc_db
    - Schema documentos
    - Tabla documentos.documentos con registros de ejemplo
- pgAdmin (pgadmin) en el puerto 8080

### 3. Acceder a pgAmin (opcional)

3.1. Abrir navegador: http://localhost:8080
    Usuario: admin@admin.com
    Contraseña: admin123
3.2. Agregar un servidor:
    Name: PostgresLocal
    Host name/address: postgres
    Port: 5432
    Username: user
    Password: pss
3.3. Guardar y conectar
3.4. Explorar la base de datos autodoc_db → Schemas → documentos → Tables → documentos.

### 4. Ejecutar la aplicación Flask localmente:

```powershell
python main.py
```

<<<<<<< HEAD
La aplicación escuchará por defecto en http://127.0.0.1:5000/ y expondrá una ruta `/` que devuelve un JSON simple.
=======
- La aplicación escuchará por defecto en http://127.0.0.1:5000/
- Puedes probar la ruta /crear_tabla en Postman:

```powershell
GET http://127.0.0.1:5000/crear_tabla
```

Respuesta esperada: "Tabla creada correctamente"

#### 5. Detener los contenedores

```powershell
docker-compose down
```

- Esto detiene y elimina los contenedores pero mantiene los volúmenes de datos.
- Para eliminar también los volúmenes:


```powershell
docker-compose down -v
```

### 6. Notas
- Variables de conexión a PostgreSQL (DB_HOST, DB_USER, DB_PASS, DB_NAME) se encuentran en config.py.
- No subas datos sensibles al repositorio.
- Gracias al script data.sql dentro de app/db/postgres, cualquier persona que clone el repositorio y haga docker-compose up -d tendrá la base de datos lista automáticamente, sin necesidad de ejecutar endpoints o scripts adicionales.
>>>>>>> andrea
