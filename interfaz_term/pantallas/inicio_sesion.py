"""
Pantalla de inicio de sesión de Nexum.

Muestra un formulario con correo y contraseña. Realiza validación básica
de campos vacíos. La autenticación real se conectará cuando el servicio
de autenticación esté disponible.

Firma: mostrar_login_con_volver(sesion) -> (interfaz, pantalla)
    interfaz  — sesion["interfaz"] sin cambios (se mantiene "miembro" o "usuario")
    pantalla  — 3 (menú principal) | 4 (volver)
"""

import getpass

from rich.console import Console
from rich.panel import Panel
from rich import box as rich_box

import questionary

from interfaz_term.estilos.tema import (
    COLOR_ENCABEZADO,
    COLOR_TITULO,
)
from interfaz_term.componentes.mensajes import advertencia, error
from servicios.autenticacion.servicio_autenticacion import (
    autenticar_miembro,
    autenticar_usuario,
)

_consola = Console()


def _mostrar_formulario(tipo: str) -> dict | None:
    """
    Muestra los campos de correo y contraseña y valida que no estén vacíos.
    Devuelve una identidad neutral cuando las credenciales son válidas.
    """
    while True:
        _consola.clear()
        _consola.print(
            Panel(
                f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}]\n"
                f"[dim]Sistema de membresías y fidelización[/dim]\n\n"
                f"Ingresando como: [{COLOR_ENCABEZADO}]{tipo.capitalize()}[/{COLOR_ENCABEZADO}]",
                border_style=COLOR_ENCABEZADO,
                box=rich_box.ROUNDED,
                padding=(1, 4),
            )
        )

        _consola.print(f"\n[{COLOR_ENCABEZADO}]Correo electrónico:[/{COLOR_ENCABEZADO}]", end=" ")
        correo = input().strip()

        _consola.print(f"[{COLOR_ENCABEZADO}]Contraseña:[/{COLOR_ENCABEZADO}]", end=" ")
        contra = getpass.getpass("").strip()

        if not correo or not contra:
            advertencia("Por favor complete el correo y la contraseña.")
            continue

        autenticar = autenticar_miembro if tipo == "miembro" else autenticar_usuario
        identidad = autenticar(correo, contra)
        if identidad is None:
            error("El correo o la contraseña no son válidos.")
            continue

        return identidad


def mostrar_login_con_volver(sesion: dict) -> tuple:
    """
    Pantalla de inicio de sesión con opción de volver.

    Lee sesion["interfaz"] para obtener el tipo ("miembro" o "usuario").

    Devuelve:
        (sesion["interfaz"], 3) — login exitoso; ir al menú principal.
        (None, 4)              — el usuario eligió volver a la pantalla de bienvenida.
    """
    tipo = sesion["interfaz"]

    _consola.clear()
    _consola.print(
        Panel(
            f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}]\n"
            f"[dim]Sistema de membresías y fidelización[/dim]\n\n"
            f"Ingresando como: [{COLOR_ENCABEZADO}]{tipo.capitalize()}[/{COLOR_ENCABEZADO}]",
            border_style=COLOR_ENCABEZADO,
            box=rich_box.ROUNDED,
            padding=(1, 4),
        )
    )

    accion = questionary.select(
        "¿Qué deseas hacer?",
        choices=["Iniciar sesión", "← Volver"],
    ).ask()

    if accion != "Iniciar sesión":
        sesion["identidad"] = None
        return tipo, 4

    sesion["identidad"] = _mostrar_formulario(tipo)
    return tipo, 3
