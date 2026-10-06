# Base de datos

La implementación de la base de datos aún está pendiente. El esquema deberá
reflejar las entidades y relaciones definidas en `documentación/DER.json`.

## Entidades principales

- `MIEMBRO`
- `PLAN`
- `VERSION_PLAN`
- `MEMBRESIA`
- `RECOMPENSA`
- `VERSION_RECOMPENSA`
- `CANJE`
- `COMPRA`
- `RENOVACION`
- `TRANSACCION_PUNTOS`
- `ROL`
- `USUARIO`

`Administrador` y `Cajero` no son entidades. Son valores de `ROL` asociados a
entidades `USUARIO`, con permisos diferentes en la interfaz de usuario.

## Relaciones con atributos

La relación entre `VERSION_PLAN` y `MEMBRESIA` debe convertirse en una tabla
intermedia porque contiene `fecha_aplicacion`. Esta tabla conserva el
historial de versiones aplicadas a cada membresía.

Las relaciones de `TRANSACCION_PUNTOS` con `COMPRA` y `CANJE` identifican el
origen de cada movimiento de puntos.

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
| RF-08 | `PLAN.es_gratuita` |
| RF-09 | `VERSION_PLAN` y su relación con `PLAN` |
| RF-10 | `VERSION_PLAN.precio`, `plazo_meses`, `puntos_por_peso` y `porcentaje_descuento` |
| RF-11 | `VERSION_PLAN.fecha_inicio` y `fecha_final` |
| RF-12 | `VERSION_PLAN.limite_canjes` y la relación entre `VERSION_PLAN` y `MEMBRESIA` |
| RF-13 | `RECOMPENSA` |
| RF-14 | `VERSION_RECOMPENSA` y su relación con `RECOMPENSA` |
| RF-15 | `VERSION_RECOMPENSA.costo_puntos`, `fecha_inicio` y `fecha_final` |
| RF-16 | `VERSION_RECOMPENSA.limite_canjes` y `CANJE` |
| RF-17 | `COMPRA`, `MEMBRESIA` y la relación de asociación |
| RF-18 | `COMPRA`, `USUARIO` y la relación que registra al usuario administrativo |
| RF-19 | `TRANSACCION_PUNTOS`, `COMPRA` y la relación de origen de puntos |
| RF-20 | `COMPRA`, `MEMBRESIA` y `TRANSACCION_PUNTOS.fecha` |
| RF-21 | `TRANSACCION_PUNTOS`, `MIEMBRO`, `MEMBRESIA`, `cantidad`, `fecha` y `tipo` |
| RF-22 | `CANJE`, `VERSION_RECOMPENSA` y `TRANSACCION_PUNTOS` |
| RF-23 | La tabla intermedia entre `VERSION_PLAN` y `MEMBRESIA`, especialmente `fecha_aplicacion` |
| RF-24 | `MIEMBRO` |
| RF-25 | `MEMBRESIA`, `ESTADO MEMBRESIA`, `fecha_activacion` y `fecha_vencimiento` |
| RF-26 | `PLAN`, `VERSION_PLAN`, `MEMBRESIA` y la tabla de aplicación de versión |
| RF-27 | `VERSION_PLAN` y sus atributos de condiciones y beneficios |
| RF-28 | `MEMBRESIA`, `RENOVACION` y la relación de registro de renovación |
| RF-29 | `MEMBRESIA` y `ESTADO MEMBRESIA` |
| RF-30 | `COMPRA` y la relación de `COMPRA` con `MEMBRESIA` |
| RF-31 | `TRANSACCION_PUNTOS.cantidad` y los movimientos asociados a `MIEMBRO` |
| RF-32 | `TRANSACCION_PUNTOS`, `fecha`, `cantidad`, `tipo` y `descripcion` |
| RF-33 | `VERSION_RECOMPENSA`, `fecha_inicio` y `fecha_final` |
| RF-34 | `VERSION_RECOMPENSA.costo_puntos` |
| RF-35 | `CANJE`, `VERSION_RECOMPENSA`, `MEMBRESIA` y `TRANSACCION_PUNTOS` |
| RF-36 | `CANJE`, `MEMBRESIA`, `VERSION_RECOMPENSA` y `TRANSACCION_PUNTOS.fecha` |

## Reglas de datos

- Las versiones de plan y recompensa deben conservar su vigencia mediante
  `fecha_inicio` y `fecha_final`.
- Una versión no puede tener una fecha final anterior a su fecha inicial.
- Las versiones de plan y recompensa son inmutables; los cambios de condiciones
  deben representarse mediante una nueva versión con nuevas fechas de vigencia.
- Una membresía debe consultar la versión de plan aplicada que esté vigente.
- Una recompensa solo puede canjearse mientras su versión esté vigente.
- Los límites de uso y canje se calculan por miembro a partir de los registros
  históricos válidos.
- Una versión de plan promocional pertenece a un único plan base.
- Una versión de recompensa pertenece a una única recompensa base.
- `PLAN.es_gratuita` describe la naturaleza estructural del plan; no sustituye
  el `precio` de una `VERSION_PLAN`.
