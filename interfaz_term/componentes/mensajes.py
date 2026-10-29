"""
Componentes de mensajes para la interfaz de terminal.

Cada función dibuja un Panel de Rich con el color apropiado y espera
que el usuario presione Enter para continuar.
"""

from rich.console import Console
from rich.panel import Panel

from interfaz_term.estilos.tema import (
    BORDE_PANEL,
    COLOR_ADVERTENCIA,
    COLOR_ERROR,
    COLOR_INFO,
    COLOR_EXITO,
    TITULO_ADVERTENCIA,
    TITULO_ERROR,
    TITULO_INFO,
    TITULO_EXITO,
)

import questionary

_consola = Console()


def informacion(texto: str) -> None:
    """Muestra un panel azul informativo y espera que el usuario presione Enter."""
    _consola.print(
        Panel(texto, title=TITULO_INFO, border_style=COLOR_INFO, box=_caja())
    )
    input()


def advertencia(texto: str) -> None:
    """Muestra un panel amarillo de advertencia y espera que el usuario presione Enter."""
    _consola.print(
        Panel(texto, title=TITULO_ADVERTENCIA, border_style=COLOR_ADVERTENCIA, box=_caja())
    )
    input()


def error(texto: str) -> None:
    """Muestra un panel rojo de error y espera que el usuario presione Enter."""
    _consola.print(
        Panel(texto, title=TITULO_ERROR, border_style=COLOR_ERROR, box=_caja())
    )
    input()


def exito(texto: str) -> None:
    """Muestra un panel verde de éxito y espera que el usuario presione Enter."""
    _consola.print(
        Panel(texto, title=TITULO_EXITO, border_style=COLOR_EXITO, box=_caja())
    )
    input()


def confirmar(pregunta: str) -> bool:
    """Muestra una confirmación Sí/No con questionary. Devuelve True si el usuario confirmó."""
    return questionary.confirm(pregunta).ask()


def _caja():
    """Devuelve el objeto box de Rich que corresponde al estilo de borde configurado."""
    from rich import box as rich_box
    mapa = {
        "rounded": rich_box.ROUNDED,
        "square":  rich_box.SQUARE,
        "simple":  rich_box.SIMPLE,
    }
    return mapa.get(BORDE_PANEL, rich_box.ROUNDED)
