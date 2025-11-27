import mimetypes
import os
from flask import g, jsonify
from app.db.psql_connection_pool import PsqlConnectionPool
from app.config.config import DB_CONFIG # Configuración de la BBDD
from app.db import queries as db # Consultas a la BBDD
import requests

# Importar variables de entorno para Sharepoint
SITE_ID = os.getenv("SITE_ID")
DRIVE_ID = os.getenv("DRIVE_ID")


# ------------------ Pool por request ------------------ #
def get_db_pool():
    """
    Devuelve el pool de conexiones de la base de datos.
    Se almacena en g para que sea único por request.
    """
    if "db_pool" not in g:
        g.db_pool = PsqlConnectionPool(DB_CONFIG)
        g.db_pool.connect()  # Inicializa el pool si no está creado
    return g.db_pool

# ----------- MICROSOFT GRAPH ------------ #
# API que permite acceder a datos de Microsoft 365 (OneDrive, SharePoint, etc.)
# Obtiene un access token para Microsoft Graph usando Client Credentials.
def get_access_token():
    # Leer variables de entorno
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # URL del endpoint de token de Azure AD (OAuth2)
    # Hacer la petición para obtener el token
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

# ----------------- PRUEBA ----------------- #
def saludo():
    return "¡Hola desde funciones.py!"

"""-----------------------------------------------------------------------
                       PROYECTOS
-----------------------------------------------------------------------"""

# Devuelve la lista de proyectos. Si se pasa el parámetro "nombre", filtra por coincidencia parcial.
def obtener_proyectos(nombre=None):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        if nombre:
            cursor.execute(db.GET_PROJECT_BY_NAME, (f"%{nombre}%",))
        else:
            cursor.execute(db.GET_ALL_PROJECTS)
        proyectos = cursor.fetchall()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyectos

# Devuelve un proyecto por su ID.
def obtener_proyecto_por_id(proyecto_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.GET_PROJECT_BY_ID, (proyecto_id,))
        proyecto = cursor.fetchone()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyecto

# Inserta un nuevo proyecto en la base de datos y devuelve el ID
def crear_proyecto(nombre, descripcion, proyecto_url, id_sharepoint):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            db.CREATE_PROJECT, 
            (nombre, descripcion, proyecto_url, id_sharepoint)
        )
        proyecto_id = cursor.fetchone()["proyecto_id"]
        conn.commit()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyecto_id

# Crear carpeta en Sharepoint para el proyecto
def crear_carpeta_sharepoint(nombre_carpeta):
    # Token de acceso a la API de Microsoft Graph
    token = get_access_token() 

    # Endpoint para crear carpeta en la raíz del SHAREPOINT
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVE_ID}/root/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "name": nombre_carpeta,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status() # Lanza error si falla
    folder_info = response.json() # JSON de Microsoft Graph

    # Devuelve la URL de la carpeta creada y su ID
    return folder_info.get("webUrl"), folder_info.get("id")


def modificar_proyecto_bbdd(proyecto_id, nombre, descripcion, proyecto_url):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.UPDATE_PROJECT, (nombre, descripcion, proyecto_url, proyecto_id))
        conn.commit()
        # Si ninguna fila fue afectada, el proyecto no existía
        return cursor.rowcount > 0
    finally:
        cursor.close()
        pool.release_connection(conn)

def modificar_proyecto_sharepoint(proyecto_id, nuevo_nombre):
    # Obtener folder_id del proyecto
    folder_id = obtener_info_proyecto(proyecto_id)

    # Token de acceso a la API de Microsoft Graph
    token = get_access_token() 

    # Endpoint para actualizar el nombre de la carpeta
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{folder_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "name": nuevo_nombre
    }

    response = requests.patch(url, headers=headers, json=body)
    response.raise_for_status() # Lanza error si falla

    return response.json().get("webUrl")  # Devuelve la nueva URL pública de la carpeta

