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
            texto_secundario,
            title=f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}]",
            border_style=COLOR_BORDE_BANNER,
            box=rich_box.ROUNDED,
            padding=(0, 4),
        )
    )


def mostrar_banner_operacion(
    titulo: str,
    identidad: dict,
    contexto: list[str] | None = None,
    limpiar: bool = False,
) -> None:
    """Muestra el encabezado unificado de una operación o formulario."""
    if limpiar:
        _consola.clear()
    nombre = identidad.get("nombre", "")
    rol = identidad.get("rol_nombre", "Usuario")
    lineas = [f"Usuario: {nombre} | Rol: {rol}"]
    if contexto:
        lineas.extend(contexto)
    _consola.print(
        Panel(
            "\n".join(lineas),
            title=f"[{COLOR_TITULO}]{titulo}[/{COLOR_TITULO}]",
            border_style=COLOR_BORDE_BANNER,
            box=rich_box.ROUNDED,
            padding=(0, 2),
        )
    )
