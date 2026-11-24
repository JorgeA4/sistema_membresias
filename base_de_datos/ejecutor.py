from contextlib import contextmanager
from contextvars import ContextVar

import pymysql

from base_de_datos.conexion import obtener_conexion
from utilidades.excepciones import ErrorPersistencia

_conexion_actual = ContextVar("conexion_nexum", default=None)


# convierte cualquier error de mariadb en un error generico de persistencia
def traducir_error_sql(error):
    if isinstance(error, pymysql.MySQLError):
        return ErrorPersistencia(
            "No fue posible completar la operación en la base de datos."
        )
    return error


# proporciona una conexion y confirma o revierte la operacion
@contextmanager
def usar_conexion():
    conexion = _conexion_actual.get()
    propia = conexion is None
    if propia:
        conexion = obtener_conexion()
    try:
        yield conexion
        if propia:
            conexion.commit()
    except Exception as error:
        if propia:
            conexion.rollback()
        error_dominio = traducir_error_sql(error)
        if error_dominio is not error:
            raise error_dominio from error
        raise
    finally:
        if propia:
            conexion.close()


# agrupa varias operaciones en una unica transaccion mariadb
@contextmanager
def transaccion():
    conexion_existente = _conexion_actual.get()
    if conexion_existente is not None:
        yield
        return

    conexion = obtener_conexion()
    token = _conexion_actual.set(conexion)
    try:
        yield
        conexion.commit()
    except Exception as error:
        conexion.rollback()
        error_dominio = traducir_error_sql(error)
        if error_dominio is not error:
            raise error_dominio from error
        raise
    finally:
        _conexion_actual.reset(token)
        conexion.close()


# obtiene una sola fila del cursor
def obtener_fila(cursor):
    return cursor.fetchone()


# obtiene todas las filas del cursor
def obtener_filas(cursor):
    return cursor.fetchall()


# ejecuta una consulta y devuelve una sola fila
def ejecutar_una(consulta, parametros=()):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, parametros)
            fila = obtener_fila(cursor)
            return fila


# ejecuta una consulta y devuelve todas sus filas
def ejecutar_varias(consulta, parametros=()):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, parametros)
            filas = obtener_filas(cursor)
            return filas


# ejecuta una operacion de escritura contra la base de datos
def ejecutar(consulta, parametros=()):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, parametros)
