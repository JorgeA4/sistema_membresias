from datetime import date, datetime, timedelta

import base_de_datos.consultas as bd
from clases.membresia import Membresia
from clases.recompensa import Recompensa
from clases.transaccion_puntos import TransaccionPuntos
from clases.version_recompensa import VersionRecompensa
from servicios.autorizacion.servicio_autorizacion import (
    requiere_administrador,
    requiere_administrador_o_gerente,
    requiere_administrador_o_propietario,
    requiere_operador_tienda,
)
from servicios.compra.servicio_compra import actualizar_vigencia_puntos
from servicios.membresia.servicio_membresia import actualizar_estado_membresia
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    LimiteExcedido,
    OperacionNoPermitida,
    SaldoInsuficiente,
    VersionNoVigente,
)


def registrar_recompensa(identidad: dict, datos: dict) -> Recompensa:
    requiere_administrador(identidad)
    codigo = datos["codigo"].strip()
    nombre = datos["nombre"].strip()

    if not codigo or not nombre:
        raise DatosInvalidos("El código y el nombre de la recompensa son obligatorios.")
    if bd.buscar_recompensa_por_codigo(codigo) is not None:
        raise DatosInvalidos("El código de la recompensa ya existe.")

    recompensa = Recompensa(codigo, nombre, datos.get("descripcion"))
    bd.guardar_recompensa(recompensa)
    return recompensa


def registrar_recompensa_con_condiciones(
    identidad: dict, datos_recompensa: dict, datos_condiciones: dict
) -> Recompensa:
    requiere_administrador(identidad)
    with bd.transaccion():
        recompensa = registrar_recompensa(identidad, datos_recompensa)
        condiciones = dict(datos_condiciones)
        condiciones["recompensa"] = recompensa
        crear_version_recompensa(identidad, condiciones)
        return recompensa


def consultar_recompensa(codigo: str) -> Recompensa | None:
    return bd.buscar_recompensa_por_codigo(codigo)


def obtener_recompensas(identidad: dict) -> list[Recompensa]:
    requiere_administrador_o_gerente(identidad)
    return bd.obtener_todas_las_recompensas()


def modificar_recompensa(identidad: dict, codigo: str, datos: dict) -> Recompensa:
    requiere_administrador(identidad)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise EntidadNoEncontrada("La recompensa no existe.")

    atributos_permitidos = {"nombre", "descripcion"}
    atributos_invalidos = set(datos) - atributos_permitidos
    if atributos_invalidos:
        raise DatosInvalidos("Los datos contienen atributos no modificables.")

    if "nombre" in datos:
        nombre = datos["nombre"].strip()
        if not nombre:
            raise DatosInvalidos("El nombre de la recompensa es obligatorio.")
        recompensa.nombre = nombre

    if "descripcion" in datos:
        recompensa.descripcion = datos["descripcion"]

    bd.guardar_recompensa(recompensa)
    return recompensa


def eliminar_recompensa(identidad: dict, codigo: str) -> None:
    requiere_administrador(identidad)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise EntidadNoEncontrada("La recompensa no existe.")
    if bd.obtener_versiones_de_recompensa(codigo):
        raise OperacionNoPermitida("No se puede eliminar una recompensa con versiones registradas.")
    bd.eliminar_recompensa(codigo)


