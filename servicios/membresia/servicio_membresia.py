import calendar
from datetime import date, timedelta
from decimal import Decimal

import base_de_datos.consultas as bd
from clases.membresia import Membresia
from clases.renovacion import Renovacion
from clases.version_plan import TipoAplicacionPlan, VersionPlan


def consultar_membresia(num: int) -> Membresia | None:
    return bd.buscar_membresia_por_num(num)


def consultar_membresia_de_miembro(num_miembro: int) -> Membresia | None:
    return bd.buscar_membresia_de_miembro(num_miembro)


def renovar_membresia(num_membresia: int, num_version_plan: int) -> Renovacion:
    membresia = consultar_membresia(num_membresia)
    if membresia is None:
        raise ValueError("La membresía no existe.")
    if membresia.estado != Membresia.Estado.ACTIVA:
        raise ValueError("La membresía no está activa.")

    version = bd.buscar_version_plan_por_num(num_version_plan)
    if version is None:
        raise ValueError("La versión de plan no existe.")
    if not version.esta_vigente():
        raise ValueError("La versión de plan no está vigente.")
    if version.aplica_en not in (
        TipoAplicacionPlan.RENOVACION,
        TipoAplicacionPlan.AMBAS,
    ):
        raise ValueError("La versión de plan no permite renovaciones.")

    fecha_pago = date.today()
    fecha_inicio = _obtener_inicio_renovacion(membresia, fecha_pago)
    fecha_fin = _sumar_meses(fecha_inicio, version.plazo_meses) - timedelta(days=1)
    monto_pagado = Decimal(str(version.precio))

    renovacion = Renovacion(
        num=None,
        fecha_pago=fecha_pago,
        monto_pagado=monto_pagado,
        fecha_inicio_periodo=fecha_inicio,
        fecha_fin_periodo=fecha_fin,
        membresia=membresia,
        version_plan_comprado=version,
    )
    membresia.version_plan_actual = version
    bd.guardar_renovacion(renovacion)
    bd.guardar_membresia(membresia)
    return renovacion


def cancelar_membresia(num_membresia: int) -> Membresia:
    membresia = consultar_membresia(num_membresia)
    if membresia is None:
        raise ValueError("La membresía no existe.")
    if membresia.estado == Membresia.Estado.CANCELADA:
        raise ValueError("La membresía ya está cancelada.")

    membresia.estado = Membresia.Estado.CANCELADA
    bd.guardar_membresia(membresia)
    return membresia


def _obtener_inicio_renovacion(membresia: Membresia, fecha_pago: date) -> date:
    renovaciones = bd.obtener_renovaciones_de_membresia(membresia.num)
    if not renovaciones:
        return max(membresia.fecha_contratacion, fecha_pago)

    ultima = max(
        renovaciones,
        key=lambda renovacion: (renovacion.fecha_fin_periodo, renovacion.num),
    )
    if ultima.fecha_fin_periodo >= fecha_pago:
        return ultima.fecha_fin_periodo + timedelta(days=1)
    return fecha_pago


def _sumar_meses(fecha: date, meses: int) -> date:
    indice_mes = fecha.year * 12 + fecha.month - 1 + meses
    año, mes_indice = divmod(indice_mes, 12)
    mes = mes_indice + 1
    dia = min(fecha.day, calendar.monthrange(año, mes)[1])
    return date(año, mes, dia)
