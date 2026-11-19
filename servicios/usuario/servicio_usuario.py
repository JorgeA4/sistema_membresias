from datetime import date

import base_de_datos.consultas as bd
from clases.rol import Rol
from clases.usuario import Usuario
from servicios.autorizacion.servicio_autorizacion import requiere_administrador
from utilidades.seguridad import hashear_contraseña


def registrar_usuario(usuario: Usuario, datos: dict) -> Usuario:
    requiere_administrador(usuario)
    correo = datos["correo"].strip()
    if not correo:
        raise ValueError("El correo es obligatorio.")
    if bd.buscar_usuario_por_correo(correo) is not None:
        raise ValueError("El correo ya está registrado.")

    nuevo_usuario = Usuario(
        num=None,
        nombre=datos["nombre"],
        primer_apellido=datos["primer_apellido"],
        segundo_apellido=datos.get("segundo_apellido"),
        telefono=datos.get("telefono"),
        correo=correo,
        contraseña=hashear_contraseña(datos["contraseña"]),
        rol=_obtener_rol(datos),
        fecha_registro=datos.get("fecha_registro", date.today()),
    )
    bd.guardar_usuario(nuevo_usuario)
    return nuevo_usuario


def consultar_usuario(num: int) -> Usuario | None:
    return bd.buscar_usuario_por_num(num)


def obtener_usuarios() -> list[Usuario]:
    return bd.obtener_todos_los_usuarios()


def modificar_usuario(usuario: Usuario, num: int, datos: dict) -> Usuario:
    requiere_administrador(usuario)
    objetivo = consultar_usuario(num)
    if objetivo is None:
        raise ValueError("El usuario no existe.")

    atributos_permitidos = {
        "nombre",
        "primer_apellido",
        "segundo_apellido",
        "telefono",
        "correo",
        "contraseña",
        "rol",
        "codigo_rol",
    }
    if set(datos) - atributos_permitidos:
        raise ValueError("Los datos contienen atributos no modificables.")

    if "correo" in datos:
        correo = datos["correo"].strip()
        existente = bd.buscar_usuario_por_correo(correo)
        if existente is not None and existente.num != num:
            raise ValueError("El correo ya está registrado.")
        objetivo.correo = correo

    for atributo in ("nombre", "primer_apellido", "segundo_apellido", "telefono"):
        if atributo in datos:
            setattr(objetivo, atributo, datos[atributo])

    if "contraseña" in datos:
        objetivo.contraseña = hashear_contraseña(datos["contraseña"])
    if "rol" in datos or "codigo_rol" in datos:
        objetivo.rol = _obtener_rol(datos)

    bd.guardar_usuario(objetivo)
    return objetivo


def eliminar_usuario(usuario: Usuario, num: int) -> None:
    requiere_administrador(usuario)
    objetivo = consultar_usuario(num)
    if objetivo is None:
        raise ValueError("El usuario no existe.")
    if objetivo.num == usuario.num:
        raise ValueError("No se puede eliminar el usuario autenticado.")
    bd.eliminar_usuario(num)


def _obtener_rol(datos: dict) -> Rol:
    referencia = datos.get("rol")
    if isinstance(referencia, str):
        rol = bd.buscar_rol_por_codigo(referencia)
    elif referencia is None:
        rol = bd.buscar_rol_por_codigo(datos.get("codigo_rol"))
    else:
        rol = referencia
    if not isinstance(rol, Rol):
        raise ValueError("El rol no existe.")
    return rol
