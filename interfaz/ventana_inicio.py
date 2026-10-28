import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from interfaz.pantallas.bienvenida import PantallaBienvenida
from interfaz.pantallas.inicio_sesion import PantallaInicioSesion
from interfaz.pantallas.miembro.principal import PantallaPrincipalMiembro
from interfaz.pantallas.usuario.principal import PantallaPrincipalUsuario

# Índices de cada pantalla dentro del QStackedWidget
BIENVENIDA   = 0
INICIO_SESION = 1
MIEMBRO      = 2
USUARIO      = 3


def ejecutar_aplicacion():
    aplicacion = QApplication(sys.argv)

    ventana = QMainWindow()
    ventana.setWindowTitle("Nexum")
    ventana.resize(800, 500)

    # Creamos todas las pantallas
    bienvenida    = PantallaBienvenida()
    inicio_sesion = PantallaInicioSesion()
    miembro       = PantallaPrincipalMiembro()
    usuario       = PantallaPrincipalUsuario()

    # Las agregamos al stack en orden; el índice coincide con las constantes
    pila = QStackedWidget()
    pila.addWidget(bienvenida)     # 0 → BIENVENIDA
    pila.addWidget(inicio_sesion)  # 1 → INICIO_SESION
    pila.addWidget(miembro)        # 2 → MIEMBRO
    pila.addWidget(usuario)        # 3 → USUARIO

    # ── Bienvenida → InicioSesion ──────────────────────────────────────────
    def al_elegir_tipo(tipo):
        ventana.setWindowTitle(f"Nexum — {tipo.capitalize()}")
        inicio_sesion.preparar(tipo)
        pila.setCurrentIndex(INICIO_SESION)

    bienvenida.seleccion_hecha.connect(al_elegir_tipo)

    # ── InicioSesion → Miembro o Usuario (login exitoso) ───────────────────
    def al_iniciar_sesion(tipo):
        if tipo == "miembro":
            pila.setCurrentIndex(MIEMBRO)
        else:
            pila.setCurrentIndex(USUARIO)

    inicio_sesion.login_exitoso.connect(al_iniciar_sesion)

    # ── InicioSesion → Bienvenida (volver) ─────────────────────────────────
    inicio_sesion.volver.connect(lambda: pila.setCurrentIndex(BIENVENIDA))

    # ── Miembro / Usuario → Bienvenida (cerrar sesión) ─────────────────────
    def al_cerrar_sesion():
        ventana.setWindowTitle("Nexum")
        pila.setCurrentIndex(BIENVENIDA)

    miembro.cerrar_sesion.connect(al_cerrar_sesion)
    usuario.cerrar_sesion.connect(al_cerrar_sesion)

    ventana.setCentralWidget(pila)
    ventana.show()
    sys.exit(aplicacion.exec())


if __name__ == "__main__":
    ejecutar_aplicacion()
