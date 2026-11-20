import calendar
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

import base_de_datos.consultas as bd
from clases.compra import Compra
from clases.membresia import Membresia
from clases.transaccion_cashback import TransaccionCashback
from clases.transaccion_puntos import TransaccionPuntos
from servicios.autorizacion.servicio_autorizacion import (
    requiere_administrador_o_propietario,
    requiere_operador_compra,
)
from servicios.membresia.servicio_membresia import actualizar_estado_membresia
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    LimiteExcedido,
    OperacionNoPermitida,
    SaldoInsuficiente,
)


_DOS_DECIMALES = Decimal("0.01")


def registrar_compra(identidad: dict, datos: dict) -> Compra:
    usuario = requiere_operador_compra(identidad)
    with bd.transaccion():
        membresia = _obtener_membresia(datos)
        actualizar_estado_membresia(membresia)
        actualizar_vigencia_puntos(membresia)
        version = membresia.version_plan_actual

        if membresia.estado != Membresia.Estado.ACTIVA:
            raise OperacionNoPermitida("La membresía no está activa.")
        if version is None:
            raise OperacionNoPermitida("La membresía no tiene una versión de plan activa.")

        monto_base = _convertir_importe(datos["monto_base"])
        if monto_base <= 0:
            raise DatosInvalidos("El monto base debe ser mayor que cero.")

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


def obtener_compras_de_membresia(identidad: dict, num_membresia: int) -> list[Compra]:
    membresia = _verificar_membresia(num_membresia)
    requiere_administrador_o_propietario(identidad, membresia)
    return bd.obtener_compras_de_membresia(num_membresia)


def obtener_transacciones_de_miembro(identidad: dict, num_miembro: int) -> list[TransaccionPuntos]:
    if bd.buscar_miembro_por_num(num_miembro) is None:
        raise EntidadNoEncontrada("El miembro no existe.")
    membresia = bd.buscar_membresia_de_miembro(num_miembro)
    if membresia is None:
        raise EntidadNoEncontrada("El miembro no tiene una membresía.")
    requiere_administrador_o_propietario(identidad, membresia)
    actualizar_vigencia_puntos(membresia)
    return sorted(
        bd.obtener_transacciones_de_miembro(num_miembro),
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    )


def obtener_saldo_de_miembro(identidad: dict, num_miembro: int) -> int:
    transacciones = obtener_transacciones_de_miembro(identidad, num_miembro)
    if not transacciones:
        return 0
    return transacciones[-1].saldo


def obtener_fecha_vencimiento_puntos(identidad: dict, num_miembro: int):
    if bd.buscar_miembro_por_num(num_miembro) is None:
        raise EntidadNoEncontrada("El miembro no existe.")
    membresia = bd.buscar_membresia_de_miembro(num_miembro)
    if membresia is None:
        raise EntidadNoEncontrada("El miembro no tiene una membresía.")
    requiere_administrador_o_propietario(identidad, membresia)
    actualizar_vigencia_puntos(membresia)
    return _calcular_fecha_vencimiento_puntos(membresia)


def actualizar_vigencia_puntos(membresia: Membresia, fecha: date | None = None) -> None:
    """Vence el saldo global después de la fecha calculada para la última compra."""
    fecha = fecha or date.today()
    fecha_vencimiento = _calcular_fecha_vencimiento_puntos(membresia)
    if fecha_vencimiento is None or fecha <= fecha_vencimiento:
        return

    transacciones = bd.obtener_transacciones_de_miembro(membresia.miembro.num)
    ultima_compra = _obtener_ultima_compra_con_puntos(transacciones)
    if ultima_compra is None:
        return
    clave_ultima_compra = (ultima_compra.fecha, ultima_compra.num)
    if any(
        transaccion.concepto == "Puntos vencidos"
        and (transaccion.fecha, transaccion.num) > clave_ultima_compra
        for transaccion in transacciones
    ):
        return

    saldo = _obtener_saldo_puntos(transacciones)
    if saldo <= 0:
        return
    bd.guardar_transaccion_puntos(
        TransaccionPuntos(
            num=None,
            movimiento=-saldo,
            saldo=0,
            fecha=fecha,
            concepto="Puntos vencidos",
            compra=None,
            version_recompensa=None,
            membresia=membresia,
        )
    )


def _calcular_fecha_vencimiento_puntos(membresia: Membresia):
    version = membresia.version_plan_actual
    configuracion = None if version is None else version.config_puntos
    if configuracion is None or configuracion.vigencia_meses is None:
        return None
    transacciones = bd.obtener_transacciones_de_miembro(membresia.miembro.num)
    ultima_compra = _obtener_ultima_compra_con_puntos(transacciones)
    if ultima_compra is None:
        return None
    return _sumar_meses(ultima_compra.fecha, configuracion.vigencia_meses)


def _obtener_ultima_compra_con_puntos(transacciones):
    compras = [
        transaccion
        for transaccion in transacciones
        if transaccion.movimiento > 0 and transaccion.compra is not None
    ]
    if not compras:
        return None
    return max(compras, key=lambda transaccion: (transaccion.fecha, transaccion.num))


