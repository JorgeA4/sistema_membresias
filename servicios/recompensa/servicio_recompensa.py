from datetime import date

import base_de_datos.consultas as bd
from clases.membresia import Membresia
from clases.recompensa import Recompensa
from clases.transaccion_puntos import TransaccionPuntos
from clases.version_recompensa import VersionRecompensa
from servicios.autorizacion.servicio_autorizacion import (
    requiere_administrador,
    requiere_administrador_o_propietario,
)


def registrar_recompensa(usuario, datos: dict) -> Recompensa:
    requiere_administrador(usuario)
    codigo = datos["codigo"].strip()
    nombre = datos["nombre"].strip()

    if not codigo or not nombre:
        raise ValueError("El código y el nombre de la recompensa son obligatorios.")
    if bd.buscar_recompensa_por_codigo(codigo) is not None:
        raise ValueError("El código de la recompensa ya existe.")

    recompensa = Recompensa(codigo, nombre, datos.get("descripcion"))
    bd.guardar_recompensa(recompensa)
    return recompensa


def consultar_recompensa(codigo: str) -> Recompensa | None:
    return bd.buscar_recompensa_por_codigo(codigo)


def obtener_recompensas() -> list[Recompensa]:
    return bd.obtener_todas_las_recompensas()


def modificar_recompensa(usuario, codigo: str, datos: dict) -> Recompensa:
    requiere_administrador(usuario)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise ValueError("La recompensa no existe.")

    atributos_permitidos = {"nombre", "descripcion"}
    atributos_invalidos = set(datos) - atributos_permitidos
    if atributos_invalidos:
        raise ValueError("Los datos contienen atributos no modificables.")

    if "nombre" in datos:
        nombre = datos["nombre"].strip()
        if not nombre:
            raise ValueError("El nombre de la recompensa es obligatorio.")
        recompensa.nombre = nombre

    if "descripcion" in datos:
        recompensa.descripcion = datos["descripcion"]

    bd.guardar_recompensa(recompensa)
    return recompensa


def eliminar_recompensa(usuario, codigo: str) -> None:
    requiere_administrador(usuario)
    recompensa = consultar_recompensa(codigo)
    if recompensa is None:
        raise ValueError("La recompensa no existe.")
    if bd.obtener_versiones_de_recompensa(codigo):
        raise ValueError("No se puede eliminar una recompensa con versiones registradas.")
    bd.eliminar_recompensa(codigo)


def crear_version_recompensa(usuario, datos: dict) -> VersionRecompensa:
    requiere_administrador(usuario)
    recompensa = _obtener_recompensa(datos)
    fecha_inicio = datos["fecha_inicio"]
    fecha_final = datos["fecha_final"]
    costo_puntos = datos["costo_puntos"]
    limite_canjes = datos.get("limite_canjes")

    if not isinstance(fecha_inicio, date) or not isinstance(fecha_final, date):
        raise ValueError("Las fechas de la versión deben ser fechas válidas.")
    if fecha_final < fecha_inicio:
        raise ValueError("La fecha final no puede ser anterior a la inicial.")
    if isinstance(costo_puntos, bool) or not isinstance(costo_puntos, int) or costo_puntos <= 0:
        raise ValueError("El costo debe ser un entero mayor que cero.")
    if (
        limite_canjes is not None
        and (
            isinstance(limite_canjes, bool)
            or not isinstance(limite_canjes, int)
            or limite_canjes <= 0
        )
    ):
        raise ValueError("El límite de canjes debe ser un entero mayor que cero.")

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


def consultar_version_recompensa(num: int) -> VersionRecompensa | None:
    return bd.buscar_version_recompensa_por_num(num)


def obtener_versiones_de_recompensa(codigo: str) -> list[VersionRecompensa]:
    if consultar_recompensa(codigo) is None:
        raise ValueError("La recompensa no existe.")
    return bd.obtener_versiones_de_recompensa(codigo)


def obtener_versiones_recompensa_vigentes() -> list[VersionRecompensa]:
    return [
        version
        for recompensa in obtener_recompensas()
        for version in bd.obtener_versiones_de_recompensa(recompensa.codigo)
        if version.esta_vigente()
    ]


def finalizar_version_recompensa(usuario, num: int, fecha_final: date) -> VersionRecompensa:
    requiere_administrador(usuario)
    version = consultar_version_recompensa(num)
    if version is None:
        raise ValueError("La versión de recompensa no existe.")
    if not isinstance(fecha_final, date):
        raise ValueError("La fecha final no es válida.")

    version.finalizar_vigencia(fecha_final)
    return version


def canjear_recompensa(
    actor,
    num_membresia: int,
    num_version_recompensa: int,
) -> TransaccionPuntos:
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise ValueError("La membresía no existe.")
    requiere_administrador_o_propietario(actor, membresia)
    if membresia.estado != Membresia.Estado.ACTIVA:
        raise ValueError("La membresía no está activa.")

    version = consultar_version_recompensa(num_version_recompensa)
    if version is None:
        raise ValueError("La versión de recompensa no existe.")
    if not version.esta_vigente():
        raise ValueError("La versión de recompensa no está vigente.")

    transacciones = bd.obtener_transacciones_de_miembro(membresia.miembro.num)
    canjes = [
        transaccion
        for transaccion in transacciones
        if transaccion.version_recompensa is not None
        and transaccion.version_recompensa.num == version.num
        and transaccion.movimiento < 0
    ]
    if version.limite_canjes is not None and len(canjes) >= version.limite_canjes:
        raise ValueError("Se alcanzó el límite de canjes de la recompensa.")

    saldo = _obtener_saldo(transacciones)
    if saldo < version.costo_puntos:
        raise ValueError("El saldo de puntos es insuficiente.")

    transaccion = TransaccionPuntos(
        num=None,
        movimiento=-version.costo_puntos,
        saldo=saldo - version.costo_puntos,
        fecha=date.today(),
        concepto=f"Canje de {version.recompensa.nombre}",
        compra=None,
        version_recompensa=version,
        membresia=membresia,
    )
    bd.guardar_transaccion_puntos(transaccion)
    return transaccion


def obtener_historial_canjes(actor, num_membresia: int) -> list[TransaccionPuntos]:
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise ValueError("La membresía no existe.")
    requiere_administrador_o_propietario(actor, membresia)

    transacciones = bd.obtener_transacciones_de_miembro(membresia.miembro.num)
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
        raise ValueError("La recompensa no existe.")
    return recompensa


def _obtener_saldo(transacciones: list[TransaccionPuntos]) -> int:
    if not transacciones:
        return 0
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo
