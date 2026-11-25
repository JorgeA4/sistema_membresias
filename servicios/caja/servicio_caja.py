from base_de_datos.consultas import transaccion
import base_de_datos.consultas.recompensas.consultas_recompensas as consultas_recompensas
import base_de_datos.consultas.puntos_y_cashback.consultas_puntos_y_cashback as consultas_puntos_y_cashback
from servicios.autorizacion.servicio_autorizacion import requiere_operador_tienda
from servicios.compra.servicio_compra import registrar_compra
from servicios.recompensa.servicio_recompensa import canjear_recompensa, validar_canje
from utilidades.excepciones import EntidadNoEncontrada, VersionNoVigente


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

    with transaccion():

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
        transacciones_puntos = (
            consultas_puntos_y_cashback
            .obtener_transacciones_de_miembro(compra.membresia.miembro.num)
        )
        transacciones_puntos = [
            transaccion for transaccion in transacciones_puntos
            if transaccion.membresia is not None
            and transaccion.membresia.num == compra.membresia.num
            and transaccion.compra is not None
            and transaccion.compra.num == compra.num
        ]
        puntos_generados = sum(
            transaccion.movimiento
            for transaccion in transacciones_puntos
            if transaccion.movimiento > 0
            and transaccion.version_recompensa is None
        )

        transacciones_cashback = (
            consultas_puntos_y_cashback
            .obtener_transacciones_cashback_de_membresia(compra.membresia.num)
        )
        cashback_generado = sum(
            (
                transaccion.monto
                for transaccion in transacciones_cashback
                if transaccion.compra is not None
                and transaccion.compra.num == compra.num
                and transaccion.monto > 0
            ),
            0,
        )
        return {
            "compra": compra,
            "canje": canje,
            "puntos_generados": puntos_generados,
            "cashback_generado": cashback_generado,
        }


def _obtener_version_recompensa_vigente(codigo: str):
    recompensa = consultas_recompensas.buscar_recompensa_por_codigo(codigo.strip())
    if recompensa is None:
        raise EntidadNoEncontrada("La recompensa no existe.")
    versiones = [
        version
        for version in consultas_recompensas.obtener_versiones_de_recompensa(codigo)
        if version.esta_vigente()
    ]
    if len(versiones) != 1:
        raise VersionNoVigente("La recompensa no tiene una única versión vigente.")
    return versiones[0]
