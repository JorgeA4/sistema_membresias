import os

import pymysql
from dotenv import load_dotenv
from pymysql.connections import Connection

load_dotenv()

# abre una conexion a Nexum usando la configuracion del entorno
def obtener_conexion() -> Connection:
    usuario = os.getenv("NEXUM_DB_USUARIO", "root")
    contraseña = os.getenv("NEXUM_DB_CONTRASENA", "")
    nombre_base = os.getenv("NEXUM_DB_NOMBRE", "Nexum")

    parametros = {
        "user": usuario,
        "password": contraseña,
        "database": nombre_base,
        "charset": "utf8mb4",
        "autocommit": False,
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5,
    }

    parametros["host"] = os.getenv("NEXUM_DB_HOST", "127.0.0.1")
    parametros["port"] = int(os.getenv("NEXUM_DB_PUERTO", "3306"))

    return pymysql.connect(**parametros)
