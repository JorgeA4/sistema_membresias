from clases.miembro import Miembro
from clases.plan import Plan
from clases.version_plan import VersionPlan
from clases.membresia import Membresia
from clases.transaccion_puntos import TransaccionPuntos
from clases.transaccion_cashback import TransaccionCashback
from clases.compra import Compra
from clases.recompensa import Recompensa
from clases.version_recompensa import VersionRecompensa
from clases.renovacion import Renovacion
from clases.rol import Rol
from clases.usuario import Usuario
from contextlib import contextmanager
from copy import deepcopy

# --- Tablas con PK str (codigo) ---

roles: dict[str, Rol] = {}
planes: dict[str, Plan] = {}
recompensas: dict[str, Recompensa] = {}

# --- Tablas con PK int (num) ---

miembros: dict[int, Miembro] = {}
versiones_plan: dict[int, VersionPlan] = {}
membresias: dict[int, Membresia] = {}
transacciones_puntos: dict[int, TransaccionPuntos] = {}
transacciones_cashback: dict[int, TransaccionCashback] = {}
compras: dict[int, Compra] = {}
versiones_recompensa: dict[int, VersionRecompensa] = {}
renovaciones: dict[int, Renovacion] = {}
usuarios: dict[int, Usuario] = {}

_secuencias: dict[str, int] = {}


@contextmanager
def transaccion():
    """Permite revertir una operación que modifica varias tablas simuladas."""
    nombres_tablas = (
        "miembros",
        "versiones_plan",
        "membresias",
        "transacciones_puntos",
        "transacciones_cashback",
        "compras",
        "versiones_recompensa",
        "renovaciones",
        "usuarios",
        "planes",
        "recompensas",
        "roles",
    )
    respaldo = {nombre: deepcopy(globals()[nombre]) for nombre in nombres_tablas}
    respaldo_secuencias = deepcopy(_secuencias)
    try:
        yield
    except Exception:
        for nombre, tabla in respaldo.items():
            tabla_actual = globals()[nombre]
            tabla_actual.clear()
            tabla_actual.update(tabla)
        _secuencias.clear()
        _secuencias.update(respaldo_secuencias)
        raise


def siguiente_numero(nombre_tabla: str, tabla: dict[int, object]) -> int:
    siguiente = max(_secuencias.get(nombre_tabla, 1), max(tabla, default=0) + 1)
    _secuencias[nombre_tabla] = siguiente + 1
    return siguiente


# ---------------------------------------------------------------------------
# Carga inicial de datos de prueba
# ---------------------------------------------------------------------------

def _cargar_datos_prueba():
    import base_de_datos.datos_prueba as dp

    roles[dp.rol_administrador.codigo] = dp.rol_administrador
    roles[dp.rol_cajero.codigo]         = dp.rol_cajero

    usuarios[dp.usuario_1.num] = dp.usuario_1

    miembros[dp.miembro_1.num] = dp.miembro_1

    planes[dp.plan_basico.codigo]   = dp.plan_basico
    planes[dp.plan_premium.codigo]  = dp.plan_premium

    versiones_plan[dp.version_plan_1.num] = dp.version_plan_1
    versiones_plan[dp.version_plan_2.num] = dp.version_plan_2

    recompensas[dp.recompensa_descuento.codigo] = dp.recompensa_descuento
    recompensas[dp.recompensa_cafe.codigo]       = dp.recompensa_cafe

    versiones_recompensa[dp.version_recompensa_1.num] = dp.version_recompensa_1
    versiones_recompensa[dp.version_recompensa_2.num] = dp.version_recompensa_2

    membresias[dp.membresia_1.num] = dp.membresia_1


_cargar_datos_prueba()
