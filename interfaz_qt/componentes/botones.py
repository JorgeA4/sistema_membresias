from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


def boton_volver(señal: Signal) -> QPushButton:
    """
    Crea un botón 'Volver' ya conectado a la señal indicada.

    Uso:
        btn = boton_volver(self.volver)
        layout.addWidget(btn)
    """
    boton = QPushButton("← Volver")
    boton.clicked.connect(señal.emit)
    return boton


def boton_cerrar_sesion(señal: Signal) -> QPushButton:
    """
    Crea un botón 'Cerrar sesión' ya conectado a la señal indicada.

    Uso:
        btn = boton_cerrar_sesion(self.cerrar_sesion)
        layout.addWidget(btn)
    """
    boton = QPushButton("Cerrar sesión")
    boton.clicked.connect(señal.emit)
    return boton
