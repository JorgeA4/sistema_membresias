# Base de datos

La implementación de la base de datos aún está pendiente. El esquema deberá
reflejar las entidades y relaciones definidas en `documentación/DER.drawio` y
los campos documentados en `documentación/DD.tsv`.

## Decisiones de implementación

- El sistema utilizará MariaDB como sistema gestor de bases de datos.
- El entorno de desarrollo ejecutará MariaDB mediante XAMPP/LAMP.
- phpMyAdmin podrá utilizarse como herramienta gráfica de administración.
- La conexión desde Python se realizará mediante `PyMySQL`.
- Las credenciales se proporcionarán mediante variables de entorno y no se
  almacenarán en el código fuente.
- Las claves primarias utilizarán `INT AUTO_INCREMENT`.
- Los valores monetarios utilizarán `DECIMAL(10, 2)`; no se utilizará `FLOAT`
  para representar dinero.
- Las fechas y horas se almacenarán como `DATETIME`.
- Las contraseñas se almacenarán únicamente como hashes generados con `bcrypt`.
- La integridad de los datos se protegerá mediante claves foráneas,
  restricciones `CHECK`, restricciones `UNIQUE` y transacciones.
- Las versiones históricas de planes y recompensas serán inmutables. Los
  cambios se representarán mediante nuevas versiones.

## Entidades principales

- `MIEMBRO`
- `PLAN`
- `VERSION_PLAN`
- `CONFIG_CASHBACK`
- `CONFIG_PUNTOS`
- `CONFIG_DESCUENTO`
- `DIA_APLICABLE_DESC`
- `MEMBRESIA`
- `RECOMPENSA`
- `VERSION_RECOMPENSA`
- `COMPRA`
- `RENOVACION`
- `TRANSACCION_PUNTOS`
- `TRANSACCION_CASHBACK`
- `ROL`
- `USUARIO`

`Administrador` y `Cajero` no son entidades. Son valores de `ROL` asociados a
entidades `USUARIO`, con permisos diferentes en la interfaz de usuario.

## Trazabilidad de requisitos

La siguiente tabla relaciona cada requisito funcional con los elementos del
modelo de datos que permiten cumplirlo. Las relaciones representan vínculos
del DER y los atributos representan la información necesaria para la función.
Las reglas de permisos se validan en la aplicación usando `USUARIO` y `ROL`;
no constituyen entidades adicionales.

| Requisito | Elementos relacionados del modelo |
|---|---|
| RF-01 | `MIEMBRO` y sus atributos de identificación y registro |
| RF-02 | `MIEMBRO` |
| RF-03 | `MIEMBRO` |
| RF-04 | `USUARIO`, `ROL` y la relación de asignación de rol |
| RF-05 | `USUARIO` |
| RF-06 | `USUARIO`, `ROL` y sus permisos aplicados en la interfaz |
| RF-07 | `PLAN` |
| RF-09 | `VERSION_PLAN` y su relación con `PLAN` |
| RF-10 | `VERSION_PLAN.precio`, `plazo_meses`, `CONFIG_PUNTOS.porcentaje` y `CONFIG_DESCUENTO.porcentaje` |
| RF-11 | `VERSION_PLAN.fecha_inicio` y `fecha_final` |
| RF-13 | `RECOMPENSA` |
| RF-14 | `VERSION_RECOMPENSA` y su relación con `RECOMPENSA` |
| RF-15 | `VERSION_RECOMPENSA.costo_puntos`, `fecha_inicio` y `fecha_final` |
| RF-16 | `VERSION_RECOMPENSA.limite_canjes` |
| RF-17 | `COMPRA`, `MEMBRESIA` y la relación de asociación |
| RF-18 | `COMPRA`, `USUARIO` y la relación que registra al usuario administrativo |
| RF-19 | `TRANSACCION_PUNTOS`, `COMPRA` y la relación de origen de puntos |
| RF-20 | `COMPRA`, `MEMBRESIA` y `TRANSACCION_PUNTOS.fecha` |
| RF-21 | `TRANSACCION_PUNTOS`, `MIEMBRO`, `MEMBRESIA`, `movimiento`, `fecha` y `saldo` |
| RF-22 | `TRANSACCION_PUNTOS.version_recompensa`, `MEMBRESIA`, `movimiento` y `fecha` |
| RF-24 | `MIEMBRO` |
| RF-25 | `MEMBRESIA`, `estado` y `version_plan_actual` |
| RF-26 | `PLAN`, `VERSION_PLAN`, `MEMBRESIA` y `version_plan_actual` |
| RF-27 | `VERSION_PLAN` y sus atributos de condiciones y beneficios |
| RF-28 | `MEMBRESIA`, `RENOVACION` y la relación de registro de renovación |
| RF-29 | `MEMBRESIA` y `ESTADO MEMBRESIA` |
| RF-30 | `COMPRA` y la relación de `COMPRA` con `MEMBRESIA` |
| RF-31 | `TRANSACCION_PUNTOS.movimiento` y los movimientos asociados a `MEMBRESIA` |
| RF-32 | `TRANSACCION_PUNTOS`, `fecha`, `movimiento`, `concepto` y `saldo` |
| RF-33 | `VERSION_RECOMPENSA`, `fecha_inicio` y `fecha_final` |
| RF-34 | `VERSION_RECOMPENSA.costo_puntos` |
| RF-35 | `VERSION_RECOMPENSA`, `TRANSACCION_PUNTOS` y el saldo de puntos de `MEMBRESIA` |
| RF-36 | `TRANSACCION_PUNTOS.version_recompensa`, `MEMBRESIA` y `fecha` |

## Reglas de datos

- Las versiones de plan y recompensa deben conservar su vigencia mediante
  `fecha_inicio` y `fecha_final`.
- Una versión no puede tener una fecha final anterior a su fecha inicial.
- Las versiones de plan y recompensa son inmutables; los cambios de condiciones
  deben representarse mediante una nueva versión con nuevas fechas de vigencia.
- Una membresía debe consultar la versión de plan aplicada que esté vigente.
- Un canje se registra como un movimiento negativo en `TRANSACCION_PUNTOS`,
  asociado a `version_recompensa`.
- Una recompensa solo puede canjearse mientras su versión esté vigente y la
  membresía tenga saldo suficiente.
- El límite de canjes de `VERSION_RECOMPENSA` se valida por membresía a partir
  de sus transacciones de puntos asociadas a esa versión.
- Una versión de plan promocional pertenece a un único plan base.
- Una versión de recompensa pertenece a una única recompensa base.
