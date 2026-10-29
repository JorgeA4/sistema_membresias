from PySide6.QtWidgets import QMessageBox


def advertencia(padre, mensaje):
    """Muestra un cuadro de advertencia (campos vacíos, datos inválidos, etc.)."""
    QMessageBox.warning(padre, "Advertencia", mensaje)


def error(padre, mensaje):
    """Muestra un cuadro de error (fallo de autenticación, error del sistema, etc.)."""
    QMessageBox.critical(padre, "Error", mensaje)


def informacion(padre, mensaje):
    """Muestra un cuadro informativo (operación exitosa, confirmación, etc.)."""
    QMessageBox.information(padre, "Información", mensaje)


def confirmar(padre, pregunta):
    """Muestra un diálogo Sí/No. Devuelve True si el usuario confirmó."""
    respuesta = QMessageBox.question(padre, "Confirmar", pregunta)
    return respuesta == QMessageBox.StandardButton.Yes
