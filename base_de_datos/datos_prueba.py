from datetime import date

from clases.rol import Rol
from clases.usuario import Usuario
from clases.miembro import Miembro
from clases.plan import Plan
from clases.version_plan import ConfigDescuento, ConfigPuntos, TipoAplicacionPlan, VersionPlan
from clases.recompensa import Recompensa
from clases.version_recompensa import VersionRecompensa
from clases.membresia import Membresia

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
    # Contraseña de prueba en texto plano: admin123
    contraseña="$2b$12$sh.QrNRpkkCbDpMKWHCsZeq8l.BucvScTtRKv.m6x0Oqu6ea9cb0u",
    rol=rol_administrador,
    fecha_registro=date(2024, 1, 10),
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
    # Contraseña de prueba en texto plano: miembro123
    contraseña="$2b$12$MHNd6asNYH5gkEdduHMRLeiP7Ui.ARNbeDbTG1na4wh3YksvqtrYS",
    fecha_registro=date(2024, 1, 15),
)

# ---------------------------------------------------------------------------
# Planes y sus versiones
# ---------------------------------------------------------------------------

plan_basico = Plan(
    codigo="BAS",
    nombre="Básico",
    descripcion="Plan de entrada",
)

plan_premium = Plan(
    codigo="PRE",
    nombre="Premium",
    descripcion="Plan de pago con beneficios extendidos",
)

config_puntos_basico = ConfigPuntos(
    num=1,
    porcentaje=0.01,
    vigencia_meses=None,
)

config_puntos_premium = ConfigPuntos(
    num=2,
    porcentaje=0.025,
    vigencia_meses=12,
)

config_descuento_premium = ConfigDescuento(
    num=1,
    porcentaje=0.10,
)

version_plan_1 = VersionPlan(
    num=1,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    precio=1.0,
    plazo_meses=12,
    aplica_en=TipoAplicacionPlan.AMBAS,
    plan=plan_basico,
    config_puntos=config_puntos_basico,
)

version_plan_2 = VersionPlan(
    num=2,
    fecha_inicio=date(2024, 1, 1),
    fecha_final=date(2026, 12, 31),
    precio=299.0,
    plazo_meses=12,
    aplica_en=TipoAplicacionPlan.AMBAS,
    plan=plan_premium,
    config_puntos=config_puntos_premium,
    config_descuento=config_descuento_premium,
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
# Membresías
# ---------------------------------------------------------------------------

membresia_1 = Membresia(
    num=1,
    fecha_contratacion=date(2026, 1, 1),
    estado=Membresia.Estado.ACTIVA,
    miembro=miembro_1,
    version_plan_actual=version_plan_2,
)
