"""
Componentes de formulario para la interfaz de terminal.

Ofrece dos funciones:
  - pedir_campo()      → solicita un campo individual con etiqueta.
  - pedir_formulario() → solicita varios campos, muestra resumen y pide confirmación.
"""

import getpass

from rich.console import Console
from rich.table import Table

from interfaz_term.estilos.tema import COLOR_ENCABEZADO, ESTILO_TABLA
import questionary

_consola = Console()


def pedir_campo(etiqueta: str, requerido: bool = True, contrasena: bool = False) -> str:
    """
    Muestra la etiqueta con Rich y recoge el valor con input() o getpass.

    Parámetros:
        etiqueta   — texto descriptivo del campo.
        requerido  — si es True, no acepta valores vacíos (repite el prompt).
        contrasena — si es True, usa getpass para no mostrar el texto.

    Devuelve el valor ingresado.
    """
    while True:
        _consola.print(f"[{COLOR_ENCABEZADO}]{etiqueta}:[/{COLOR_ENCABEZADO}]", end=" ")
        if contrasena:
            valor = getpass.getpass("")
        else:
            valor = input()

        valor = valor.strip()
        if requerido and not valor:
            _consola.print("[yellow]Este campo es obligatorio.[/yellow]")
            continue

        return valor


def pedir_formulario(campos: list[dict]) -> dict | None:
    """
    Solicita una lista de campos, muestra un resumen y pide confirmación.

    Cada elemento de `campos` es un dict con las claves:
        - clave      (str) — nombre interno del campo, usado como clave del dict devuelto.
        - etiqueta   (str) — texto mostrado al usuario.
        - requerido  (bool, opcional, default True)
        - contrasena (bool, opcional, default False)

    Flujo:
        1. Pide todos los campos en orden.
        2. Muestra un resumen con Rich (oculta contraseñas).
        3. Pregunta si confirmar o corregir.
           - Si confirma → devuelve el dict de valores.
           - Si elige corregir → permite editar campo por campo y repite el resumen.
           - Si cancela → devuelve None.

    Ejemplo:
        resultado = pedir_formulario([
            {"clave": "nombre",  "etiqueta": "Nombre completo"},
            {"clave": "correo",  "etiqueta": "Correo electrónico"},
            {"clave": "contra",  "etiqueta": "Contraseña", "contrasena": True},
        ])
    """
    valores: dict = {}

    # Paso 1: recoger todos los campos
    for campo in campos:
        clave      = campo["clave"]
        etiqueta   = campo["etiqueta"]
        requerido  = campo.get("requerido", True)
        contrasena = campo.get("contrasena", False)
        valores[clave] = pedir_campo(etiqueta, requerido=requerido, contrasena=contrasena)

    while True:
        # Paso 2: mostrar resumen
        _mostrar_resumen(campos, valores)

        # Paso 3: confirmar, corregir o cancelar
        accion = questionary.select(
            "¿Qué deseas hacer?",
            choices=["Confirmar", "Corregir un campo", "Cancelar"],
        ).ask()

        if accion == "Confirmar":
            return valores

        if accion == "Cancelar":
            return None

        # Corregir: elegir qué campo editar
        etiquetas = [c["etiqueta"] for c in campos]
        etiqueta_elegida = questionary.select(
            "Selecciona el campo a corregir:",
            choices=etiquetas,
        ).ask()

        campo_elegido = next(c for c in campos if c["etiqueta"] == etiqueta_elegida)
        clave      = campo_elegido["clave"]
        requerido  = campo_elegido.get("requerido", True)
        contrasena = campo_elegido.get("contrasena", False)
        valores[clave] = pedir_campo(etiqueta_elegida, requerido=requerido, contrasena=contrasena)


def _mostrar_resumen(campos: list[dict], valores: dict) -> None:
    """Muestra un resumen de los valores del formulario con Rich."""
    tabla = Table(title="Resumen", header_style=ESTILO_TABLA, show_lines=True)
    tabla.add_column("Campo")
    tabla.add_column("Valor")

    for campo in campos:
        clave      = campo["clave"]
        etiqueta   = campo["etiqueta"]
        contrasena = campo.get("contrasena", False)
        valor_mostrado = "••••••••" if contrasena else valores.get(clave, "")
        tabla.add_row(etiqueta, valor_mostrado)

    _consola.print(tabla)
