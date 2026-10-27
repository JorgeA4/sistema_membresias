import base_de_datos.bd_simulada as bd
from clases.miembro import Miembro
from clases.plan import Plan
from clases.version_plan import VersionPlan
from clases.membresia import Membresia
from clases.aplicacion_version_plan import AplicacionVersionPlan
from clases.recompensa import Recompensa
from clases.version_recompensa import VersionRecompensa
from clases.compra import Compra
from clases.canje import Canje
from clases.renovacion import Renovacion
from clases.transaccion_puntos import TransaccionPuntos
from clases.usuario import Usuario
from clases.rol import Rol

# ---------------------------------------------------------------------------
# Miembro
# ---------------------------------------------------------------------------

def buscar_miembro_por_correo(correo: str) -> Miembro | None:
    for miembro in bd.miembros.values():
        if miembro.correo == correo:
            return miembro
    return None

def buscar_miembro_por_num(num: int) -> Miembro | None:
    return bd.miembros.get(num)

def obtener_todos_los_miembros() -> list[Miembro]:
    return list(bd.miembros.values())

def guardar_miembro(miembro: Miembro) -> None:
    bd.miembros[miembro.num] = miembro

def eliminar_miembro(num: int) -> None:
    bd.miembros.pop(num, None)

# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------

def buscar_usuario_por_correo(correo: str) -> Usuario | None:
    for usuario in bd.usuarios.values():
        if usuario.correo == correo:
            return usuario
    return None

def buscar_usuario_por_num(num: int) -> Usuario | None:
    return bd.usuarios.get(num)

def obtener_todos_los_usuarios() -> list[Usuario]:
    return list(bd.usuarios.values())

def guardar_usuario(usuario: Usuario) -> None:
    bd.usuarios[usuario.num] = usuario

def eliminar_usuario(num: int) -> None:
    bd.usuarios.pop(num, None)

# ---------------------------------------------------------------------------
# Plan y VersionPlan
# ---------------------------------------------------------------------------

def buscar_plan_por_codigo(codigo: str) -> Plan | None:
    return bd.planes.get(codigo)

def obtener_todos_los_planes() -> list[Plan]:
    return list(bd.planes.values())

def guardar_plan(plan: Plan) -> None:
    bd.planes[plan.codigo] = plan

def obtener_versiones_de_plan(codigo_plan: str) -> list[VersionPlan]:
    return [v for v in bd.versiones_plan.values() if v.plan.codigo == codigo_plan]

def buscar_version_plan_vigente(codigo_plan: str) -> VersionPlan | None:
    for version in bd.versiones_plan.values():
        if version.plan.codigo == codigo_plan and version.esta_vigente():
            return version
    return None

def guardar_version_plan(version_plan: VersionPlan) -> None:
    bd.versiones_plan[version_plan.num] = version_plan

# ---------------------------------------------------------------------------
# Membresia y AplicacionVersionPlan
# ---------------------------------------------------------------------------

def buscar_membresia_por_num(num: int) -> Membresia | None:
    return bd.membresias.get(num)

def buscar_membresia_de_miembro(num_miembro: int) -> Membresia | None:
    for membresia in bd.membresias.values():
        if membresia.miembro.num == num_miembro and membresia.esta_vigente():
            return membresia
    return None

def guardar_membresia(membresia: Membresia) -> None:
    bd.membresias[membresia.num] = membresia

def obtener_aplicaciones_de_membresia(num_membresia: int) -> list[AplicacionVersionPlan]:
    return [a for a in bd.aplicaciones_version_plan if a.membresia.num == num_membresia]

def guardar_aplicacion_version_plan(aplicacion: AplicacionVersionPlan) -> None:
    bd.aplicaciones_version_plan.append(aplicacion)

# ---------------------------------------------------------------------------
# Recompensa y VersionRecompensa
# ---------------------------------------------------------------------------

def buscar_recompensa_por_codigo(codigo: str) -> Recompensa | None:
    return bd.recompensas.get(codigo)

def obtener_todas_las_recompensas() -> list[Recompensa]:
    return list(bd.recompensas.values())

def guardar_recompensa(recompensa: Recompensa) -> None:
    bd.recompensas[recompensa.codigo] = recompensa

def obtener_versiones_de_recompensa(codigo_recompensa: str) -> list[VersionRecompensa]:
    return [v for v in bd.versiones_recompensa.values() if v.recompensa.codigo == codigo_recompensa]

def buscar_version_recompensa_vigente(codigo_recompensa: str) -> VersionRecompensa | None:
    for version in bd.versiones_recompensa.values():
        if version.recompensa.codigo == codigo_recompensa and version.esta_vigente():
            return version
    return None

def guardar_version_recompensa(version_recompensa: VersionRecompensa) -> None:
    bd.versiones_recompensa[version_recompensa.num] = version_recompensa

# ---------------------------------------------------------------------------
# Compra, Canje, Renovacion y TransaccionPuntos
# ---------------------------------------------------------------------------

def guardar_compra(compra: Compra) -> None:
    bd.compras[compra.num] = compra

def guardar_canje(canje: Canje) -> None:
    bd.canjes[canje.num] = canje

def guardar_renovacion(renovacion: Renovacion) -> None:
    bd.renovaciones[renovacion.num] = renovacion

def obtener_renovaciones_de_membresia(num_membresia: int) -> list[Renovacion]:
    return [r for r in bd.renovaciones.values() if r.membresia.num == num_membresia]

def guardar_transaccion_puntos(transaccion: TransaccionPuntos) -> None:
    bd.transacciones_puntos[transaccion.num] = transaccion

def obtener_transacciones_de_miembro(num_miembro: int) -> list[TransaccionPuntos]:
    return [t for t in bd.transacciones_puntos.values() if t.miembro.num == num_miembro]

def obtener_saldo_de_miembro(num_miembro: int) -> int:
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    if not transacciones:
        return 0
    return max(transacciones, key=lambda t: t.fecha).saldo

# ---------------------------------------------------------------------------
# Rol
# ---------------------------------------------------------------------------

def buscar_rol_por_codigo(codigo: str) -> Rol | None:
    return bd.roles.get(codigo)

def obtener_todos_los_roles() -> list[Rol]:
    return list(bd.roles.values())
