from datetime import date
from decimal import Decimal, InvalidOperation

import base_de_datos.consultas as bd
from clases.plan import Plan
from clases.version_plan import TipoAplicacionPlan, VersionPlan
from servicios.autorizacion.servicio_autorizacion import (
    requiere_administrador,
    requiere_administrador_o_gerente,
    requiere_operador_tienda,
)
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    OperacionNoPermitida,
    VersionNoVigente,
)


def registrar_plan(identidad: dict, datos: dict) -> Plan:
    requiere_administrador(identidad)
    codigo = datos["codigo"].strip()
    nombre = datos["nombre"].strip()

    if not codigo or not nombre:
        raise DatosInvalidos("El código y el nombre del plan son obligatorios.")
    if bd.buscar_plan_por_codigo(codigo) is not None:
        raise DatosInvalidos("El código del plan ya existe.")
    if any(plan.nombre == nombre for plan in bd.obtener_todos_los_planes()):
        raise DatosInvalidos("El nombre del plan ya existe.")

    plan = Plan(codigo, nombre, datos.get("descripcion"))
    bd.guardar_plan(plan)
    return plan


def consultar_plan(codigo: str) -> Plan | None:
    return bd.buscar_plan_por_codigo(codigo)


def obtener_planes(identidad: dict) -> list[Plan]:
    requiere_administrador_o_gerente(identidad)
    return bd.obtener_todos_los_planes()


def modificar_plan(identidad: dict, codigo: str, datos: dict) -> Plan:
    requiere_administrador(identidad)
    plan = consultar_plan(codigo)
    if plan is None:
        raise EntidadNoEncontrada("El plan no existe.")

    atributos_permitidos = {"nombre", "descripcion"}
    atributos_invalidos = set(datos) - atributos_permitidos
    if atributos_invalidos:
        raise DatosInvalidos("Los datos contienen atributos no modificables.")

    if "nombre" in datos:
        nombre = datos["nombre"].strip()
        if not nombre:
            raise DatosInvalidos("El nombre del plan es obligatorio.")
        if any(
            otro.nombre == nombre and otro.codigo != codigo
            for otro in bd.obtener_todos_los_planes()
        ):
            raise DatosInvalidos("El nombre del plan ya existe.")
        plan.nombre = nombre

    if "descripcion" in datos:
        plan.descripcion = datos["descripcion"]

    bd.guardar_plan(plan)
    return plan


def eliminar_plan(identidad: dict, codigo: str) -> None:
    requiere_administrador(identidad)
    plan = consultar_plan(codigo)
    if plan is None:
        raise EntidadNoEncontrada("El plan no existe.")
    if bd.obtener_versiones_de_plan(codigo):
        raise OperacionNoPermitida("No se puede eliminar un plan con versiones registradas.")
    bd.eliminar_plan(codigo)


def crear_version_plan(identidad: dict, datos: dict) -> VersionPlan:
    requiere_administrador(identidad)
    plan = _obtener_plan(datos)
    fecha_inicio = datos["fecha_inicio"]
    fecha_final = datos["fecha_final"]
    precio = _convertir_precio(datos["precio"])
    plazo_meses = datos["plazo_meses"]

    if not isinstance(fecha_inicio, date) or not isinstance(fecha_final, date):
        raise DatosInvalidos("Las fechas de la versión deben ser fechas válidas.")
    if fecha_final < fecha_inicio:
        raise DatosInvalidos("La fecha final no puede ser anterior a la inicial.")
    if precio <= 0:
        raise DatosInvalidos("El precio debe ser mayor que cero.")
    if isinstance(plazo_meses, bool) or not isinstance(plazo_meses, int) or plazo_meses <= 0:
        raise DatosInvalidos("El plazo debe ser un número entero mayor que cero.")

    version_base = _obtener_version_base(datos)
    if version_base is not None and version_base.plan.codigo != plan.codigo:
        raise DatosInvalidos("La versión base debe pertenecer al mismo plan.")

    _validar_configuracion_puntos(datos.get("config_puntos"))
    _validar_configuracion_descuento(datos.get("config_descuento"))
    _validar_configuracion_cashback(datos.get("config_cashback"))

    try:
        aplica_en = TipoAplicacionPlan(datos["aplica_en"])
    except (KeyError, ValueError):
        raise DatosInvalidos("La aplicación de la versión no es válida.") from None

    version = VersionPlan(
        num=datos.get("num"),
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        precio=precio,
        plazo_meses=plazo_meses,
        aplica_en=aplica_en,
        plan=plan,
        config_cashback=datos.get("config_cashback"),
        config_puntos=datos.get("config_puntos"),
        config_descuento=datos.get("config_descuento"),
        version_base_de_promo=version_base,
    )
    bd.guardar_version_plan(version)
    return version


def consultar_version_plan(num: int) -> VersionPlan | None:
    return bd.buscar_version_plan_por_num(num)


def obtener_versiones_de_plan(codigo_plan: str) -> list[VersionPlan]:
    if consultar_plan(codigo_plan) is None:
        raise EntidadNoEncontrada("El plan no existe.")
    return bd.obtener_versiones_de_plan(codigo_plan)


def obtener_versiones_plan_para_operacion(
    identidad: dict,
    aplica_en: str | None = None,
) -> list[VersionPlan]:
    """Obtiene versiones seleccionables para una operación administrativa."""
    if aplica_en is None:
        requiere_administrador(identidad)
    else:
        requiere_operador_tienda(identidad)
        try:
            tipo_aplicacion = TipoAplicacionPlan(aplica_en)
        except ValueError:
            raise DatosInvalidos("El tipo de operación de la versión no es válido.") from None

    versiones = []
    for plan in bd.obtener_todos_los_planes():
        for version in bd.obtener_versiones_de_plan(plan.codigo):
            if aplica_en is not None and version.aplica_en not in (
                tipo_aplicacion,
                TipoAplicacionPlan.AMBAS,
            ):
                continue
            if aplica_en is not None and not version.esta_vigente():
                continue
            versiones.append(version)
    return sorted(versiones, key=lambda version: (version.plan.codigo, version.num))


def finalizar_version_plan(identidad: dict, num: int, fecha_final: date) -> VersionPlan:
    requiere_administrador(identidad)
    version = consultar_version_plan(num)
    if version is None:
        raise EntidadNoEncontrada("La versión de plan no existe.")
    if not isinstance(fecha_final, date):
        raise DatosInvalidos("La fecha final no es válida.")

    version.finalizar_vigencia(fecha_final)
    bd.guardar_version_plan(version)
    return version


def _obtener_plan(datos: dict) -> Plan:
    referencia = datos.get("plan")
    if isinstance(referencia, str):
        plan = bd.buscar_plan_por_codigo(referencia)
    elif referencia is None:
        plan = bd.buscar_plan_por_codigo(datos.get("codigo_plan"))
    else:
        plan = referencia

    if not isinstance(plan, Plan):
        raise EntidadNoEncontrada("El plan no existe.")
    return plan


def _obtener_version_base(datos: dict) -> VersionPlan | None:
    referencia = datos.get("version_base_de_promo")
    if isinstance(referencia, int):
        version_base = bd.buscar_version_plan_por_num(referencia)
        if version_base is None:
            raise EntidadNoEncontrada("La versión base de promoción no existe.")
    else:
        version_base = referencia

    if version_base is not None and not isinstance(version_base, VersionPlan):
        raise DatosInvalidos("La versión base de promoción no es válida.")
    return version_base


def _convertir_precio(valor) -> Decimal:
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise DatosInvalidos("El precio no es válido.") from None


def _validar_configuracion_puntos(configuracion) -> None:
    if configuracion is None:
        return
    porcentaje = _convertir_porcentaje(configuracion.porcentaje)
    if porcentaje == 0:
        raise DatosInvalidos("El porcentaje de puntos debe ser mayor que cero.")
    vigencia = configuracion.vigencia_meses
    if vigencia is not None and (
        isinstance(vigencia, bool) or not isinstance(vigencia, int) or vigencia <= 0
    ):
            raise DatosInvalidos("La vigencia de puntos debe ser un entero mayor que cero.")


def _validar_configuracion_descuento(configuracion) -> None:
    if configuracion is None:
        return
    porcentaje = _convertir_porcentaje(configuracion.porcentaje)
    if porcentaje == 0:
        raise DatosInvalidos("El porcentaje de descuento debe ser mayor que cero.")
    if configuracion.monto_minimo is not None:
        _convertir_monto_no_negativo(configuracion.monto_minimo, "El monto mínimo del descuento")
    for dia in configuracion.dias_aplicables:
        if isinstance(dia, bool) or not isinstance(dia, int) or not 1 <= dia <= 7:
            raise DatosInvalidos("Los días aplicables deben estar entre 1 y 7.")


def _validar_configuracion_cashback(configuracion) -> None:
    if configuracion is None:
        return
    porcentaje = _convertir_porcentaje(configuracion.porcentaje)
    if porcentaje == 0:
        raise DatosInvalidos("El porcentaje de cashback debe ser mayor que cero.")
    if configuracion.limite_min_mensual is not None:
        _convertir_monto_no_negativo(
            configuracion.limite_min_mensual,
            "El umbral mensual de cashback",
        )


def _convertir_porcentaje(valor) -> Decimal:
    try:
        porcentaje = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise DatosInvalidos("El porcentaje no es válido.") from None
    if porcentaje < 0 or porcentaje > 1:
        raise DatosInvalidos("El porcentaje debe estar entre cero y uno.")
    return porcentaje


def _convertir_monto_no_negativo(valor, nombre: str) -> Decimal:
    try:
        monto = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise DatosInvalidos(f"{nombre} no es válido.") from None
    if monto < 0:
        raise DatosInvalidos(f"{nombre} no puede ser negativo.")
    return monto
