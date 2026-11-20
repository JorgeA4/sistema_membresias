import calendar
from datetime import date, timedelta
from decimal import Decimal

import base_de_datos.consultas as bd
from clases.membresia import Membresia
from clases.renovacion import Renovacion
from clases.version_plan import TipoAplicacionPlan, VersionPlan
from servicios.autorizacion.servicio_autorizacion import (
    requiere_operador_tienda,
    requiere_administrador_o_propietario,
)
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    OperacionNoPermitida,
    VersionNoVigente,
)


def consultar_membresia(identidad: dict, num: int) -> Membresia | None:
    requiere_operador_tienda(identidad)
    membresia = bd.buscar_membresia_por_num(num)
    if membresia is not None:
        actualizar_estado_membresia(membresia)
    return membresia


def consultar_membresia_de_miembro(identidad: dict, num_miembro: int) -> Membresia | None:
    if not isinstance(identidad, dict):
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")
    if identidad.get("tipo") == "miembro" and identidad.get("num") != num_miembro:
        raise OperacionNoPermitida("No tiene permiso para consultar esta membresía.")
    membresia = bd.buscar_membresia_de_miembro(num_miembro)
    if membresia is not None:
        requiere_administrador_o_propietario(identidad, membresia)
        actualizar_estado_membresia(membresia)
    return membresia


def renovar_membresia(identidad: dict, num_membresia: int, num_version_plan: int) -> Renovacion:
    requiere_operador_tienda(identidad)
    with bd.transaccion():
        membresia = consultar_membresia(identidad, num_membresia)
        if membresia is None:
            raise EntidadNoEncontrada("La membresía no existe.")
        if membresia.estado == Membresia.Estado.CANCELADA:
            raise OperacionNoPermitida("La membresía está cancelada y requiere una nueva contratación.")

        version = bd.buscar_version_plan_por_num(num_version_plan)
        if version is None:
            raise EntidadNoEncontrada("La versión de plan no existe.")
        if not version.esta_vigente():
            raise VersionNoVigente("La versión de plan no está vigente.")
        if version.aplica_en not in (
            TipoAplicacionPlan.RENOVACION,
            TipoAplicacionPlan.AMBAS,
        ):
            raise OperacionNoPermitida("La versión de plan no permite renovaciones.")

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
        if fecha_inicio <= fecha_pago:
            membresia.version_plan_actual = version
            membresia.estado = Membresia.Estado.ACTIVA
        bd.guardar_renovacion(renovacion)
        bd.guardar_membresia(membresia)
        return renovacion


def contratar_membresia(
    identidad: dict,
    num_miembro: int,
    num_version_plan: int,
) -> Renovacion:
    requiere_operador_tienda(identidad)
    with bd.transaccion():
        miembro = bd.buscar_miembro_por_num(num_miembro)
        if miembro is None:
            raise EntidadNoEncontrada("El miembro no existe.")

        version = bd.buscar_version_plan_por_num(num_version_plan)
        if version is None:
            raise EntidadNoEncontrada("La versión de plan no existe.")
        if not version.esta_vigente():
            raise VersionNoVigente("La versión de plan no está vigente.")
        if version.aplica_en not in (TipoAplicacionPlan.CONTRATACION, TipoAplicacionPlan.AMBAS):
            raise OperacionNoPermitida("La versión de plan no permite contrataciones.")
        existente = bd.buscar_membresia_de_miembro(num_miembro)
        if existente is not None:
            actualizar_estado_membresia(existente)
            if existente.estado != Membresia.Estado.CANCELADA:
                raise OperacionNoPermitida("El miembro ya tiene una membresía no cancelada.")

        membresia = Membresia(
            num=None,
            fecha_contratacion=date.today(),
            estado=Membresia.Estado.ACTIVA,
            miembro=miembro,
            version_plan_actual=version,
        )
        bd.guardar_membresia(membresia)
        renovacion = Renovacion(
            num=None,
            fecha_pago=date.today(),
            monto_pagado=Decimal(str(version.precio)),
            fecha_inicio_periodo=date.today(),
            fecha_fin_periodo=_sumar_meses(date.today(), version.plazo_meses) - timedelta(days=1),
            membresia=membresia,
            version_plan_comprado=version,
        )
        bd.guardar_renovacion(renovacion)
        return renovacion


