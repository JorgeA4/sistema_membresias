from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PantallaBienvenida(QWidget):
    """Pantalla inicial donde el usuario elige si es Miembro o Usuario."""

    # Señal propia: se emite cuando el usuario elige su tipo.
    # Envía un string: "miembro" o "usuario".
    seleccion_hecha = Signal(str)

    def __init__(self):
        super().__init__()
        self._construir()

    def _construir(self):
        titulo = QLabel("NEXUM")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Sistema de membresías y fidelización")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pregunta = QLabel("¿Cómo deseas ingresar?")
        pregunta.setAlignment(Qt.AlignmentFlag.AlignCenter)

        boton_miembro = QPushButton("Soy miembro")
        boton_usuario = QPushButton("Soy usuario")

        # Al hacer clic, emitimos la señal con el tipo correspondiente
        boton_miembro.clicked.connect(lambda: self.seleccion_hecha.emit("miembro"))
        boton_usuario.clicked.connect(lambda: self.seleccion_hecha.emit("usuario"))

        diseño = QVBoxLayout()
        diseño.addStretch()
        diseño.addWidget(titulo)
        diseño.addWidget(subtitulo)
        diseño.addSpacing(30)
        diseño.addWidget(pregunta)
        diseño.addSpacing(10)
        diseño.addWidget(boton_miembro)
        diseño.addWidget(boton_usuario)
        diseño.addStretch()
        diseño.setContentsMargins(100, 40, 100, 40)
        diseño.setSpacing(10)

        self.setLayout(diseño)
