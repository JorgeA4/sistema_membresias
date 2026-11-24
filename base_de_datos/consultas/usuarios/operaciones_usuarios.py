"""Acceso persistente de usuarios."""

from base_de_datos.ejecutor import usar_conexion

# Guarda un usuario nuevo o actualizado.
def guardar_usuario(usuario):
    with usar_conexion() as conexion:
        valores = (
            usuario.nombre, usuario.primer_apellido, usuario.segundo_apellido,
            usuario.telefono, usuario.correo, usuario.contraseña,
            usuario.fecha_registro, usuario.rol.codigo,
        )
        with conexion.cursor() as cursor:
            if usuario.num is None:
                cursor.execute(
                    """
                    INSERT INTO usuario
                        (
                            nombre,
                            primer_apellido,
                            segundo_apellido,
                            telefono,
                            correo,
                            `contraseña`,
                            fecha_registro,
                            rol
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                usuario.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE usuario
                    SET
                        nombre = %s,
                        primer_apellido = %s,
                        segundo_apellido = %s,
                        telefono = %s,
                        correo = %s,
                        `contraseña` = %s,
                        fecha_registro = %s,
                        rol = %s
                    WHERE
                        num = %s
                    """,
                    valores + (usuario.num,),
                )

# Elimina un usuario por su número.
def eliminar_usuario(num):
    consulta = """
        DELETE FROM usuario
        WHERE num = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num,))
