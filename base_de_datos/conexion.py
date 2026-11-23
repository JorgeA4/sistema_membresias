"""Configuración y apertura de conexiones con MariaDB de Nexum."""

import os
import sys

import pymysql
from dotenv import load_dotenv
from pymysql.connections import Connection


load_dotenv()


def obtener_conexion() -> Connection:
    """Abre una conexión a Nexum usando la configuración del entorno."""
    usuario = os.getenv("NEXUM_DB_USUARIO", "root")
    contraseña = os.getenv("NEXUM_DB_CONTRASENA", "")

    if not usuario:
        raise RuntimeError("Falta la variable de entorno NEXUM_DB_USUARIO")

    nombre_base = os.getenv("NEXUM_DB_NOMBRE", "Nexum")
    socket = os.getenv("NEXUM_DB_SOCKET")
    if socket is None and sys.platform.startswith("linux"):
        socket_lampp = "/opt/lampp/var/mysql/mysql.sock"
        if os.path.exists(socket_lampp):
            socket = socket_lampp

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
