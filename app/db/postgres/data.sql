-- 1. CREATE USER (run as postgres superuser)
CREATE USER user WITH PASSWORD 'autodoc';

-- 2. CREATE DATABASE
CREATE DATABASE autodoc_db OWNER user ENCODING 'UTF8';

-- 3. CREATE SCHEMA
CREATE SCHEMA IF NOT EXISTS documentos AUTHORIZATION user;
GRANT ALL PRIVILEGES ON SCHEMA documentos TO user;

-- 4. CREATE TABLES

-- Tabla de ejemplo: documentos
CREATE TABLE documentos.documentos (
    documento_id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. INSERTAR REGISTROS DE EJEMPLO

INSERT INTO documentos.documentos (titulo, contenido)
VALUES 
('Manual de usuario', 'Este es el manual de usuario para la aplicación AutoDoc.'),
('Guía de instalación', 'Instrucciones paso a paso para instalar y configurar AutoDoc.');