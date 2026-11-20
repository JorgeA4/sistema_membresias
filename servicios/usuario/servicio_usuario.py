from datetime import date

import base_de_datos.consultas as bd
from clases.rol import Rol
from clases.usuario import Usuario
from servicios.autorizacion.servicio_autorizacion import requiere_administrador
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    OperacionNoPermitida,
)
from utilidades.seguridad import hashear_contraseña


def registrar_usuario(identidad: dict, datos: dict) -> Usuario:
    requiere_administrador(identidad)
    correo = datos["correo"].strip()
    if not correo:
        raise DatosInvalidos("El correo es obligatorio.")
    if bd.buscar_usuario_por_correo(correo) is not None:
        raise DatosInvalidos("El correo ya está registrado.")

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


def consultar_usuario(identidad: dict, num: int) -> Usuario | None:
    requiere_administrador(identidad)
    return bd.buscar_usuario_por_num(num)


def obtener_usuarios(identidad: dict) -> list[Usuario]:
    requiere_administrador(identidad)
    return bd.obtener_todos_los_usuarios()


def obtener_actividad_usuario(identidad: dict, num: int):
    requiere_administrador(identidad)
    if bd.buscar_usuario_por_num(num) is None:
        raise EntidadNoEncontrada("El usuario no existe.")
    return bd.obtener_compras_de_usuario(num)


def modificar_usuario(identidad: dict, num: int, datos: dict) -> Usuario:
    requiere_administrador(identidad)
    objetivo = bd.buscar_usuario_por_num(num)
    if objetivo is None:
        raise EntidadNoEncontrada("El usuario no existe.")

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
        raise DatosInvalidos("Los datos contienen atributos no modificables.")

    if "correo" in datos:
        correo = datos["correo"].strip()
        existente = bd.buscar_usuario_por_correo(correo)
        if existente is not None and existente.num != num:
            raise DatosInvalidos("El correo ya está registrado.")
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


def eliminar_usuario(identidad: dict, num: int) -> None:
    requiere_administrador(identidad)
    objetivo = bd.buscar_usuario_por_num(num)
    if objetivo is None:
        raise EntidadNoEncontrada("El usuario no existe.")
    if objetivo.num == identidad.get("num"):
        raise OperacionNoPermitida("No se puede eliminar el usuario autenticado.")
    if bd.tiene_historial_usuario(num):
        raise OperacionNoPermitida("No se puede eliminar un usuario con historial.")
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
        raise EntidadNoEncontrada("El rol no existe.")
    return rol
