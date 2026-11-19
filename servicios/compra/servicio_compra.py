from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

import base_de_datos.consultas as bd
from clases.compra import Compra
from clases.membresia import Membresia
from clases.transaccion_cashback import TransaccionCashback
from clases.transaccion_puntos import TransaccionPuntos
from clases.usuario import Usuario


_DOS_DECIMALES = Decimal("0.01")


def registrar_compra(datos: dict) -> Compra:
    membresia = _obtener_membresia(datos)
    usuario = _obtener_usuario(datos)
    version = membresia.version_plan_actual

    if membresia.estado != Membresia.Estado.ACTIVA:
        raise ValueError("La membresía no está activa.")
    if version is None:
        raise ValueError("La membresía no tiene una versión de plan activa.")

    monto_base = _convertir_importe(datos["monto_base"])
    if monto_base <= 0:
        raise ValueError("El monto base debe ser mayor que cero.")

    fecha = date.today()
    descuento = _calcular_descuento(version.config_descuento, monto_base, fecha)
    monto_con_descuento = monto_base - descuento["nominal"]
    cashback_aplicado = _obtener_cashback_aplicado(
        datos,
        version.config_cashback,
        membresia.num,
        fecha,
        monto_con_descuento,
    )
    monto_final = _cuantificar(monto_con_descuento - cashback_aplicado)

    compra = Compra(
        num=None,
        monto_base=monto_base,
        porcentaje_descuento=descuento["porcentaje"],
        descuento_nominal=descuento["nominal"],
        cashback_aplicado=cashback_aplicado,
        monto_final=monto_final,
        membresia=membresia,
        usuario=usuario,
    )
    bd.guardar_compra(compra)

    _registrar_puntos(compra, version.config_puntos)
    _registrar_cashback(
        compra,
        version.config_cashback,
        cashback_aplicado,
        fecha,
    )
    return compra


def obtener_compras_de_membresia(num_membresia: int) -> list[Compra]:
    _verificar_membresia(num_membresia)
    return bd.obtener_compras_de_membresia(num_membresia)


def obtener_transacciones_de_miembro(num_miembro: int) -> list[TransaccionPuntos]:
    if bd.buscar_miembro_por_num(num_miembro) is None:
        raise ValueError("El miembro no existe.")
    return sorted(
        bd.obtener_transacciones_de_miembro(num_miembro),
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    )


def obtener_saldo_de_miembro(num_miembro: int) -> int:
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    if not transacciones:
        return 0
    return transacciones[-1].saldo


def obtener_transacciones_cashback_de_membresia(
    num_membresia: int,
) -> list[TransaccionCashback]:
    _verificar_membresia(num_membresia)
    return sorted(
        bd.obtener_transacciones_cashback_de_membresia(num_membresia),
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    )


def obtener_saldo_cashback_de_membresia(num_membresia: int) -> Decimal:
    transacciones = obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        return Decimal("0.00")
    return transacciones[-1].saldo


def _obtener_membresia(datos: dict) -> Membresia:
    referencia = datos.get("membresia")
    if isinstance(referencia, int):
        membresia = bd.buscar_membresia_por_num(referencia)
    elif referencia is None:
        membresia = bd.buscar_membresia_por_num(datos.get("num_membresia"))
    else:
        membresia = referencia
    if not isinstance(membresia, Membresia):
        raise ValueError("La membresía no existe.")
    return membresia


def _obtener_usuario(datos: dict) -> Usuario:
    referencia = datos.get("usuario")
    if isinstance(referencia, int):
        usuario = bd.buscar_usuario_por_num(referencia)
    elif referencia is None:
        usuario = bd.buscar_usuario_por_num(datos.get("num_usuario"))
    else:
        usuario = referencia
    if not isinstance(usuario, Usuario):
        raise ValueError("El usuario no existe.")
    return usuario


def _verificar_membresia(num_membresia: int) -> Membresia:
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if not isinstance(membresia, Membresia):
        raise ValueError("La membresía no existe.")
    return membresia


