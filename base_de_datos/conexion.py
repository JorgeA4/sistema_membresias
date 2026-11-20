"""Configuración y apertura de conexiones con MariaDB de Nexum."""

import os

import pymysql
from pymysql.connections import Connection


def obtener_conexion() -> Connection:
    """Abre una conexión a Nexum usando la configuración del entorno."""
    usuario = os.getenv("NEXUM_DB_USUARIO")
    contraseña = os.getenv("NEXUM_DB_CONTRASENA")

    if not usuario:
        raise RuntimeError("Falta la variable de entorno NEXUM_DB_USUARIO")
    if not contraseña:
        raise RuntimeError("Falta la variable de entorno NEXUM_DB_CONTRASENA")

    nombre_base = os.getenv("NEXUM_DB_NOMBRE", "Nexum")
    socket = os.getenv(
        "NEXUM_DB_SOCKET",
        "/opt/lampp/var/mysql/mysql.sock",
    )

    parametros = {
        "user": usuario,
        "password": contraseña,
        "database": nombre_base,
        "charset": "utf8mb4",
        "autocommit": False,
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5,
    }

    if socket:
        parametros["unix_socket"] = socket
    else:
        parametros["host"] = os.getenv("NEXUM_DB_HOST", "127.0.0.1")
        parametros["port"] = int(os.getenv("NEXUM_DB_PUERTO", "3306"))

    return pymysql.connect(**parametros)
