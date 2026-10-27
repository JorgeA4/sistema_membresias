from clases.miembro import Miembro
from clases.plan import Plan
from clases.version_plan import VersionPlan
from clases.membresia import Membresia
from clases.aplicacion_version_plan import AplicacionVersionPlan
from clases.transaccion_puntos import TransaccionPuntos
from clases.compra import Compra
from clases.recompensa import Recompensa
from clases.version_recompensa import VersionRecompensa
from clases.renovacion import Renovacion
from clases.canje import Canje
from clases.rol import Rol
from clases.usuario import Usuario

# --- Tablas con PK str (codigo) ---

roles: dict[str, Rol] = {}
planes: dict[str, Plan] = {}
recompensas: dict[str, Recompensa] = {}

# --- Tablas con PK int (num) ---

miembros: dict[int, Miembro] = {}
versiones_plan: dict[int, VersionPlan] = {}
membresias: dict[int, Membresia] = {}
transacciones_puntos: dict[int, TransaccionPuntos] = {}
compras: dict[int, Compra] = {}
versiones_recompensa: dict[int, VersionRecompensa] = {}
renovaciones: dict[int, Renovacion] = {}
canjes: dict[int, Canje] = {}
usuarios: dict[int, Usuario] = {}

# --- Tabla puente M:M (sin PK propia) ---

# La clave lógica es la combinación (membresia, version_plan).
aplicaciones_version_plan: list[AplicacionVersionPlan] = []


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

    aplicaciones_version_plan.append(dp.aplicacion_1)


_cargar_datos_prueba()
