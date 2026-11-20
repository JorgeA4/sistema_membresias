# Modelo de clases Python

Este documento traduce el modelo de datos actual de Nexum a clases Python.
Las clases representan datos, relaciones e invariantes propios. La lógica que
coordina varias entidades debe implementarse en `servicios/`.

Las clases deben utilizar atributos en `snake_case` y nombres en español. Cada
clase vive en un archivo dentro de `clases/`, salvo las clases de configuración
de `VersionPlan`, que se agrupan en `version_plan.py`.

## Enumeraciones

```python
from enum import Enum


class EstadoMembresia(Enum):
    ACTIVA = "ACTIVA"
    SUSPENDIDA = "SUSPENDIDA"
    CANCELADA = "CANCELADA"


class TipoAplicacionPlan(Enum):
    CONTRATACION = "CONTRATACION"
    RENOVACION = "RENOVACION"
    AMBAS = "AMBAS"
```

`EstadoMembresia` representa el `estado` de `Membresia`. `TipoAplicacionPlan`
representa los valores permitidos por `VersionPlan.aplica_en`.

## Configuraciones de beneficios

### `ConfigCashback`

Representa las condiciones de cashback asociadas a una versión de plan.

```python
class ConfigCashback:
    num: int
    porcentaje: float
    limite_min_mensual: float | None
```

### `ConfigPuntos`

Representa las condiciones de acumulación y vigencia de puntos.

```python
class ConfigPuntos:
    num: int
    porcentaje: float
    vigencia_meses: int | None
```

### `ConfigDescuento`

Representa las condiciones de descuento de una versión de plan.

```python
class ConfigDescuento:
    num: int
    porcentaje: float
    monto_minimo: float | None
    dias_aplicables: list["DiaAplicableDesc"]
```

### `DiaAplicableDesc`

Representa un día de la semana en el que puede utilizarse una configuración de
descuento. La combinación de `config_descuento` y `dia_semana` es única.

```python
class DiaAplicableDesc:
    config_descuento: ConfigDescuento
    dia_semana: int  # 1 a 7
```

## Entidades base

### `Miembro`

Representa a la persona que participa en el programa.

```python
class Miembro:
    num: int
    nombre: str
    primer_apellido: str
    segundo_apellido: str | None
    telefono: str
    correo: str
    contraseña: str
    fecha_registro: date
```

### `Plan`

Representa la identidad y las características generales de un plan.

```python
class Plan:
    codigo: str
    nombre: str
    descripcion: str | None
```

### `Recompensa`

Representa la identidad base de una recompensa.

```python
class Recompensa:
    codigo: str
    nombre: str
    descripcion: str | None
```

### `Rol`

Representa un rol administrativo y sus permisos.

```python
class Rol:
    codigo: str
    nombre: str
    descripcion: str | None
```

### `Usuario`

Representa a un usuario administrativo con un rol asignado.

```python
class Usuario:
    num: int
    nombre: str
    primer_apellido: str
    segundo_apellido: str | None
    telefono: str | None
    correo: str
    contraseña: str
    rol: Rol
    fecha_registro: date
```

## Versiones

### `VersionPlan`

Representa las condiciones comerciales inmutables de un plan durante un
periodo de vigencia. Una versión promocional puede referenciar la versión
regular de la que deriva.

```python
class VersionPlan:
    num: int
    fecha_inicio: date
    fecha_final: date
    precio: Decimal
    plazo_meses: int
    aplica_en: TipoAplicacionPlan
    plan: Plan
    config_cashback: ConfigCashback | None
    config_puntos: ConfigPuntos | None
    config_descuento: ConfigDescuento | None
    version_base_de_promo: "VersionPlan" | None

    def esta_vigente(self, fecha: date | None = None) -> bool:
        """Indica si la fecha está dentro del periodo de vigencia."""

    def finalizar_vigencia(self, fecha: date) -> None:
        """Actualiza la fecha final sin modificar las condiciones."""
```

