from datetime import date

from clases.rol import Rol
from clases.usuario import Usuario
from clases.miembro import Miembro
from clases.plan import Plan
from clases.version_plan import VersionPlan
from clases.recompensa import Recompensa
from clases.version_recompensa import VersionRecompensa
from clases.membresia import Membresia
from clases.aplicacion_version_plan import AplicacionVersionPlan

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

rol_administrador = Rol(
    codigo="ADM",
    nombre="Administrador",
    descripcion="Acceso completo al sistema",
)

rol_cajero = Rol(
    codigo="CAJ",
    nombre="Cajero",
    descripcion="Solo puede registrar compras",
)

# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

usuario_1 = Usuario(
    num=1,
    nombre="Carlos",
    primer_apellido="Mendoza",
    segundo_apellido="Ríos",
    telefono="5512345678",
    correo="carlos.mendoza@nexum.com",
    contraseña="admin123",
    rol=rol_administrador,
)

# ---------------------------------------------------------------------------
# Miembros
# ---------------------------------------------------------------------------

miembro_1 = Miembro(
    num=1,
    nombre="Ana",
    primer_apellido="García",
    segundo_apellido="López",
    telefono="5598765432",
    correo="ana.garcia@correo.com",
    contraseña="miembro456",
    fecha_registro=date(2024, 1, 15),
)

# ---------------------------------------------------------------------------
# Planes y sus versiones
# ---------------------------------------------------------------------------

plan_basico = Plan(
    codigo="BAS",
    nombre="Básico",
    descripcion="Plan de entrada sin costo",
    es_gratuita=True,
    periodo_rembolso=0,
)

plan_premium = Plan(
    codigo="PRE",
    nombre="Premium",
    descripcion="Plan de pago con beneficios extendidos",
    es_gratuita=False,
    periodo_rembolso=30,
)

version_plan_1 = VersionPlan(
    num=1,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    precio=0.0,
    puntos_por_peso=1.0,
    porcentaje_descuento=0,
    limite_canjes=3,
    plazo_meses=12,
    plan=plan_basico,
)

version_plan_2 = VersionPlan(
    num=2,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    precio=299.0,
    puntos_por_peso=2.5,
    porcentaje_descuento=10,
    limite_canjes=10,
    plazo_meses=12,
    plan=plan_premium,
)

# ---------------------------------------------------------------------------
# Recompensas y sus versiones
# ---------------------------------------------------------------------------

recompensa_descuento = Recompensa(
    codigo="DESC10",
    nombre="Descuento 10%",
    descripcion="Cupón de 10% en siguiente compra",
)

recompensa_cafe = Recompensa(
    codigo="CAFE",
    nombre="Café gratis",
    descripcion="Un café de cortesía en tienda",
)

version_recompensa_1 = VersionRecompensa(
    num=1,
    costo_puntos=500,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    limite_canjes=1,
    recompensa=recompensa_descuento,
)

version_recompensa_2 = VersionRecompensa(
    num=2,
    costo_puntos=200,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    limite_canjes=3,
    recompensa=recompensa_cafe,
)

# ---------------------------------------------------------------------------
# Membresías y aplicaciones de versión de plan
# ---------------------------------------------------------------------------

membresia_1 = Membresia(
    num=1,
    fecha_activacion=date(2026, 1, 1),
    fecha_vencimiento=date(2027, 1, 1),
    miembro=miembro_1,
    estado=1,  # Membresia.Estado.ACTIVA
)

aplicacion_1 = AplicacionVersionPlan(
    membresia=membresia_1,
    version_plan=version_plan_2,
    fecha=date(2026, 1, 1),
)