def cancelar_membresia(identidad: dict, num_membresia: int) -> Membresia:
    from servicios.autorizacion.servicio_autorizacion import requiere_administrador

    requiere_administrador(identidad)
    membresia = consultar_membresia(identidad, num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    if membresia.estado == Membresia.Estado.CANCELADA:
        raise OperacionNoPermitida("La membresía ya está cancelada.")

    membresia.estado = Membresia.Estado.CANCELADA
    bd.guardar_membresia(membresia)
    return membresia


def suspender_membresia(identidad: dict, num_membresia: int) -> Membresia:
    from servicios.autorizacion.servicio_autorizacion import requiere_administrador

    requiere_administrador(identidad)
    membresia = consultar_membresia(identidad, num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    if membresia.estado == Membresia.Estado.CANCELADA:
        raise OperacionNoPermitida("La membresía está cancelada.")
    membresia.estado = Membresia.Estado.SUSPENDIDA
    bd.guardar_membresia(membresia)
    return membresia


def actualizar_estado_membresia(membresia: Membresia, fecha: date | None = None) -> Membresia:
    fecha = fecha or date.today()
    if membresia.estado == Membresia.Estado.CANCELADA:
        return membresia

    periodo = _obtener_periodo_actual(membresia, fecha)
    if periodo is None:
        return membresia

    fecha_inicio, fecha_final, version = periodo
    if fecha <= fecha_final:
        cambio = False
        if membresia.estado == Membresia.Estado.SUSPENDIDA:
            membresia.estado = Membresia.Estado.ACTIVA
            cambio = True
        if fecha >= fecha_inicio:
            version_actual = membresia.version_plan_actual
            if version_actual is None or version_actual.num != version.num:
                membresia.version_plan_actual = version
                cambio = True
        if cambio:
            bd.guardar_membresia(membresia)
        return membresia

    if fecha <= _sumar_meses(fecha_final + timedelta(days=1), 1) - timedelta(days=1):
        membresia.estado = Membresia.Estado.SUSPENDIDA
    else:
        membresia.estado = Membresia.Estado.CANCELADA
    bd.guardar_membresia(membresia)
    return membresia


def _obtener_inicio_renovacion(membresia: Membresia, fecha_pago: date) -> date:
    renovaciones = bd.obtener_renovaciones_de_membresia(membresia.num)
    if renovaciones:
        ultima = max(
            renovaciones,
            key=lambda renovacion: (renovacion.fecha_fin_periodo, renovacion.num),
        )
        if ultima.fecha_fin_periodo >= fecha_pago:
            return ultima.fecha_fin_periodo + timedelta(days=1)
        return fecha_pago

    periodo_actual = _obtener_periodo_actual(membresia, fecha_pago)
    if periodo_actual is not None and periodo_actual[1] >= fecha_pago:
        return periodo_actual[1] + timedelta(days=1)
    return fecha_pago


def _obtener_periodo_actual(membresia: Membresia, fecha: date):
    periodos = [
        (
            renovacion.fecha_inicio_periodo,
            renovacion.fecha_fin_periodo,
            renovacion.version_plan_comprado,
        )
        for renovacion in bd.obtener_renovaciones_de_membresia(membresia.num)
        if renovacion.fecha_inicio_periodo <= fecha
    ]
    if periodos:
        return max(periodos, key=lambda periodo: periodo[1])
    if membresia.version_plan_actual is None:
        return None
    inicio = membresia.fecha_contratacion
    final = _sumar_meses(inicio, membresia.version_plan_actual.plazo_meses) - timedelta(days=1)
    return inicio, final, membresia.version_plan_actual


def _sumar_meses(fecha: date, meses: int) -> date:
    indice_mes = fecha.year * 12 + fecha.month - 1 + meses
    año, mes_indice = divmod(indice_mes, 12)
    mes = mes_indice + 1
    dia = min(fecha.day, calendar.monthrange(año, mes)[1])
    return date(año, mes, dia)
