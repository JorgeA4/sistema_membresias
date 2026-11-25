"""Preguntas interactivas con configuración común para la interfaz."""

import questionary


def seleccionar(*argumentos, **opciones):
    """Muestra una selección sin el texto de ayuda predeterminado."""
    opciones.setdefault("instruction", " ")
    return questionary.select(*argumentos, **opciones)
