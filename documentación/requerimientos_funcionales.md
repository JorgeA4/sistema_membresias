# Interfaz de usuario

La interfaz de usuario es utilizada por entidades `USUARIO` con distintos
roles y permisos. El rol `Administrador` tiene acceso completo a la gestión
del sistema, incluido el registro de compras. El rol `Cajero` también puede
registrar compras, pero está limitado a esa operación. Ambos son usuarios
administrativos; `Administrador` y `Cajero` no son entidades separadas del
modelo.

## Gestión de miembros
- **RF-01:** Registrar nuevos miembros.
- **RF-02:** Consultar la información de los miembros.
- **RF-03:** Modificar la información de los miembros.

## Gestión de usuarios y roles
- **RF-04:** Registrar usuarios administrativos con un rol asignado.
- **RF-05:** Consultar y modificar la información de los usuarios
  administrativos.
- **RF-06:** Asignar permisos de acuerdo con el rol del usuario.

## Configuración de planes
- **RF-07:** Crear, consultar y modificar planes de membresía.
- **RF-08:** Definir si un plan es gratuito por su naturaleza base mediante
  `es_gratuita`.
- **RF-09:** Crear versiones regulares o promocionales de un plan.
- **RF-10:** Definir para cada versión su precio, plazo, tasa de acumulación de
  puntos y porcentaje de descuento.
- **RF-11:** Definir la vigencia de cada versión mediante fecha de inicio y
  fecha final.
- **RF-12:** Definir el `limite_canjes` de una versión de plan por miembro.

## Configuración de recompensas
- **RF-13:** Crear, consultar y modificar recompensas base.
- **RF-14:** Crear versiones temporales de recompensas.
- **RF-15:** Definir para cada versión el costo en puntos y su período de
  disponibilidad.
- **RF-16:** Definir el límite de canjes de una versión por miembro.

## Registro de compras y actividad
- **RF-17:** Registrar una compra asociada a una membresía mediante su número.
- **RF-18:** Registrar el usuario administrativo que realizó la compra.
- **RF-19:** Generar la transacción de puntos correspondiente cuando aplique.
- **RF-20:** Consultar el historial de compras de los miembros.
- **RF-21:** Consultar los puntos acumulados y el historial de transacciones de
  puntos de los miembros.
- **RF-22:** Consultar el historial de canjes realizados por los miembros.
- **RF-23:** Consultar las versiones de plan aplicadas a cada membresía.

---

# Interfaz de miembro

La interfaz de miembro es utilizada por las entidades `MIEMBRO`. Permite a
cada miembro consultar su información y operar únicamente sobre sus propias
membresías, puntos y recompensas.

## Gestión y consulta de membresía
- **RF-24:** Consultar su información personal.
- **RF-25:** Consultar la información y estado de su membresía.
- **RF-26:** Consultar el plan base y la versión vigente aplicada a su
  membresía.
- **RF-27:** Consultar los beneficios y condiciones de la versión vigente.
- **RF-28:** Solicitar la renovación de su membresía cuando corresponda.
- **RF-29:** Solicitar la cancelación de su membresía cuando corresponda.

## Actividad y puntos
- **RF-30:** Consultar su historial de compras.
- **RF-31:** Consultar su saldo de puntos disponibles.
- **RF-32:** Consultar el historial de sus transacciones de puntos.

## Recompensas
- **RF-33:** Consultar las versiones de recompensas vigentes.
- **RF-34:** Consultar el costo en puntos de cada versión disponible.
- **RF-35:** Canjear puntos por versiones de recompensas disponibles.
- **RF-36:** Consultar su historial de canjes realizados.
