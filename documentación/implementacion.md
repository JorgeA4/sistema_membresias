# Convenciones de implementación

Este documento define el contrato vigente de los servicios de Nexum y separa
las funciones implementadas de las decisiones técnicas pendientes. Se mantiene
el modelo de datos actual sin agregar entidades ni atributos.

## Estado actual

Implementado sobre la base de datos MariaDB mediante el adaptador de
`base_de_datos/`:

- Identidad neutral para la sesión y autorización por rol.
- Login, logout y navegación de las interfaces de miembro y usuario.
- Menú operativo de Cajero y Administrador.
- Contratación inicial mediante `Renovacion`.
- Renovaciones anticipadas y cambios de plan diferidos al fin del periodo.
- Actualización automática de estados `ACTIVA`, `SUSPENDIDA` y `CANCELADA`.
- Ventas con descuentos, puntos y cashback.
- Canjes asociados a una venta.
- Ajustes de puntos y cashback exclusivos del Administrador.
- Consultas de actividad protegidas por identidad y propiedad.

## Contrato general de servicios

Los servicios reciben identificadores y datos de entrada, validan las reglas
de negocio y delegan la persistencia en `base_de_datos/`. No deben modificar
directamente los diccionarios de `bd_simulada` ni ejecutar SQL.

Las operaciones protegidas reciben una identidad neutral como primer argumento,
con `tipo` y `num`, además de datos mínimos para presentación. Los servicios
resuelven internamente la entidad autenticada y validan sus permisos. La
interfaz no almacena entidades del dominio.

`Administrador` puede gestionar la configuración, los registros, las
operaciones de tienda, los informes y los ajustes. `Cajero` puede registrar
miembros y realizar operaciones presenciales: ventas, cashback, canjes,
contrataciones, renovaciones y cambios de plan. `Gerente de Sucursal` tiene
acceso completo a las operaciones de tienda, miembros y membresías, actividad
y ajustes; solo puede consultar planes y recompensas, y no puede administrar
usuarios ni configurar planes o recompensas. `Cajero` no puede configurar el
sistema, administrar usuarios, realizar ajustes ni consultar informes
administrativos. Las operaciones de consulta de un miembro validan que sea
propietario cuando la identidad corresponde a un miembro.

Las funciones de consulta devuelven una entidad, una lista de entidades o
`None` cuando no existe el registro solicitado. Las operaciones de escritura
devuelven la entidad creada o modificada. Las eliminaciones no necesitan
devolver un valor si terminan correctamente.

Los datos recibidos desde formularios se representan inicialmente como un
`dict`.

## Firmas mínimas

### Miembros

```python
registrar_miembro(identidad: dict, datos: dict) -> Miembro
consultar_miembro(identidad: dict, num: int) -> Miembro | None
obtener_miembros() -> list[Miembro]
modificar_miembro(identidad: dict, num: int, datos: dict) -> Miembro
eliminar_miembro(identidad: dict, num: int) -> None
```

### Usuarios

```python
registrar_usuario(identidad: dict, datos: dict) -> Usuario
consultar_usuario(identidad: dict, num: int) -> Usuario | None
obtener_usuarios(identidad: dict) -> list[Usuario]
modificar_usuario(identidad: dict, num: int, datos: dict) -> Usuario
eliminar_usuario(identidad: dict, num: int) -> None
```

### Autenticación

```python
autenticar_miembro(correo: str, contraseña: str) -> dict | None
autenticar_usuario(correo: str, contraseña: str) -> dict | None
```

### Planes y versiones

```python
registrar_plan(identidad: dict, datos: dict) -> Plan
consultar_plan(codigo: str) -> Plan | None
obtener_planes(identidad: dict) -> list[Plan]
modificar_plan(identidad: dict, codigo: str, datos: dict) -> Plan
eliminar_plan(identidad: dict, codigo: str) -> None
crear_version_plan(identidad: dict, datos: dict) -> VersionPlan
consultar_version_plan(num: int) -> VersionPlan | None
obtener_versiones_de_plan(codigo_plan: str) -> list[VersionPlan]
finalizar_version_plan(identidad: dict, num: int, fecha_final: date) -> VersionPlan
```

### Recompensas y versiones

```python
registrar_recompensa(identidad: dict, datos: dict) -> Recompensa
consultar_recompensa(codigo: str) -> Recompensa | None
obtener_recompensas(identidad: dict) -> list[Recompensa]
modificar_recompensa(identidad: dict, codigo: str, datos: dict) -> Recompensa
eliminar_recompensa(identidad: dict, codigo: str) -> None
crear_version_recompensa(identidad: dict, datos: dict) -> VersionRecompensa
consultar_version_recompensa(num: int) -> VersionRecompensa | None
obtener_versiones_de_recompensa(codigo: str) -> list[VersionRecompensa]
finalizar_version_recompensa(identidad: dict, num: int, fecha_final: date) -> VersionRecompensa
canjear_recompensa(identidad: dict, num_membresia: int, num_version_recompensa: int, compra=None) -> TransaccionPuntos
obtener_historial_canjes(identidad: dict, num_membresia: int) -> list[TransaccionPuntos]
validar_canje(identidad: dict, num_membresia: int, num_version_recompensa: int)
obtener_versiones_recompensa_vigentes() -> list[VersionRecompensa]
```

Un canje se representa mediante una `TransaccionPuntos` con `movimiento`
negativo y `version_recompensa` asociada. El historial de canjes se obtiene
filtrando las transacciones de puntos que tienen esa asociación.

### Membresías

