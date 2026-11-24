from clases.compra import Compra
from clases.membresia import Membresia
from clases.miembro import Miembro
from clases.plan import Plan
from clases.recompensa import Recompensa
from clases.renovacion import Renovacion
from clases.rol import Rol
from clases.transaccion_cashback import TransaccionCashback
from clases.transaccion_puntos import TransaccionPuntos
from clases.usuario import Usuario
from clases.version_plan import (
    ConfigCashback,
    ConfigDescuento,
    ConfigPuntos,
    DiaAplicableDesc,
    TipoAplicacionPlan,
    VersionPlan,
)
from clases.version_recompensa import VersionRecompensa

# convierte una fila en un miembro
def mapear_miembro(fila):
    if fila is None:
        return None
    return Miembro(
        fila["num"], fila["nombre"], fila["primer_apellido"],
        fila["segundo_apellido"], fila["telefono"], fila["correo"],
        fila["contraseña"], fila["fecha_registro"],
    )

# convierte una fila en un rol
def mapear_rol(fila):
    if fila is None:
        return None
    return Rol(fila["codigo"], fila["nombre"], fila["descripcion"])

# convierte una fila en un usaurio
def mapear_usuario(fila, rol):
    if fila is None:
        return None
    return Usuario(
        fila["num"], fila["nombre"], fila["primer_apellido"],
        fila["segundo_apellido"], fila["telefono"], fila["correo"],
        fila["contraseña"], rol, fila["fecha_registro"],
    )

# convierte una fila en un plan
def mapear_plan(fila):
    if fila is None:
        return None
    return Plan(fila["codigo"], fila["nombre"], fila["descripcion"])

# convierte una fila en una recompensa
def mapear_recompensa(fila):
    if fila is None:
        return None
    return Recompensa(fila["codigo"], fila["nombre"], fila["descripcion"])

# convierte una fila y sus configuraciones en una version de plan
def mapear_version_plan(fila, plan, configuracion_cashback,
                        configuracion_puntos, configuracion_descuento,
                        version_base_de_promo=None):
    if fila is None:
        return None
    return VersionPlan(
        fila["num"], fila["fecha_inicio"], fila["fecha_final"],
        fila["precio"], fila["plazo_meses"],
        TipoAplicacionPlan(fila["aplica_en"]), plan,
        configuracion_cashback, configuracion_puntos,
        configuracion_descuento, version_base_de_promo,
    )

# convierte la configuracion de cashback de una fila
def mapear_configuracion_cashback(fila):
    if fila is None or fila["config_cashback_num"] is None:
        return None
    return ConfigCashback(
        fila["config_cashback_num"], fila["config_cashback_porcentaje"],
        fila["config_cashback_limite"],
    )

# convierte la configuracion de puntos de una fila
def mapear_configuracion_puntos(fila):
    if fila is None or fila["config_puntos_num"] is None:
        return None
    return ConfigPuntos(
        fila["config_puntos_num"], fila["config_puntos_porcentaje"],
        fila["config_puntos_vigencia"],
    )

# convierte la configuracion de descuento y sus dias
def mapear_configuracion_descuento(fila, dias):
    if fila is None or fila["config_descuento_num"] is None:
        return None
    configuracion = ConfigDescuento(
        fila["config_descuento_num"], fila["config_descuento_porcentaje"],
        fila["config_descuento_minimo"],
    )
    configuracion.dias_aplicables = [
        DiaAplicableDesc(configuracion, dia) for dia in dias
    ]
    return configuracion

# convierte una fila en una version de recompensa
def mapear_version_recompensa(fila, recompensa):
    if fila is None:
        return None
    return VersionRecompensa(
        fila["num"], fila["costo_puntos"], fila["fecha_inicio"],
        fila["fecha_final"], fila["limite_canjes"], recompensa,
    )

# convierte una fila en una membresia
def mapear_membresia(fila, miembro, version_plan):
    if fila is None:
        return None
    return Membresia(
        fila["num"], fila["fecha_contratacion"], fila["estado"],
        miembro, version_plan,
    )

# convierte una fila en una compra
def mapear_compra(fila, membresia, usuario):
    if fila is None:
        return None
    return Compra(
        fila["num"], fila["monto_base"], fila["porcentaje_descuento"],
        fila["descuento_nominal"], fila["cashback_aplicado"],
        fila["monto_final"], membresia, usuario, fila.get("fecha"),
    )

# convierte una fila en una renovacion
def mapear_renovacion(fila, membresia, version_plan):
    if fila is None:
        return None
    return Renovacion(
        fila["num"], fila["fecha_pago"], fila["monto_pagado"],
        fila["fecha_inicio_periodo"], fila["fecha_fin_periodo"],
        membresia, version_plan,
    )

# convierte una fila en una transaccion de puntos
def mapear_transaccion_puntos(fila, compra, version_recompensa, membresia):
    if fila is None:
        return None
    return TransaccionPuntos(
        fila["num"], fila["movimiento"], fila["saldo"], fila["fecha"],
        fila["concepto"], compra, version_recompensa, membresia,
    )

# convierte una fila en una transaccion de cashback
def mapear_transaccion_cashback(fila, compra, membresia):
    if fila is None:
        return None
    return TransaccionCashback(
        fila["num"], fila["monto"], fila["saldo"], fila["fecha"],
        fila["concepto"], compra, membresia,
    )
