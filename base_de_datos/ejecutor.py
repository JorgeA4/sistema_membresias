"""Ejecución centralizada de operaciones contra MariaDB."""

from contextlib import contextmanager
from contextvars import ContextVar

import pymysql

from base_de_datos.conexion import obtener_conexion
from utilidades.excepciones import ErrorPersistencia

_conexion_actual = ContextVar("conexion_nexum", default=None)


def traducir_error_sql(error):
    """Convierte cualquier error de MariaDB en un error genérico de persistencia."""
    if isinstance(error, pymysql.MySQLError):
        return ErrorPersistencia(
            "No fue posible completar la operación en la base de datos."
        )
    return error


@contextmanager
def usar_conexion():
    """Proporciona una conexión y confirma o revierte la operación."""
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


@contextmanager
def transaccion():
    """Agrupa varias operaciones en una única transacción MariaDB."""
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


def obtener_fila(cursor):
    return cursor.fetchone()


def obtener_filas(cursor):
    return cursor.fetchall()
