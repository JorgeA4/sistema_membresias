# Alcance del Proyecto

El desarrollo se divide en tres capas de prioridad. La Capa 1 debe estar
completa antes de trabajar en las siguientes. Las capas 2 y 3 se abordan en
ese orden si el tiempo lo permite.

---

## Capa 1 — Funcional mínimo
El sistema cumple su propósito principal. Todo lo que está aquí debe funcionar
para considerar el proyecto entregable.

### Interfaz de usuario
Las funciones de esta interfaz dependen del rol del usuario:

- El rol `Administrador` puede realizar todas las funciones de gestión.
- El rol `Administrador` también puede registrar compras asociadas a
  membresías.
- El rol `Cajero` puede registrar compras asociadas a membresías, pero está
  limitado a esa operación.

Ambos roles pertenecen a la entidad `USUARIO`; no representan entidades
separadas en el modelo.

- Registrar, consultar y modificar miembros.
- Crear, consultar y modificar planes.
- Definir si un plan es gratuito por su naturaleza base.
- Crear versiones regulares o promocionales de planes.
- Definir las condiciones y vigencia de cada versión de plan.
- Crear, consultar y modificar recompensas base.
- Crear versiones disponibles de recompensas.
- Definir costo, vigencia y límite de canjes de cada versión.
- Registrar compras asociadas a membresías, cuando el usuario tenga el rol
  `Administrador` o `Cajero`.
- Consultar el historial de compras y puntos de un miembro.

### Interfaz de miembro
- Consultar su información personal y estado de membresía.
- Consultar el plan base y la versión vigente aplicada a su membresía.
- Consultar sus puntos acumulados y disponibles.
- Consultar las versiones de recompensas disponibles.
- Canjear puntos por versiones de recompensas disponibles.
- Consultar su historial de canjes.
- Solicitar la renovación o cancelación de su membresía.

La definición de gratuidad del plan, el límite de canjes de una versión de plan,
el historial independiente de versiones aplicadas queda fuera del alcance
inicial porque no forma parte del modelo de datos vigente. Los canjes sí forman
parte del alcance inicial y se registran mediante `TRANSACCION_PUNTOS`.

---

## Capa 2 — Estético adicional
El sistema funciona correctamente. Esta capa mejora la presentación y la
experiencia de uso, sin agregar funcionalidades nuevas.

- Mejorar el formato visual de los menús e interfaces.
- Mostrar claramente la vigencia y condiciones de las versiones.
- Presentar mensajes de confirmación, error y éxito consistentes.
- Presentar ordenadamente el historial de compras, canjes y puntos.
- Pulir el flujo de navegación entre pantallas.

---

## Capa 3 — Extras
Funcionalidades deseables que se implementan solo si queda tiempo, una vez
completadas las capas 1 y 2.

- Código público aleatorio por membresía para identificación segura mediante
  QR.
- Generación y visualización de código QR de membresía.
- Exportación de historial o reportes.
- Historial detallado de cambios en planes, versiones y recompensas.
- Otros por definir.
