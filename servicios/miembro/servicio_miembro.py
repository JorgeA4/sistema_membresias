from datetime import date

import base_de_datos.consultas as bd
from clases.miembro import Miembro
from servicios.autorizacion.servicio_autorizacion import requiere_administrador
from utilidades.seguridad import hashear_contraseña


def registrar_miembro(identidad: dict, datos: dict) -> Miembro:
    requiere_administrador(identidad)
    miembro = Miembro(
        num=None,
        nombre=datos["nombre"],
        primer_apellido=datos["primer_apellido"],
        segundo_apellido=datos.get("segundo_apellido"),
        telefono=datos["telefono"],
        correo=datos["correo"],
        contraseña=hashear_contraseña(datos["contraseña"]),
        fecha_registro=datos.get("fecha_registro", date.today()),
    )
    bd.guardar_miembro(miembro)
    return miembro


def consultar_miembro(num: int) -> Miembro | None:
    return bd.buscar_miembro_por_num(num)


def obtener_miembros() -> list[Miembro]:
    return bd.obtener_todos_los_miembros()


def modificar_miembro(identidad: dict, num: int, datos: dict) -> Miembro:
    requiere_administrador(identidad)
    miembro = consultar_miembro(num)
    if miembro is None:
        raise ValueError("El miembro no existe.")

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

    bd.guardar_miembro(miembro)
    return miembro


def eliminar_miembro(identidad: dict, num: int) -> None:
    requiere_administrador(identidad)
    if consultar_miembro(num) is None:
        raise ValueError("El miembro no existe.")
    bd.eliminar_miembro(num)
