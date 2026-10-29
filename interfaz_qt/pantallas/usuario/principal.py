from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from interfaz_qt.componentes.botones import boton_cerrar_sesion


class PantallaPrincipalUsuario(QWidget):
    """Pantalla principal de la interfaz de usuario administrativo (esqueleto)."""

    cerrar_sesion = Signal()

    def __init__(self):
        super().__init__()
        self._construir()

    def _construir(self):
        mensaje = QLabel("✓ Bienvenido. Estás en la interfaz de Usuario.")
        mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_cerrar = boton_cerrar_sesion(self.cerrar_sesion)

        diseño = QVBoxLayout()
        diseño.addStretch()
        diseño.addWidget(mensaje)
        diseño.addSpacing(20)
        diseño.addWidget(btn_cerrar)
        diseño.addStretch()
        diseño.setContentsMargins(40, 40, 40, 40)

        self.setLayout(diseño)