```python
consultar_membresia(identidad: dict, num: int) -> Membresia | None
consultar_membresia_de_miembro(identidad: dict, num_miembro: int) -> Membresia | None
renovar_membresia(identidad: dict, num_membresia: int, num_version_plan: int) -> Renovacion
contratar_membresia(identidad: dict, num_miembro: int, num_version_plan: int) -> Renovacion
cancelar_membresia(identidad: dict, num_membresia: int) -> Membresia
suspender_membresia(identidad: dict, num_membresia: int) -> Membresia
actualizar_estado_membresia(membresia: Membresia, fecha: date | None = None) -> Membresia
```

### Compras y actividad

```python
registrar_compra(identidad: dict, datos: dict) -> Compra
obtener_compras_de_membresia(identidad: dict, num_membresia: int) -> list[Compra]
obtener_transacciones_de_miembro(identidad: dict, num_miembro: int) -> list[TransaccionPuntos]
obtener_saldo_de_miembro(identidad: dict, num_miembro: int) -> int
obtener_transacciones_cashback_de_membresia(identidad: dict, num_membresia: int) -> list[TransaccionCashback]
obtener_saldo_cashback_de_membresia(identidad: dict, num_membresia: int) -> Decimal
```

### Caja y ajustes

```python
registrar_operacion_caja(identidad: dict, datos: dict) -> dict
ajustar_puntos(identidad: dict, num_membresia: int, movimiento: int, concepto: str)
ajustar_cashback(identidad: dict, num_membresia: int, movimiento, concepto: str)
```

## Reglas técnicas vigentes

Estas reglas se aplican en la implementación actual:

- Adoptar `date` como representación temporal del alcance actual, porque las
  clases y el DD utilizan fechas. Revisar la decisión general de `DATETIME` en
  `base_de_datos.md` si posteriormente se necesitan horas.
- Usar `Decimal` para todos los importes y porcentajes monetarios.
- En compras, aplicar primero el descuento y después el cashback utilizado.
- Redondear importes monetarios a dos decimales con `ROUND_HALF_UP`.
- Calcular puntos con truncamiento a entero y cashback sobre el monto final.
- El umbral mensual de cashback se valida en el momento de uso; al superarlo
  durante el mes se desbloquea todo lo generado en ese mes.
- Rechazar compras para membresías que no estén activas.
- Las renovaciones anticipadas comienzan al día siguiente del último periodo
  registrado y no sustituyen el plan vigente hasta que termina ese periodo.
- La contratación inicial utiliza también `Renovacion` y no se asocia a una
  `Compra`.
- Una membresía vencida pasa a `SUSPENDIDA`; una renovación la reactiva.
- Una membresía permanece suspendida durante un mes sin renovación y después
  pasa a `CANCELADA`. Una membresía cancelada requiere una nueva contratación.
- El estado se actualiza al consultar u operar la membresía; no existe un
  proceso externo en segundo plano.
- Solo puede existir una versión vigente de cada recompensa base.
- El cashback del mes se puede utilizar cuando el generado en ese mes supera
  el umbral; si el mes termina sin superar el umbral, se registra su expiración
  como movimiento negativo.
- Los puntos tienen una vigencia global por membresía: se calcula desde la
  última compra que generó puntos y la `vigencia_meses` de la configuración
  aplicable. Si la fecha actual supera la fecha calculada, se registra un
  ajuste negativo por el saldo total. La comprobación ocurre al consultar,
  comprar o intentar canjear; los puntos se mantienen disponibles durante toda
  la fecha calculada.
- Una operación de caja se ejecuta atómicamente en MariaDB. Si falla la venta,
  el canje o una transacción asociada, se revierte toda la operación.
- Las solicitudes de renovación, cancelación y canje del miembro son
  informativas; la operación efectiva se realiza en caja.
- Rechazar eliminaciones de entidades con registros históricos relacionados;
  no se utilizarán eliminaciones físicas cuando destruyan trazabilidad.
- Resolver empates de fecha al calcular el saldo mediante un orden estable por
  número de transacción.
- Validar unicidad de correos, nombres de planes y demás restricciones del DD
  también en MariaDB.
- Mantener las operaciones que escriben varias entidades dentro de una única
  operación atómica.

## Trabajo pendiente

- Añadir eliminación y finalización de todas las entidades desde la interfaz
  administrativa, respetando la trazabilidad histórica.
- Revisar y completar la atomicidad de todas las operaciones que escriben
  varias entidades, incluyendo contratación y renovación de membresías.
- Crear excepciones de dominio específicas y sustituir gradualmente el uso
  directo de `ValueError` y `PermissionError`.
- Completar pruebas automatizadas de servicios, estados, cashback, caja y
  navegación TUI.

## Errores de dominio

Los servicios utilizan excepciones específicas en lugar de devolver `True` o
`False` ambiguos. Se definen en `utilidades/excepciones.py`:

```text
EntidadNoEncontrada
DatosInvalidos
OperacionNoPermitida
VersionNoVigente
SaldoInsuficiente
LimiteExcedido
```

`DatosInvalidos` conserva compatibilidad con `ValueError` y
`OperacionNoPermitida` con `PermissionError`. `EntidadNoEncontrada` deriva de
`DatosInvalidos`; `VersionNoVigente` también representa una validación de
vigencia, mientras que `SaldoInsuficiente` y `LimiteExcedido` representan
operaciones rechazadas por reglas de negocio. Los errores técnicos no
expuestos por MariaDB se encapsulan como `ErrorPersistencia`.

## Fuera del alcance inicial

No se agregarán `Plan.es_gratuita`, `VersionPlan.limite_canjes` ni una relación
histórica independiente entre `VERSION_PLAN` y `MEMBRESIA`, porque no forman
parte del modelo de datos vigente. Los canjes sí se implementan mediante
`TransaccionPuntos` y no requieren una entidad `Canje` independiente.
