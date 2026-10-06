sistema_membresias/
│
├── main.py
│
├── clases/
│   ├── miembro.py
│   ├── plan.py
│   ├── version_plan.py
│   ├── membresia.py
│   ├── transaccion_puntos.py
│   ├── compra.py
│   ├── recompensa.py
│   ├── version_recompensa.py
│   ├── renovacion.py
│   ├── canje.py
│   ├── rol.py
│   └── usuario_admin.py
│
├── servicios/
│   ├── servicio_miembro.py
│   ├── servicio_plan.py
│   ├── servicio_version_plan.py
│   ├── servicio_membresia.py
│   ├── servicio_recompensa.py
│   └── servicio_usuario_admin.py
│
├── base_de_datos/
│   └── ...
│
├── interfaz/
│   └── menu.py
│
└── utilidades/
    └── ...

# main.py
Importa el módulo que ejecuta la interfaz inicial y lo corre.

# clases/
Guarda las entidades centrales del sistema. Cada módulo contiene una entidad
principal del modelo.

## miembro.py
Representa a la persona que participa en el programa.

Atributos: `num`, `telefono`, `correo`, `nombre`, `primer_apellido`,
`segundo_apellido`, `fecha_registro`, `contraseña`.

Funciones: `info()`.

## plan.py
Representa la identidad y las características estructurales de un plan.
`es_gratuita` indica si el plan es gratuito por su naturaleza base; no indica
el precio temporal de una versión concreta.

Atributos: `num`, `nombre`, `descripcion`, `es_gratuita`.

Funciones: `info()`.

## version_plan.py
Representa una versión temporal de un plan. Puede ser una versión regular o
una versión promocional. Sus condiciones no deben modificarse después de que
se hayan definido; la versión es inmutable.

Atributos: `num`, `precio`, `plazo_meses`, `puntos_por_peso`,
`porcentaje_descuento`, `limite_canjes`, `fecha_inicio`, `fecha_final`.

Una versión pertenece a un único plan. La vigencia de la versión se controla
con sus fechas. El límite de canjes se interpreta por miembro y se calcula a
partir de las aplicaciones o usos registrados. Para cambiar sus condiciones,
se crea una nueva versión.

Funciones: `info()`, `esta_vigente()`.

## membresia.py
Representa la participación de un miembro en el programa. Sus condiciones
económicas y beneficios se obtienen de la versión de plan aplicada que esté
vigente.

Atributos: `num`, `num_miembro`, `estado`(Enum), `fecha_activacion`,
`fecha_vencimiento`.

Funciones: `info()`, `esta_vencida()`.

La relación entre `VERSION_PLAN` y `MEMBRESIA` registra `fecha_aplicacion`.
Esto permite conservar el historial de versiones aplicadas y volver a la
versión regular cuando termina una versión promocional.

## transaccion_puntos.py
Representa una acumulación o gasto de puntos.

Atributos: `num`, `num_miembro`, `num_membresia`, `cantidad`, `fecha`,
`tipo`(Enum), `descripcion`.

Funciones: `info()`.

La fecha de una operación de puntos pertenece a la transacción. Las
transacciones relacionadas con compras y canjes se identifican mediante sus
relaciones correspondientes.

## compra.py
Representa una compra asociada a una membresía y registrada por un usuario
administrativo.

Atributos: `num`, `num_membresia`, `num_usuario_admin`, `monto`.

La fecha de la compra se obtiene de la transacción asociada.

Funciones: `info()`.

## recompensa.py
Representa la identidad base de una recompensa.

Atributos: `num`, `nombre`, `descripcion`.

Funciones: `info()`.

## version_recompensa.py
Representa una versión temporal de una recompensa. El costo, la disponibilidad
y los límites pueden variar entre versiones sin modificar la recompensa base.

Atributos: `num`, `costo_puntos`, `fecha_inicio`, `fecha_final`,
`limite_canjes`.

Funciones: `info()`, `esta_vigente()`.

Un canje debe asociarse a la versión de recompensa que estaba disponible al
momento de realizarse. El límite se calcula contando los canjes válidos del
miembro para esa versión.

## renovacion.py
Representa una renovación de una membresía.

Atributos: `num`, `num_membresia`, `monto_pagado`, `fecha`.

Funciones: `info()`.

## canje.py
Representa el canje de puntos de una membresía por una versión de recompensa.

Atributos: `num`, `num_membresia`, `num_version_recompensa`.

La fecha y el gasto de puntos se registran mediante la transacción asociada al
canje.

Funciones: `info()`.

## rol.py
Representa un rol de usuario administrativo.

Atributos: `num`, `nombre`, `descripcion`.

Funciones: `info()`.

## usuario_admin.py
Representa a un usuario administrativo con un rol asignado.

Atributos: `num`, `num_rol`, `nombre`, `primer_apellido`, `segundo_apellido`,
`correo`, `telefono`, `contraseña`.

Funciones: `info()`.

# Relaciones con información propia
En el modelo relacional, las relaciones que contienen atributos se convierten
en tablas intermedias. En particular:

- La relación entre `VERSION_PLAN` y `MEMBRESIA` conserva `fecha_aplicacion`.
- Las relaciones entre transacciones y compras o canjes identifican el origen
  de la operación de puntos.

# servicios/
Guarda operaciones que involucran varias entidades y no pertenecen a una
sola clase.

## servicio_miembro.py
Funciones: `eliminar(num)`, `modificar(num, datos)`.

## servicio_plan.py
Funciones: `eliminar(num)`, `modificar(num, datos)`.

## servicio_version_plan.py
Funciones para crear y consultar versiones de plan y aplicar una versión a una
membresía. Las versiones son inmutables. Cuando cambian las condiciones, se
crea una nueva versión con su propio período de vigencia.

## servicio_membresia.py
Funciones: `renovar(id)`, `cancelar(id)` y consulta de la versión vigente.

## servicio_recompensa.py
Funciones para crear, modificar y consultar recompensas base y sus versiones.
Las versiones de recompensa son inmutables; los cambios se representan mediante
una nueva versión.

## servicio_usuario_admin.py
Funciones: `eliminar(num)`, `modificar(num, datos)`.

# base_de_datos/
Contiene la conexión, las consultas y la persistencia del modelo relacional.
También debe hacer cumplir las restricciones de fechas, claves foráneas y
límites de uso definidos para las versiones.

# interfaz/
Contiene la interfaz y su lógica de navegación.

# utilidades/
Contiene funciones reutilizables que no pertenecen directamente al dominio.