# Elimina un proyecto dado su ID. Devuelve True si se eliminó, False si no existía.
def eliminar_proyecto(proyecto_id):
    """
    Elimina un proyecto dado su ID.
     - Verifica si el proyecto existe en la BD y obtiene folder_id de SharePoint.
     - Elimina la carpeta en SharePoint.
     - Elimina el proyecto en la BD.
    Devuelve True si se eliminó, False si no existía.
    """
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # 0. Comprobar si el proyecto existe y obtener folder_id
        folder_id = obtener_info_proyecto(proyecto_id)
    
        # 1. Eliminar carpeta de Sharepoint
        token = get_access_token()
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{folder_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code not in (204, 404):
            # 204 = eliminado correctamente, 404 = ya no existía
            raise Exception(f"No se pudo eliminar la carpeta en SharePoint: {response.text}")

        # 2. Eliminar de la BBDD
        cursor.execute(db.DELETE_PROJECT, (proyecto_id,))
        if cursor.rowcount == 0:
            # No existía el proyecto
            conn.commit()
            return False
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        pool.release_connection(conn)

# Devuelve el ID de la carpeta de Sharepoint asociada a un proyecto
def obtener_info_proyecto(idProyecto):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_PROJECT_URL_BY_ID, (idProyecto,))
        result = cursor.fetchone()
        
        if not result or not result.get("proyecto_url"):
            raise Exception(f"No se encontró URL de SharePoint para el proyecto {idProyecto}")
        
        return result["id_sharepoint"]
    
    finally:
        cursor.close()
        pool.release_connection(conn)

"""-----------------------------------------------------------------------
                       DOCUMENTOS
-----------------------------------------------------------------------"""

# Obtener todos los documentos de un proyecto
def obtener_documentos(proyecto_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_DOCUMENTS_BY_PROJECT, (proyecto_id,))
        documentos = cursor.fetchall()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documentos


# Crear un nuevo documento
def crear_documento(proyecto_id, nombre, descripcion, url, archivo_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            db.CREATE_DOCUMENT,
            (proyecto_id, nombre, descripcion, url, archivo_id)
        )
        documento_id = cursor.fetchone()["documento_id"]
        conn.commit()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documento_id

# Subir archivo a Sharepoint
def subir_archivo_sharepoint(nombre_archivo, contenido_bytes, carpeta_id):
    token = get_access_token() 

    # Endpoint para subir archivo en modo simple (menos de 4MB)
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{carpeta_id}:/{nombre_archivo}:/content"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    response = requests.put(url, headers=headers, data=contenido_bytes)
    response.raise_for_status()

    return response.json().get("webUrl"), response.json().get("id")


# Obtener un documento por su ID
def obtener_documento_por_id(documento_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_DOCUMENT_BY_ID, (documento_id,))
        documento = cursor.fetchone()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documento


# Modificar documento
def modificar_documento_bbdd(documento_id, nombre, descripcion, url=None):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        if url:
            # Actualiza nombre, descripción y url
            cursor.execute(
                db.UPDATE_DOCUMENT_URL,
                (nombre, descripcion, url, documento_id)
            )
        else: 
            # Actualiza solo nombre y descripción
            cursor.execute(
                db.UPDATE_DOCUMENT,
                (nombre, descripcion, documento_id)
            )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        pool.release_connection(conn)


def modificar_documento_sharepoint(sharepoint_id, contenido_bytes):
    token = get_access_token()

    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{sharepoint_id}/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    response = requests.put(url, headers=headers, data=contenido_bytes)
    response.raise_for_status()

    # Devuelve la URL pública del archivo
    return response.json().get("webUrl")


# Eliminar un documento
def eliminar_documento(documento_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Obtener id de SharePoint
        try:
            sharepoint_id = obtener_info_documento(documento_id)
        except Exception:
            sharepoint_id = None  # Si no existe, se continúa con la BBDD

        # Eliminar archivo en SharePoint
        if sharepoint_id:
            token = get_access_token()
            url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{sharepoint_id}"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.delete(url, headers=headers)
            if response.status_code not in (204, 404):
                raise Exception(f"No se pudo eliminar el archivo en SharePoint: {response.text}")

        # Eliminar de la BBDD
        cursor.execute(db.DELETE_DOCUMENT, (documento_id,))
        if cursor.rowcount == 0:
            conn.commit()
            return False

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        pool.release_connection(conn)


# Devuelve el ID del arhivo en Sharepoint
def obtener_info_documento(documento_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_DOCUMENT_BY_ID, (documento_id,))
        result = cursor.fetchone()
        
        if not result or not result.get("id_sharepoint"):
            raise Exception(f"No se encontró el documento con ID {documento_id} o no tiene ID de SharePoint")
        
        return result["id_sharepoint"]
    
    finally:
        cursor.close()
        pool.release_connection(conn)