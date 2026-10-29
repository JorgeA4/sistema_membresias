"""
Componente de tabla reutilizable para la interfaz de terminal.

Usa Rich para construir y mostrar tablas con estilo consistente.
"""

from rich.console import Console
from rich.table import Table

from interfaz_term.estilos.tema import BORDE_TABLA, ESTILO_TABLA

_consola = Console()


def mostrar_tabla(titulo: str, columnas: list[str], filas: list[tuple]) -> None:
    """
    Construye y muestra una tabla de Rich.

    Parámetros:
        titulo   — texto que aparece como título de la tabla.
        columnas — lista de nombres de columna.
        filas    — lista de tuplas; cada tupla es una fila con tantos
                   valores como columnas.

    Ejemplo:
        mostrar_tabla(
            "Miembros",
            ["Num", "Nombre", "Correo"],
            [(1, "Ana López", "ana@mail.com"), (2, "Carlos Ruiz", "c@mail.com")],
        )
    """
    tabla = Table(title=titulo, box=_caja(), header_style=ESTILO_TABLA)

    for nombre_col in columnas:
        tabla.add_column(nombre_col)

    for fila in filas:
        tabla.add_row(*[str(v) for v in fila])

    _consola.print(tabla)


def _caja():
    """Devuelve el objeto box de Rich que corresponde al estilo de borde configurado."""
    from rich import box as rich_box
    mapa = {
        "simple_head": rich_box.SIMPLE_HEAD,
        "simple":      rich_box.SIMPLE,
        "rounded":     rich_box.ROUNDED,
        "square":      rich_box.SQUARE,
        "minimal":     rich_box.MINIMAL,
    }
    return mapa.get(BORDE_TABLA, rich_box.SIMPLE_HEAD)
