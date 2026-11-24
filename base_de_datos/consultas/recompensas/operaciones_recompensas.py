"""Acceso persistente de recompensas."""

from base_de_datos.ejecutor import usar_conexion

# Guarda una recompensa nueva o actualizada.
def guardar_recompensa(recompensa):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO recompensa
                    (
                        codigo,
                        nombre,
                        descripcion
                    )
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = %s,
                    descripcion = %s
                """,
                (recompensa.codigo, recompensa.nombre, recompensa.descripcion,
                 recompensa.nombre, recompensa.descripcion),
            )

# Elimina una recompensa por su código.
def eliminar_recompensa(codigo):
    consulta = """
        DELETE FROM recompensa
        WHERE codigo = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo,))

# Guarda una versión de recompensa.
def guardar_version_recompensa(version_recompensa):
    with usar_conexion() as conexion:
        valores = (
            version_recompensa.fecha_inicio, version_recompensa.fecha_final,
            version_recompensa.costo_puntos, version_recompensa.limite_canjes,
            version_recompensa.recompensa.codigo,
        )
        with conexion.cursor() as cursor:
            if version_recompensa.num is None:
                cursor.execute(
                    """
                    INSERT INTO version_recompensa
                        (
                            fecha_inicio,
                            fecha_final,
                            costo_puntos,
                            limite_canjes,
                            recompensa
                        )
                    VALUES
                        (%s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                object.__setattr__(version_recompensa, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    """
                    UPDATE version_recompensa
                    SET
                        fecha_inicio = %s,
                        fecha_final = %s,
                        costo_puntos = %s,
                        limite_canjes = %s,
                        recompensa = %s
                    WHERE
                        num = %s
                    """,
                    valores + (version_recompensa.num,),
                )

# Elimina una versión de recompensa por su número.
def eliminar_version_recompensa(num):
    consulta = """
        DELETE FROM version_recompensa
        WHERE num = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num,))
