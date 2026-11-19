# Convenciones de implementación

Este documento define el contrato inicial para implementar los servicios de
Nexum sin modificar el modelo de datos vigente.

## Contrato general de servicios

Los servicios reciben identificadores y datos de entrada, validan las reglas
de negocio y delegan la persistencia en `base_de_datos/`. No deben modificar
directamente los diccionarios de `bd_simulada` ni ejecutar SQL.

Las operaciones de escritura administrativas reciben el `Usuario` autenticado
como primer argumento. `Administrador` puede gestionar la configuración y los
registros; `Cajero` únicamente puede registrar compras. Las operaciones de un
miembro reciben el `Miembro` autenticado y validan que sea propietario de la
membresía indicada.

Las funciones de consulta devuelven una entidad, una lista de entidades o
`None` cuando no existe el registro solicitado. Las operaciones de escritura
devuelven la entidad creada o modificada. Las eliminaciones no necesitan
devolver un valor si terminan correctamente.

Los datos recibidos desde formularios se representan inicialmente como un
`dict`.

## Firmas mínimas

### Miembros

```python
registrar_miembro(usuario: Usuario, datos: dict) -> Miembro
consultar_miembro(num: int) -> Miembro | None
obtener_miembros() -> list[Miembro]
modificar_miembro(usuario: Usuario, num: int, datos: dict) -> Miembro
eliminar_miembro(usuario: Usuario, num: int) -> None
```

### Usuarios

```python
registrar_usuario(usuario: Usuario, datos: dict) -> Usuario
consultar_usuario(num: int) -> Usuario | None
obtener_usuarios() -> list[Usuario]
modificar_usuario(usuario: Usuario, num: int, datos: dict) -> Usuario
eliminar_usuario(usuario: Usuario, num: int) -> None
```

### Autenticación

```python
autenticar_miembro(correo: str, contraseña: str) -> Miembro | None
autenticar_usuario(correo: str, contraseña: str) -> Usuario | None
```

### Planes y versiones

```python
registrar_plan(usuario: Usuario, datos: dict) -> Plan
consultar_plan(codigo: str) -> Plan | None
obtener_planes() -> list[Plan]
modificar_plan(usuario: Usuario, codigo: str, datos: dict) -> Plan
eliminar_plan(usuario: Usuario, codigo: str) -> None
crear_version_plan(usuario: Usuario, datos: dict) -> VersionPlan
consultar_version_plan(num: int) -> VersionPlan | None
obtener_versiones_de_plan(codigo_plan: str) -> list[VersionPlan]
finalizar_version_plan(usuario: Usuario, num: int, fecha_final: date) -> VersionPlan
```

### Recompensas y versiones

```python
registrar_recompensa(usuario: Usuario, datos: dict) -> Recompensa
consultar_recompensa(codigo: str) -> Recompensa | None
obtener_recompensas() -> list[Recompensa]
modificar_recompensa(usuario: Usuario, codigo: str, datos: dict) -> Recompensa
eliminar_recompensa(usuario: Usuario, codigo: str) -> None
crear_version_recompensa(usuario: Usuario, datos: dict) -> VersionRecompensa
consultar_version_recompensa(num: int) -> VersionRecompensa | None
obtener_versiones_de_recompensa(codigo: str) -> list[VersionRecompensa]
finalizar_version_recompensa(usuario: Usuario, num: int, fecha_final: date) -> VersionRecompensa
canjear_recompensa(actor, num_membresia: int, num_version_recompensa: int) -> TransaccionPuntos
obtener_historial_canjes(actor, num_membresia: int) -> list[TransaccionPuntos]
```

Un canje se representa mediante una `TransaccionPuntos` con `movimiento`
negativo y `version_recompensa` asociada. El historial de canjes se obtiene
filtrando las transacciones de puntos que tienen esa asociación.

### Membresías

```python
consultar_membresia(num: int) -> Membresia | None
consultar_membresia_de_miembro(num_miembro: int) -> Membresia | None
renovar_membresia(actor, num_membresia: int, num_version_plan: int) -> Renovacion
cancelar_membresia(actor, num_membresia: int) -> Membresia
```

### Compras y actividad

```python
registrar_compra(usuario: Usuario, datos: dict) -> Compra
obtener_compras_de_membresia(num_membresia: int) -> list[Compra]
obtener_transacciones_de_miembro(num_miembro: int) -> list[TransaccionPuntos]
obtener_saldo_de_miembro(num_miembro: int) -> int
```

## Reglas técnicas pendientes

Estas decisiones se documentan aquí para resolverlas durante la implementación:

- Adoptar `date` como representación temporal del alcance actual, porque las
  clases y el DD utilizan fechas. Revisar la decisión general de `DATETIME` en
  `base_de_datos.md` si posteriormente se necesitan horas.
- Usar `Decimal` para todos los importes y porcentajes monetarios.
- En compras, aplicar primero el descuento y después el cashback utilizado.
- Redondear importes monetarios a dos decimales con `ROUND_HALF_UP`.
- Calcular puntos con truncamiento a entero y cashback sobre el monto final.
- El límite mínimo mensual de cashback se calcula con el cashback generado
  durante el mes actual antes de permitir su uso.
- Rechazar compras para membresías que no estén activas, salvo que se acuerde
  una excepción explícita.
- Las renovaciones anticipadas comienzan al día siguiente del último periodo
  registrado; si no existe un periodo futuro, comienzan en la fecha de pago.
- Rechazar eliminaciones de entidades con registros históricos relacionados;
  no se utilizarán eliminaciones físicas cuando destruyan trazabilidad.
- Resolver empates de fecha al calcular el saldo mediante un orden estable por
  número de transacción.
- Validar unicidad de correos, nombres de planes y demás restricciones del DD
  también en la base simulada.
- Mantener las operaciones que escriben varias entidades dentro de una única
  operación atómica cuando la persistencia MariaDB esté disponible.

## Errores de dominio

Los servicios deberán utilizar excepciones específicas en lugar de devolver
`True` o `False` ambiguos. Como contrato inicial se reservan estos nombres:

```text
EntidadNoEncontrada
DatosInvalidos
OperacionNoPermitida
VersionNoVigente
SaldoInsuficiente
LimiteExcedido
```

La jerarquía y los mensajes concretos se definirán al implementar el primer
flujo vertical.

## Fuera del alcance inicial

No se agregarán `Plan.es_gratuita`, `VersionPlan.limite_canjes` ni una relación
histórica independiente entre `VERSION_PLAN` y `MEMBRESIA`, porque no forman
parte del modelo de datos vigente. Los canjes sí se implementan mediante
`TransaccionPuntos` y no requieren una entidad `Canje` independiente.
