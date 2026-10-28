from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from interfaz.componentes.botones import boton_volver
from interfaz.componentes.mensajes import advertencia, informacion


class PantallaInicioSesion(QWidget):
    """Pantalla de inicio de sesión de Nexum."""

    # Emitida cuando el login es exitoso; lleva el tipo ("miembro" o "usuario")
    login_exitoso = Signal(str)
    # Emitida cuando el usuario presiona "Volver"
    volver = Signal()

    def __init__(self):
        super().__init__()
        self.tipo = None     # se asigna con preparar() antes de mostrar la pantalla
        self._construir()

    def preparar(self, tipo):
        """Recibe el tipo de usuario ('miembro' o 'usuario') y actualiza el encabezado."""
        self.tipo = tipo
        self.etiqueta_tipo.setText(f"Ingresando como: {tipo.capitalize()}")
        # Limpiamos los campos cada vez que se entra a esta pantalla
        self.campo_correo.clear()
        self.campo_contra.clear()

    def _construir(self):
        # Encabezado
        titulo = QLabel("NEXUM")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo = QLabel("Sistema de membresías y fidelización")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta que muestra el tipo elegido; se actualiza con preparar()
        self.etiqueta_tipo = QLabel("")
        self.etiqueta_tipo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        encabezado = QVBoxLayout()
        encabezado.addWidget(titulo)
        encabezado.addWidget(subtitulo)
        encabezado.addWidget(self.etiqueta_tipo)

        # Campo correo
        layout_correo, self.campo_correo = self._campo(
            "Correo electrónico", "Ingrese su correo"
        )

        # Campo contraseña
        layout_contra, self.campo_contra = self._campo(
            "Contraseña", "Ingrese su contraseña", echo=QLineEdit.EchoMode.Password
        )

        # Botones
        boton_iniciar = QPushButton("Iniciar sesión")
        boton_iniciar.clicked.connect(self._iniciar_sesion)

        boton_salir = QPushButton("Salir")
        boton_salir.clicked.connect(QApplication.quit)

        btn_volver = boton_volver(self.volver)

        diseño_botones = QHBoxLayout()
        diseño_botones.addWidget(btn_volver)
        diseño_botones.addWidget(boton_iniciar)
        diseño_botones.addWidget(boton_salir)
        diseño_botones.setSpacing(10)
        diseño_botones.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout principal
        diseño = QVBoxLayout()
        diseño.addLayout(encabezado)
        diseño.addLayout(layout_correo)
        diseño.addLayout(layout_contra)
        diseño.addLayout(diseño_botones)
        diseño.setContentsMargins(40, 40, 40, 40)
        diseño.setSpacing(15)
        diseño.addStretch()

        self.setLayout(diseño)

    def _campo(self, etiqueta, placeholder, echo=QLineEdit.EchoMode.Normal):
        """Crea un par etiqueta + campo de texto y devuelve (layout, campo)."""
        texto = QLabel(etiqueta + ": ")
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setEchoMode(echo)
        layout = QHBoxLayout()
        layout.addWidget(texto)
        layout.addWidget(campo)
        return layout, campo

    def _iniciar_sesion(self):
        correo = self.campo_correo.text().strip()
        contra = self.campo_contra.text().strip()

        if not correo or not contra:
            advertencia(self, "Por favor complete el correo y la contraseña.")
            return

        # Por ahora confirmamos con un mensaje; aquí irá el servicio de autenticación
        informacion(self, f"Tipo: {self.tipo}\nCorreo: {correo}")
        self.login_exitoso.emit(self.tipo)