def crear_version_recompensa(identidad: dict, datos: dict) -> VersionRecompensa:
    requiere_administrador(identidad)
    recompensa = _obtener_recompensa(datos)
    fecha_inicio = datos["fecha_inicio"]
    fecha_final = datos["fecha_final"]
    costo_puntos = datos["costo_puntos"]
    limite_canjes = datos.get("limite_canjes")

    if not isinstance(fecha_inicio, date) or not isinstance(fecha_final, date):
        raise DatosInvalidos("Las fechas de la versión deben ser fechas válidas.")
    if fecha_final < fecha_inicio:
        raise DatosInvalidos("La fecha final no puede ser anterior a la inicial.")
    if any(
        version.fecha_inicio <= fecha_final
        and fecha_inicio <= version.fecha_final
        for version in bd.obtener_versiones_de_recompensa(recompensa.codigo)
    ):
        raise OperacionNoPermitida("Ya existe una versión vigente en ese período.")
    if isinstance(costo_puntos, bool) or not isinstance(costo_puntos, int) or costo_puntos <= 0:
        raise DatosInvalidos("El costo debe ser un entero mayor que cero.")
    if (
        limite_canjes is not None
        and (
            isinstance(limite_canjes, bool)
            or not isinstance(limite_canjes, int)
            or limite_canjes <= 0
        )
    ):
        raise DatosInvalidos("El límite de canjes debe ser un entero mayor que cero.")

    version = VersionRecompensa(
        num=datos.get("num"),
        costo_puntos=costo_puntos,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        limite_canjes=limite_canjes,
        recompensa=recompensa,
    )
    bd.guardar_version_recompensa(version)
    return version


def modificar_recompensa_con_condiciones(
    identidad: dict,
    codigo: str,
    datos_recompensa: dict,
    datos_condiciones: dict,
) -> tuple[Recompensa, VersionRecompensa]:
    requiere_administrador(identidad)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise EntidadNoEncontrada("La recompensa no existe.")
    versiones = obtener_versiones_de_recompensa(codigo)
    actual = _seleccionar_condicion_vigente(versiones)
    fecha_inicio = datos_condiciones["fecha_inicio"]
    if actual is not None and fecha_inicio <= actual.fecha_inicio:
        raise DatosInvalidos("La nueva fecha inicial debe ser posterior a la condición actual.")
    with bd.transaccion():
        recompensa = modificar_recompensa(identidad, codigo, datos_recompensa)
        if actual is not None and fecha_inicio - timedelta(days=1) < actual.fecha_final:
            actual.finalizar_vigencia(fecha_inicio - timedelta(days=1))
            bd.guardar_version_recompensa(actual)
        condiciones = dict(datos_condiciones)
        condiciones["recompensa"] = codigo
        return recompensa, crear_version_recompensa(identidad, condiciones)


def reactivar_recompensa(
    identidad: dict, codigo: str, datos_condiciones: dict
) -> VersionRecompensa:
    requiere_administrador(identidad)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise EntidadNoEncontrada("La recompensa no existe.")
    if any(version.esta_vigente() for version in obtener_versiones_de_recompensa(codigo)):
        raise OperacionNoPermitida("La recompensa ya tiene condiciones vigentes.")
    if datos_condiciones["fecha_inicio"] < date.today():
        raise DatosInvalidos("La reactivación debe comenzar hoy o en una fecha futura.")
    condiciones = dict(datos_condiciones)
    condiciones["recompensa"] = codigo
    return crear_version_recompensa(identidad, condiciones)


def eliminar_condicion_futura_recompensa(identidad: dict, num: int) -> None:
    requiere_administrador(identidad)
    version = consultar_version_recompensa(num)
    if version is None:
        raise EntidadNoEncontrada("La condición de recompensa no existe.")
    if version.fecha_inicio < date.today() + timedelta(days=1):
        raise OperacionNoPermitida("Solo se pueden borrar condiciones que comiencen a partir de mañana.")
    bd.eliminar_version_recompensa(num)


def consultar_version_recompensa(num: int) -> VersionRecompensa | None:
    return bd.buscar_version_recompensa_por_num(num)


def obtener_versiones_de_recompensa(codigo: str) -> list[VersionRecompensa]:
    if consultar_recompensa(codigo) is None:
        raise EntidadNoEncontrada("La recompensa no existe.")
    return bd.obtener_versiones_de_recompensa(codigo)


def obtener_versiones_recompensa_vigentes() -> list[VersionRecompensa]:
    return [
        version
        for recompensa in bd.obtener_todas_las_recompensas()
        for version in bd.obtener_versiones_de_recompensa(recompensa.codigo)
        if version.esta_vigente()
    ]