Las condiciones de las versiones son inmutables después de crearse. La
vigencia puede acortarse o ampliarse mediante `finalizar_vigencia()`, siempre
respetando las reglas de solapamiento del servicio. Para cambiar las
condiciones se crea una nueva versión.

### `VersionRecompensa`

Representa el costo y la disponibilidad temporal de una recompensa.

```python
class VersionRecompensa:
    num: int
    fecha_inicio: date
    fecha_final: date
    costo_puntos: int
    limite_canjes: int | None
    recompensa: Recompensa

    def esta_vigente(self, fecha: date | None = None) -> bool:
        """Indica si la fecha está dentro del periodo de disponibilidad."""

    def finalizar_vigencia(self, fecha: date) -> None:
        """Acorta la disponibilidad sin modificar las condiciones."""
```

Las condiciones de las versiones de recompensa son inmutables después de
crearse. La disponibilidad puede acortarse mediante `finalizar_vigencia()`.

## Membresías y relaciones históricas

### `Membresia`

Representa la participación de un miembro en el programa y conserva el estado
actual de esa participación.

```python
class Membresia:
    num: int
    fecha_contratacion: date
    estado: EstadoMembresia
    miembro: Miembro
    version_plan_actual: VersionPlan | None
```

El cambio de estado, la renovación y la selección de versiones vigentes son
operaciones coordinadas por servicios.

## Operaciones y movimientos

### `Renovacion`

Representa la contratación de un nuevo periodo para una membresía.

```python
class Renovacion:
    num: int
    fecha_pago: date
    monto_pagado: Decimal
    fecha_inicio_periodo: date
    fecha_fin_periodo: date
    membresia: Membresia
    version_plan_comprado: VersionPlan
```

`fecha_fin_periodo` es un dato derivado del inicio del periodo y del plazo de
la versión comprada. El servicio de renovación coordina el cálculo y la
actualización de la membresía.

### `Compra`

Representa una compra asociada a una membresía y registrada por un usuario
administrativo.

```python
class Compra:
    num: int
    monto_base: Decimal
    porcentaje_descuento: Decimal
    descuento_nominal: Decimal
    cashback_aplicado: Decimal
    monto_final: Decimal
    membresia: Membresia
    usuario: Usuario
```

Los campos `descuento_nominal` y `monto_final` son calculados y almacenados
para conservar el resultado histórico de la operación. La creación de una
compra, la aplicación de beneficios y la generación de transacciones deben
coordinarse desde un servicio.

### `TransaccionPuntos`

Representa un movimiento de puntos de una membresía.

```python
class TransaccionPuntos:
    num: int
    movimiento: int
    saldo: int
    fecha: date
    concepto: str | None
    compra: Compra | None
    version_recompensa: VersionRecompensa | None
    membresia: Membresia
```

`saldo` conserva el saldo resultante después de la transacción. La validación
de saldos, la creación de movimientos y el control de canjes corresponden a
servicios.

### `TransaccionCashback`

Representa un movimiento monetario de cashback de una membresía.

```python
class TransaccionCashback:
    num: int
    monto: Decimal
    saldo: Decimal
    fecha: date
    concepto: str | None
    compra: Compra | None
    membresia: Membresia
```

`saldo` conserva el saldo resultante después del movimiento. La generación y
aplicación del cashback deben coordinarse desde servicios.

## Responsabilidades fuera de las clases

Las siguientes operaciones no deben implementarse como métodos de una sola
entidad porque coordinan varias clases:

- Registrar una compra y calcular sus beneficios.
- Generar transacciones de puntos o cashback.
- Renovar o cancelar una membresía.
- Aplicar una versión de plan y conservar su historial.
- Validar límites de canjes, cashback o puntos por miembro.
- Consultar y modificar registros mediante la base de datos.
- Aplicar permisos según el rol del usuario.

Estas responsabilidades pertenecen a `servicios/` y `base_de_datos/`.
