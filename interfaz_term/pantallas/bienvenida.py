"""
Pantalla de bienvenida de Nexum.

Muestra el nombre del sistema y permite elegir el tipo de acceso:
Miembro o Usuario.

Firma: mostrar_bienvenida(sesion) -> (interfaz, pantalla)
    interfaz  — "miembro" | "usuario" | None
    pantalla  — 2 (login) | 5 (salir)
"""

from rich.console import Console
from rich.panel import Panel
from rich import box as rich_box

import questionary

from interfaz_term.estilos.tema import (
    COLOR_ENCABEZADO,
    COLOR_TITULO,
)

_consola = Console()


def mostrar_bienvenida(sesion: dict) -> tuple:
    """
    Pantalla inicial de selección de tipo de acceso.

    Devuelve:
        ("miembro", 2) — el usuario eligió acceder como miembro.
        ("usuario", 2) — el usuario eligió acceder como usuario administrativo.
        (None, 5)      — el usuario eligió salir de la aplicación.
    """
    _consola.clear()
    _consola.print(
        Panel(
            f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}]\n"
            f"[dim]Sistema de membresías y fidelización[/dim]",
            border_style=COLOR_ENCABEZADO,
            box=rich_box.ROUNDED,
            padding=(1, 4),
        )
    )

    eleccion = questionary.select(
        "¿Cómo deseas ingresar?",
        choices=["Soy miembro", "Soy usuario", "Salir"],
    ).ask()

    if eleccion == "Soy miembro":
        return "miembro", 2
    if eleccion == "Soy usuario":
        return "usuario", 2
    return None, 5
