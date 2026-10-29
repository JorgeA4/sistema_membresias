"""
Punto de entrada de la interfaz de terminal de Nexum.

Contiene ejecutar_aplicacion() con el loop principal de navegación.
Las pantallas devuelven strings que indican la siguiente pantalla;
este módulo decide a cuál llamar según ese valor.

Flujo:
    Bienvenida → elige tipo → Login
    Login → Volver → Bienvenida
    Login → credenciales correctas → Miembro o Usuario según tipo
    Miembro / Usuario → Cerrar sesión → Bienvenida
"""

from interfaz_term.pantallas.bienvenida import mostrar_bienvenida
from interfaz_term.pantallas.inicio_sesion import mostrar_login_con_volver
from interfaz_term.pantallas.miembro.principal import mostrar_miembro
from interfaz_term.pantallas.usuario.principal import mostrar_usuario

def ejecutar_aplicacion() -> None:

    def volver(sesion):
        del sesion["historial"][-2:]
        if sesion["historial"][-1] == 1:
            interfaz = None
        else:
            interfaz = sesion["interfaz"]
        return interfaz, None

    def ejecutar_menu(sesion):
        interfaz, pantalla = flujo[sesion["interfaz"]][sesion["historial"][-1]](sesion)
        sesion["interfaz"] = interfaz
        sesion["historial"].append(pantalla)
        if sesion["historial"][-1] == None:
            sesion["historial"].pop(-1)

    """Loop principal de navegación de la aplicación."""
    sesion = {
        "interfaz": None,
        "historial": []
    }

    flujo = {
        None:{
            1:mostrar_bienvenida
        },
        "miembro": {
            2:mostrar_login_con_volver,
            3:mostrar_miembro,
            4:volver
        },
        "usuario": {
            2:mostrar_login_con_volver,
            3:mostrar_usuario,
            4:volver
        }
    }

    sesion["historial"].append(1)

    while True:
        
        if sesion["historial"][-1] == 5:
            break
        
        else:
            ejecutar_menu(sesion)

if __name__ == "__main__":
    ejecutar_aplicacion()
