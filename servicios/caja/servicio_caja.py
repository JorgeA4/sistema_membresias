import base_de_datos.consultas as bd
from servicios.autorizacion.servicio_autorizacion import requiere_operador_tienda
from servicios.compra.servicio_compra import registrar_compra
from servicios.recompensa.servicio_recompensa import canjear_recompensa, validar_canje


def registrar_operacion_caja(identidad: dict, datos: dict) -> dict:
    """Registra una venta y, opcionalmente, un canje en la misma atención."""
    requiere_operador_tienda(identidad)
    num_membresia = datos.get("num_membresia")
    codigo_recompensa = datos.get("codigo_recompensa")
    version_recompensa = None

    # La validación previa permite conservar el ajuste de puntos vencidos
    # aunque el canje sea rechazado por saldo insuficiente.
    if codigo_recompensa:
        version_recompensa = _obtener_version_recompensa_vigente(codigo_recompensa)
        validar_canje(identidad, num_membresia, version_recompensa.num)

    with bd.transaccion():

        compra = registrar_compra(
            identidad,
            {
                "num_membresia": num_membresia,
                "monto_base": datos["monto_base"],
                "cashback_aplicado": datos.get("cashback_aplicado", 0),
            },
        )
        canje = None
        if version_recompensa is not None:
            canje = canjear_recompensa(
                identidad,
                num_membresia,
                version_recompensa.num,
                compra=compra,
            )
        return {"compra": compra, "canje": canje}


def _obtener_version_recompensa_vigente(codigo: str):
    recompensa = bd.buscar_recompensa_por_codigo(codigo.strip())
    if recompensa is None:
        raise ValueError("La recompensa no existe.")
    versiones = [
        version
        for version in bd.obtener_versiones_de_recompensa(codigo)
        if version.esta_vigente()
    ]
    if len(versiones) != 1:
        raise ValueError("La recompensa no tiene una única versión vigente.")
    return versiones[0]