def finalizar_version_recompensa(identidad: dict, num: int, fecha_final: date) -> VersionRecompensa:
    requiere_administrador(identidad)
    version = consultar_version_recompensa(num)
    if version is None:
        raise EntidadNoEncontrada("La versión de recompensa no existe.")
    if not isinstance(fecha_final, date):
        raise DatosInvalidos("La fecha final no es válida.")

    version.finalizar_vigencia(fecha_final)
    bd.guardar_version_recompensa(version)
    return version


def canjear_recompensa(
    identidad: dict,
    num_membresia: int,
    num_version_recompensa: int,
    compra=None,
) -> TransaccionPuntos:
    membresia, version, transacciones, saldo = validar_canje(
        identidad, num_membresia, num_version_recompensa
    )

    transaccion = TransaccionPuntos(
        num=None,
        movimiento=-version.costo_puntos,
        saldo=saldo - version.costo_puntos,
        fecha=datetime.now(),
        concepto=f"Canje de {version.recompensa.nombre}",
        compra=compra,
        version_recompensa=version,
        membresia=membresia,
    )
    bd.guardar_transaccion_puntos(transaccion)
    return transaccion


def validar_canje(
    identidad: dict,
    num_membresia: int,
    num_version_recompensa: int,
):
    requiere_operador_tienda(identidad)
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    actualizar_estado_membresia(membresia)
    actualizar_vigencia_puntos(membresia)
    if membresia.estado != Membresia.Estado.ACTIVA:
        raise OperacionNoPermitida("La membresía no está activa.")

    version = consultar_version_recompensa(num_version_recompensa)
    if version is None:
        raise EntidadNoEncontrada("La versión de recompensa no existe.")
    if not version.esta_vigente():
        raise VersionNoVigente("La versión de recompensa no está vigente.")

    transacciones = [
        transaccion
        for transaccion in bd.obtener_transacciones_de_miembro(membresia.miembro.num)
        if transaccion.membresia is not None
        and transaccion.membresia.num == num_membresia
    ]
    canjes = [
        transaccion
        for transaccion in transacciones
        if transaccion.version_recompensa is not None
        and transaccion.version_recompensa.num == version.num
        and transaccion.movimiento < 0
    ]
    if version.limite_canjes is not None and len(canjes) >= version.limite_canjes:
        raise LimiteExcedido("Se alcanzó el límite de canjes de la recompensa.")

    saldo = _obtener_saldo(transacciones)
    if saldo < version.costo_puntos:
        raise SaldoInsuficiente("El saldo de puntos es insuficiente.")
    return membresia, version, transacciones, saldo


def obtener_historial_canjes(identidad: dict, num_membresia: int) -> list[TransaccionPuntos]:
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    requiere_administrador_o_propietario(identidad, membresia)

    transacciones = [
        transaccion
        for transaccion in bd.obtener_transacciones_de_miembro(membresia.miembro.num)
        if transaccion.membresia is not None
        and transaccion.membresia.num == num_membresia
    ]
    return sorted(
        (
            transaccion
            for transaccion in transacciones
            if transaccion.version_recompensa is not None
            and transaccion.movimiento < 0
        ),
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    )


def _obtener_recompensa(datos: dict) -> Recompensa:
    referencia = datos.get("recompensa")
    if isinstance(referencia, str):
        recompensa = bd.buscar_recompensa_por_codigo(referencia)
    elif referencia is None:
        recompensa = bd.buscar_recompensa_por_codigo(datos.get("codigo_recompensa"))
    else:
        recompensa = referencia

    if not isinstance(recompensa, Recompensa):
        raise EntidadNoEncontrada("La recompensa no existe.")
    return recompensa


def _seleccionar_condicion_vigente(versiones: list[VersionRecompensa]):
    vigentes = [version for version in versiones if version.esta_vigente()]
    if vigentes:
        return max(vigentes, key=lambda version: (version.fecha_inicio, version.num))
    return None


def _obtener_saldo(transacciones: list[TransaccionPuntos]) -> int:
    if not transacciones:
        return 0
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo
