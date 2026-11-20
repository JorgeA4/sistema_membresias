-- REINICIO COMPLETO DE LA BASE DE DATOS NEXUM
-- ADVERTENCIA: elimina todos los datos existentes de Nexum.
-- Ejecutar desde la carpeta base_de_datos con el cliente de MariaDB.

DROP DATABASE IF EXISTS Nexum;

SOURCE ./CREACIÓN_BD_NEXUM.sql;
SOURCE ./INSERTS_BD_NEXUM.sql;