def _calcular_descuento(configuracion, monto_base: Decimal, fecha: date) -> dict:
    if configuracion is None:
        return {"porcentaje": Decimal("0"), "nominal": Decimal("0.00")}

    if configuracion.monto_minimo is not None:
        monto_minimo = _convertir_importe(configuracion.monto_minimo)
        if monto_base < monto_minimo:
            return {"porcentaje": Decimal("0"), "nominal": Decimal("0.00")}

    if configuracion.dias_aplicables:
        dias = {
            dia.dia_semana if hasattr(dia, "dia_semana") else dia
            for dia in configuracion.dias_aplicables
        }
        if fecha.isoweekday() not in dias:
            return {"porcentaje": Decimal("0"), "nominal": Decimal("0.00")}

    porcentaje = _convertir_porcentaje(configuracion.porcentaje)
    nominal = _cuantificar(monto_base * porcentaje)
    return {"porcentaje": porcentaje, "nominal": nominal}


def _obtener_cashback_aplicado(
    datos: dict,
    configuracion,
    num_membresia: int,
    fecha: date,
    monto_disponible: Decimal,
) -> Decimal:
    cashback = _convertir_importe(datos.get("cashback_aplicado", 0))
    if cashback < 0:
        raise ValueError("El cashback aplicado no puede ser negativo.")
    if cashback == 0:
        return Decimal("0.00")
    if configuracion is None:
        raise ValueError("La membresía no tiene cashback configurado.")
    if cashback > monto_disponible:
        raise ValueError("El cashback aplicado supera el monto de la compra.")

    transacciones = bd.obtener_transacciones_cashback_de_membresia(num_membresia)
    saldo = _obtener_saldo_cashback(transacciones)
    if cashback > saldo:
        raise ValueError("El saldo de cashback es insuficiente.")

    limite = configuracion.limite_min_mensual
    if limite is not None:
        generado = sum(
            (
                transaccion.monto
                for transaccion in transacciones
                if transaccion.fecha.year == fecha.year
                and transaccion.fecha.month == fecha.month
                and transaccion.monto > 0
            ),
            Decimal("0"),
        )
        if generado < _convertir_importe(limite):
            raise ValueError("No se alcanzó el límite mínimo mensual de cashback.")

    return _cuantificar(cashback)


def _registrar_puntos(compra: Compra, configuracion) -> None:
    if configuracion is None:
        return

    porcentaje = _convertir_porcentaje(configuracion.porcentaje)
    movimiento = int(
        (compra.monto_final * porcentaje).to_integral_value(rounding=ROUND_DOWN)
    )
    if movimiento <= 0:
        return

    transacciones = bd.obtener_transacciones_de_miembro(compra.membresia.miembro.num)
    saldo = _obtener_saldo_puntos(transacciones)
    transaccion = TransaccionPuntos(
        num=None,
        movimiento=movimiento,
        saldo=saldo + movimiento,
        fecha=date.today(),
        concepto=None,
        compra=compra,
        version_recompensa=None,
        membresia=compra.membresia,
    )
    bd.guardar_transaccion_puntos(transaccion)


def _registrar_cashback(compra: Compra, configuracion, aplicado: Decimal, fecha: date) -> None:
    if configuracion is None:
        return

    transacciones = bd.obtener_transacciones_cashback_de_membresia(compra.membresia.num)
    saldo = _obtener_saldo_cashback(transacciones)
    if aplicado > 0:
        saldo -= aplicado
        bd.guardar_transaccion_cashback(
            TransaccionCashback(
                num=None,
                monto=-aplicado,
                saldo=saldo,
                fecha=fecha,
                concepto="Cashback aplicado en compra",
                compra=compra,
                membresia=compra.membresia,
            )
        )

    generado = _cuantificar(
        compra.monto_final * _convertir_porcentaje(configuracion.porcentaje)
    )
    if generado > 0:
        saldo += generado
        bd.guardar_transaccion_cashback(
            TransaccionCashback(
                num=None,
                monto=generado,
                saldo=saldo,
                fecha=fecha,
                concepto="Cashback generado por compra",
                compra=compra,
                membresia=compra.membresia,
            )
        )


def _convertir_importe(valor) -> Decimal:
    try:
        return Decimal(str(valor)).quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El importe no es válido.") from None


def _convertir_porcentaje(valor) -> Decimal:
    try:
        porcentaje = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El porcentaje no es válido.") from None
    if porcentaje < 0 or porcentaje > 1:
        raise ValueError("El porcentaje debe estar entre cero y uno.")
    return porcentaje


def _cuantificar(valor: Decimal) -> Decimal:
    return valor.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)


def _obtener_saldo_puntos(transacciones: list[TransaccionPuntos]) -> int:
    if not transacciones:
        return 0
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo


def _obtener_saldo_cashback(transacciones: list[TransaccionCashback]) -> Decimal:
    if not transacciones:
        return Decimal("0.00")
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo
