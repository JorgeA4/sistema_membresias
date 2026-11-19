from datetime import date
from decimal import Decimal, InvalidOperation

import base_de_datos.consultas as bd
from clases.plan import Plan
from clases.version_plan import TipoAplicacionPlan, VersionPlan


def registrar_plan(datos: dict) -> Plan:
    codigo = datos["codigo"].strip()
    nombre = datos["nombre"].strip()

    if not codigo or not nombre:
        raise ValueError("El código y el nombre del plan son obligatorios.")
    if bd.buscar_plan_por_codigo(codigo) is not None:
        raise ValueError("El código del plan ya existe.")
    if any(plan.nombre == nombre for plan in bd.obtener_todos_los_planes()):
        raise ValueError("El nombre del plan ya existe.")

    plan = Plan(codigo, nombre, datos.get("descripcion"))
    bd.guardar_plan(plan)
    return plan


def consultar_plan(codigo: str) -> Plan | None:
    return bd.buscar_plan_por_codigo(codigo)


def obtener_planes() -> list[Plan]:
    return bd.obtener_todos_los_planes()


def modificar_plan(codigo: str, datos: dict) -> Plan:
    plan = consultar_plan(codigo)
    if plan is None:
        raise ValueError("El plan no existe.")

    atributos_permitidos = {"nombre", "descripcion"}
    atributos_invalidos = set(datos) - atributos_permitidos
    if atributos_invalidos:
        raise ValueError("Los datos contienen atributos no modificables.")

    if "nombre" in datos:
        nombre = datos["nombre"].strip()
        if not nombre:
            raise ValueError("El nombre del plan es obligatorio.")
        if any(
            otro.nombre == nombre and otro.codigo != codigo
            for otro in bd.obtener_todos_los_planes()
        ):
            raise ValueError("El nombre del plan ya existe.")
        plan.nombre = nombre

    if "descripcion" in datos:
        plan.descripcion = datos["descripcion"]

    bd.guardar_plan(plan)
    return plan


def eliminar_plan(codigo: str) -> None:
    plan = consultar_plan(codigo)
    if plan is None:
        raise ValueError("El plan no existe.")
    if bd.obtener_versiones_de_plan(codigo):
        raise ValueError("No se puede eliminar un plan con versiones registradas.")
    bd.eliminar_plan(codigo)


def crear_version_plan(datos: dict) -> VersionPlan:
    plan = _obtener_plan(datos)
    fecha_inicio = datos["fecha_inicio"]
    fecha_final = datos["fecha_final"]
    precio = _convertir_precio(datos["precio"])
    plazo_meses = datos["plazo_meses"]

    if not isinstance(fecha_inicio, date) or not isinstance(fecha_final, date):
        raise ValueError("Las fechas de la versión deben ser fechas válidas.")
    if fecha_final < fecha_inicio:
        raise ValueError("La fecha final no puede ser anterior a la inicial.")
    if precio <= 0:
        raise ValueError("El precio debe ser mayor que cero.")
    if isinstance(plazo_meses, bool) or not isinstance(plazo_meses, int) or plazo_meses <= 0:
        raise ValueError("El plazo debe ser un número entero mayor que cero.")

    version_base = _obtener_version_base(datos)
    if version_base is not None and version_base.plan.codigo != plan.codigo:
        raise ValueError("La versión base debe pertenecer al mismo plan.")

    try:
        aplica_en = TipoAplicacionPlan(datos["aplica_en"])
    except (KeyError, ValueError):
        raise ValueError("La aplicación de la versión no es válida.") from None

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


def obtener_versiones_de_plan(codigo_plan: str) -> list[VersionPlan]:
    if consultar_plan(codigo_plan) is None:
        raise ValueError("El plan no existe.")
    return bd.obtener_versiones_de_plan(codigo_plan)


def finalizar_version_plan(num: int, fecha_final: date) -> VersionPlan:
    version = bd.buscar_version_plan_por_num(num)
    if version is None:
        raise ValueError("La versión de plan no existe.")
    if not isinstance(fecha_final, date):
        raise ValueError("La fecha final no es válida.")

    version.finalizar_vigencia(fecha_final)
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
        raise ValueError("El plan no existe.")
    return plan


def _obtener_version_base(datos: dict) -> VersionPlan | None:
    referencia = datos.get("version_base_de_promo")
    if isinstance(referencia, int):
        version_base = bd.buscar_version_plan_por_num(referencia)
        if version_base is None:
            raise ValueError("La versión base de promoción no existe.")
    else:
        version_base = referencia

    if version_base is not None and not isinstance(version_base, VersionPlan):
        raise ValueError("La versión base de promoción no es válida.")
    return version_base


def _convertir_precio(valor) -> Decimal:
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El precio no es válido.") from None
