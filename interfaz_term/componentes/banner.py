"""Banner común para las pantallas de la interfaz de terminal."""

from rich import box as rich_box
from rich.console import Console
from rich.panel import Panel

from interfaz_term.estilos.tema import COLOR_BORDE_BANNER, COLOR_TITULO


_consola = Console()


def mostrar_banner(texto_secundario: str) -> None:
    """Limpia la consola y muestra el banner principal de Nexum."""
    _consola.clear()
    _consola.print(
        Panel(
            f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}]\n{texto_secundario}",
            border_style=COLOR_BORDE_BANNER,
            box=rich_box.ROUNDED,
            padding=(0, 4),
        )
    )
