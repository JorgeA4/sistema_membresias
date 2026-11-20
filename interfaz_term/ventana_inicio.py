"""
Punto de entrada de la interfaz de terminal de Nexum.

Contiene ejecutar_aplicacion() con el loop principal de navegación.
Las pantallas devuelven tuplas que indican la siguiente pantalla;
este módulo decide a cuál llamar según ese valor.

Flujo:
    Bienvenida → elige tipo → Login
    Login → Volver → Bienvenida
    Login → credenciales correctas → Miembro o Usuario según tipo
    Miembro / Usuario → Cerrar sesión → Bienvenida
"""

from interfaz_term.pantallas.bienvenida import mostrar_bienvenida
from interfaz_term.pantallas.inicio_sesion import mostrar_login_con_volver
from interfaz_term.pantallas.miembro.principal import (
    mostrar_beneficios,
    mostrar_historial,
    mostrar_mi_cuenta,
    mostrar_miembro,
    mostrar_solicitudes_tienda,
)
from interfaz_term.pantallas.usuario.principal import (
    mostrar_actividad_ajustes,
    mostrar_menu_usuario,
    mostrar_detalle_miembro,
    mostrar_miembros_membresias,
    mostrar_operaciones_tienda,
    mostrar_planes,
    mostrar_recompensas,
    mostrar_resultados_miembros,
    mostrar_usuarios_permisos,
)
from interfaz_term.navegacion import (
    ACTIVIDAD_AJUSTES,
    BIENVENIDA,
    CERRAR_SESION,
    DETALLE_MIEMBRO,
    INICIO_SESION,
    BENEFICIOS,
    HISTORIAL,
    MENU_MIEMBRO,
    MENU_USUARIO,
    MI_CUENTA,
    MIEMBROS_MEMBRESIAS,
    OPERACIONES_TIENDA,
    PLANES,
    RECOMPENSAS,
    RESULTADOS_MIEMBROS,
    SOLICITUDES_TIENDA,
    USUARIOS_ADMINISTRATIVOS,
    VOLVER,
)

def ejecutar_aplicacion() -> None:

    def volver(sesion):
        if len(sesion["historial"]) > 1:
            sesion["historial"].pop()
        if sesion["historial"][-1] == BIENVENIDA:
            sesion["interfaz"] = None
            sesion["identidad"] = None
        return sesion["interfaz"], None

    def cerrar_sesion(sesion):
        sesion["interfaz"] = None
        sesion["identidad"] = None
        sesion["historial"] = [BIENVENIDA]
        return None, None

    def ejecutar_menu(sesion):
        interfaz_actual = sesion["interfaz"]
        interfaz, pantalla = flujo[interfaz_actual][sesion["historial"][-1]](sesion)
        sesion["interfaz"] = interfaz
        if pantalla == VOLVER:
            volver(sesion)
        elif pantalla == CERRAR_SESION:
            if interfaz_actual is None:
                sesion["historial"] = [CERRAR_SESION]
            else:
                cerrar_sesion(sesion)
        elif pantalla is not None:
            sesion["historial"].append(pantalla)

    """Loop principal de navegación de la aplicación."""
    sesion = {
        "interfaz": None,
        "identidad": None,
        "historial": []
    }

    flujo = {
        None:{
            BIENVENIDA:mostrar_bienvenida
        },
    "miembro": {
            INICIO_SESION:mostrar_login_con_volver,
            MENU_MIEMBRO:mostrar_miembro,
            MI_CUENTA:mostrar_mi_cuenta,
            BENEFICIOS:mostrar_beneficios,
            HISTORIAL:mostrar_historial,
            SOLICITUDES_TIENDA:mostrar_solicitudes_tienda,
            VOLVER:volver,
        },
        "usuario": {
            INICIO_SESION:mostrar_login_con_volver,
            MENU_USUARIO:mostrar_menu_usuario,
            OPERACIONES_TIENDA:mostrar_operaciones_tienda,
            MIEMBROS_MEMBRESIAS:mostrar_miembros_membresias,
            RESULTADOS_MIEMBROS:mostrar_resultados_miembros,
            DETALLE_MIEMBRO:mostrar_detalle_miembro,
            PLANES:mostrar_planes,
            RECOMPENSAS:mostrar_recompensas,
            USUARIOS_ADMINISTRATIVOS:mostrar_usuarios_permisos,
            ACTIVIDAD_AJUSTES:mostrar_actividad_ajustes,
            VOLVER:volver,
        }
    }

    sesion["historial"].append(BIENVENIDA)

    while True:
        
        if sesion["historial"][-1] == CERRAR_SESION:
            break
        ejecutar_menu(sesion)

if __name__ == "__main__":
    ejecutar_aplicacion()