def _sumar_meses(fecha: date, meses: int) -> date:
    indice_mes = fecha.year * 12 + fecha.month - 1 + meses
    año, mes_indice = divmod(indice_mes, 12)
    mes = mes_indice + 1
    dia = min(fecha.day, calendar.monthrange(año, mes)[1])
    return date(año, mes, dia)


def obtener_transacciones_cashback_de_membresia(
    identidad: dict,
    num_membresia: int,
) -> list[TransaccionCashback]:
    membresia = _verificar_membresia(num_membresia)
    requiere_administrador_o_propietario(identidad, membresia)
    return sorted(
        bd.obtener_transacciones_cashback_de_membresia(num_membresia),
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    )


def obtener_saldo_cashback_de_membresia(identidad: dict, num_membresia: int) -> Decimal:
    transacciones = obtener_transacciones_cashback_de_membresia(identidad, num_membresia)
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
        raise EntidadNoEncontrada("La membresía no existe.")
    return membresia


def _verificar_membresia(num_membresia: int) -> Membresia:
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if not isinstance(membresia, Membresia):
        raise EntidadNoEncontrada("La membresía no existe.")
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
        raise DatosInvalidos("El cashback aplicado no puede ser negativo.")
    if cashback == 0:
        return Decimal("0.00")
    if configuracion is None:
        raise OperacionNoPermitida("La membresía no tiene cashback configurado.")
    if cashback > monto_disponible:
        raise LimiteExcedido("El cashback aplicado supera el monto de la compra.")

    transacciones = bd.obtener_transacciones_cashback_de_membresia(num_membresia)
    _registrar_expiraciones_cashback(transacciones, configuracion, num_membresia, fecha)
    transacciones = bd.obtener_transacciones_cashback_de_membresia(num_membresia)
    saldo = _obtener_cashback_disponible(transacciones, configuracion, fecha)
    if cashback > saldo:
        raise SaldoInsuficiente("El saldo de cashback es insuficiente.")

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
        raise DatosInvalidos("El importe no es válido.") from None


def _convertir_porcentaje(valor) -> Decimal:
    try:
        porcentaje = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise DatosInvalidos("El porcentaje no es válido.") from None
    if porcentaje < 0 or porcentaje > 1:
        raise DatosInvalidos("El porcentaje debe estar entre cero y uno.")
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


def _registrar_expiraciones_cashback(
    transacciones: list[TransaccionCashback],
    configuracion,
    num_membresia: int,
    fecha: date,
) -> None:
    limite = configuracion.limite_min_mensual
    if limite is None:
        return

    limite = _convertir_importe(limite)
    meses_expirados = {
        (transaccion.fecha.year, transaccion.fecha.month)
        for transaccion in transacciones
        if transaccion.monto < 0
        and transaccion.concepto
        and transaccion.concepto.startswith("Expiración de cashback")
    }
    meses = {
        (transaccion.fecha.year, transaccion.fecha.month)
        for transaccion in transacciones
        if transaccion.monto > 0
        and (transaccion.fecha.year, transaccion.fecha.month) != (fecha.year, fecha.month)
    }
    for año, mes in meses:
        if (año, mes) in meses_expirados:
            continue
        generado = sum(
            (
                transaccion.monto
                for transaccion in transacciones
                if transaccion.monto > 0
                and transaccion.fecha.year == año
                and transaccion.fecha.month == mes
            ),
            Decimal("0"),
        )
        if generado <= limite:
            saldo = _obtener_saldo_cashback(transacciones) - generado
            bd.guardar_transaccion_cashback(
                TransaccionCashback(
                    num=None,
                    monto=-generado,
                    saldo=max(saldo, Decimal("0.00")),
                    fecha=date(año, mes, calendar.monthrange(año, mes)[1]),
                    concepto=f"Expiración de cashback {año:04d}-{mes:02d}",
                    compra=None,
                    membresia=bd.buscar_membresia_por_num(num_membresia),
                )
            )


def _obtener_cashback_disponible(
    transacciones: list[TransaccionCashback],
    configuracion,
    fecha: date,
) -> Decimal:
    limite = configuracion.limite_min_mensual
    positivos = [transaccion for transaccion in transacciones if transaccion.monto > 0]
    disponibles = Decimal("0.00")
    meses = {(t.fecha.year, t.fecha.month) for t in positivos}
    limite_decimal = None if limite is None else _convertir_importe(limite)
    for año, mes in meses:
        generado = sum(
            (
                t.monto for t in positivos
                if t.fecha.year == año and t.fecha.month == mes
            ),
            Decimal("0"),
        )
        if limite_decimal is None or generado > limite_decimal:
            disponibles += generado

    disponibles += sum(
        (
            t.monto for t in transacciones
            if t.monto < 0
            and not (t.concepto and t.concepto.startswith("Expiración de cashback"))
        ),
        Decimal("0"),
    )
    return max(disponibles, Decimal("0.00"))
