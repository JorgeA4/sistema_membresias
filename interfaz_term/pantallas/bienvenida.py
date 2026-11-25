"""
Pantalla de bienvenida de Nexum.

Muestra el nombre del sistema y permite elegir el tipo de acceso:
Miembro o Usuario.

Firma: mostrar_bienvenida(sesion) -> (interfaz, pantalla)
    interfaz  — "miembro" | "usuario" | None
    pantalla  — 2 (login) | 5 (salir)
"""

import questionary

from interfaz_term.componentes.preguntas import seleccionar

from interfaz_term.componentes.banner import mostrar_banner


def mostrar_bienvenida(sesion: dict) -> tuple:
    """
    Pantalla inicial de selección de tipo de acceso.

    Devuelve:
        ("miembro", 2) — el usuario eligió acceder como miembro.
        ("usuario", 2) — el usuario eligió acceder como usuario administrativo.
        (None, 5)      — el usuario eligió salir de la aplicación.
    """
    mostrar_banner("[dim]Sistema de membresías y fidelización[/dim]")

    eleccion = seleccionar(
        "¿Cómo deseas ingresar?",
        choices=["Soy miembro", "Soy usuario", "Salir"],
    ).ask()

    if eleccion == "Soy miembro":
        sesion["identidad"] = None
        return "miembro", 2
    if eleccion == "Soy usuario":
        sesion["identidad"] = None
        return "usuario", 2
    return None, 5
