"""
Pantalla principal de la interfaz de miembro (esqueleto).

Muestra un mensaje de bienvenida y un menú con las opciones disponibles.
Por ahora solo contiene la opción de cerrar sesión; las demás se
agregarán cuando los servicios correspondientes estén disponibles.
"""

from rich.console import Console
from rich.panel import Panel
from rich import box as rich_box

import questionary

from interfaz_term.estilos.tema import COLOR_ENCABEZADO, COLOR_TITULO

_consola = Console()


def mostrar_miembro(sesion: dict) -> tuple:
    """
    Menú principal del miembro.

    Devuelve:
        (None, 1) — cuando el usuario elige cerrar sesión; vuelve a bienvenida.
    """
    while True:
        _consola.clear()
        _consola.print(
            Panel(
                f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}] — [dim]Interfaz de Miembro[/dim]",
                border_style=COLOR_ENCABEZADO,
                box=rich_box.ROUNDED,
                padding=(0, 4),
            )
        )
        _consola.print(
            f"\n[{COLOR_ENCABEZADO}]✓ Bienvenido. Estás en la interfaz de Miembro.[/{COLOR_ENCABEZADO}]\n"
        )

        accion = questionary.select(
            "¿Qué deseas hacer?",
            choices=[
                "Cerrar sesión",
            ],
        ).ask()

        if accion == "Cerrar sesión":
            return None, 1
