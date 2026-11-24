from datetime import date

from base_de_datos.consultas import transaccion
import base_de_datos.consultas.miembros.consultas_miembros as consultas_miembros
import base_de_datos.consultas.miembros.operaciones_miembros as operaciones_miembros
from clases.miembro import Miembro
from servicios.autorizacion.servicio_autorizacion import (
    requiere_administrador,
    requiere_administrador_o_gerente,
    requiere_operador_tienda,
)
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    OperacionNoPermitida,
)
from utilidades.seguridad import hashear_contraseña


def registrar_miembro(identidad: dict, datos: dict) -> Miembro:
    requiere_operador_tienda(identidad)
    correo = datos["correo"].strip()
    if not correo:
        raise DatosInvalidos("El correo es obligatorio.")
    if consultas_miembros.buscar_miembro_por_correo(correo) is not None:
        raise DatosInvalidos("El correo ya está registrado.")
    miembro = Miembro(
        num=None,
        nombre=datos["nombre"],
        primer_apellido=datos["primer_apellido"],
        segundo_apellido=datos.get("segundo_apellido"),
        telefono=datos["telefono"],
        correo=correo,
        contraseña=hashear_contraseña(datos["contraseña"]),
        fecha_registro=datos.get("fecha_registro", date.today()),
    )
    operaciones_miembros.guardar_miembro(miembro)
    return miembro


def registrar_miembro_con_membresia(identidad: dict, datos: dict, num_version_plan: int):
    """Registra un miembro y contrata su primera membresía atomícamente."""
    requiere_operador_tienda(identidad)
    from servicios.membresia.servicio_membresia import contratar_membresia

    with transaccion():
        miembro = registrar_miembro(identidad, datos)
        renovacion = contratar_membresia(
            identidad,
            miembro.num,
            num_version_plan,
        )
        return miembro, renovacion


def consultar_miembro(identidad: dict, num: int) -> Miembro | None:
    if not isinstance(identidad, dict):
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")
    if identidad.get("tipo") == "usuario":
        requiere_operador_tienda(identidad)
    elif identidad.get("tipo") == "miembro":
        if identidad.get("num") != num:
            raise OperacionNoPermitida("No tiene permiso para consultar este miembro.")
    else:
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")
    return consultas_miembros.buscar_miembro_por_num(num)


def obtener_miembros(identidad: dict) -> list[Miembro]:
    requiere_operador_tienda(identidad)
    return consultas_miembros.obtener_todos_los_miembros()


def buscar_miembros(identidad: dict, filtros: dict) -> list[Miembro]:
    requiere_operador_tienda(identidad)
    return consultas_miembros.buscar_miembros(filtros)


def modificar_miembro(identidad: dict, num: int, datos: dict) -> Miembro:
    requiere_administrador_o_gerente(identidad)
    miembro = consultar_miembro(identidad, num)
    if miembro is None:
        raise EntidadNoEncontrada("El miembro no existe.")

    atributos_permitidos = {
        "nombre",
        "primer_apellido",
        "segundo_apellido",
        "telefono",
        "correo",
    }
    for atributo, valor in datos.items():
        if atributo in atributos_permitidos:
            setattr(miembro, atributo, valor)

    if "contraseña" in datos:
        miembro.contraseña = hashear_contraseña(datos["contraseña"])

    operaciones_miembros.guardar_miembro(miembro)
    return miembro


def eliminar_miembro(identidad: dict, num: int) -> None:
    requiere_administrador(identidad)
    if consultar_miembro(identidad, num) is None:
        raise EntidadNoEncontrada("El miembro no existe.")
    if consultas_miembros.tiene_historial_miembro(num):
        raise OperacionNoPermitida("No se puede eliminar un miembro con historial.")
    operaciones_miembros.eliminar_miembro(num)
