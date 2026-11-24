"""Acceso persistente de miembros."""

from base_de_datos.ejecutor import usar_conexion


# Guarda un miembro nuevo o actualizado.
def guardar_miembro(miembro):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            valores = (
                miembro.nombre, miembro.primer_apellido,
                miembro.segundo_apellido, miembro.telefono, miembro.correo,
                miembro.contraseña, miembro.fecha_registro,
            )
            if miembro.num is None:
                cursor.execute(
                    """
                    INSERT INTO miembro
                        (
                            nombre,
                            primer_apellido,
                            segundo_apellido,
                            telefono,
                            correo,
                            `contraseña`,
                            fecha_registro
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                miembro.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE miembro
                    SET
                        nombre = %s,
                        primer_apellido = %s,
                        segundo_apellido = %s,
                        telefono = %s,
                        correo = %s,
                        `contraseña` = %s,
                        fecha_registro = %s
                    WHERE
                        num = %s
                    """,
                    valores + (miembro.num,),
                )

# Elimina un miembro por su número.
def eliminar_miembro(num):
    consulta = """
        DELETE FROM miembro
        WHERE num = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num,))
