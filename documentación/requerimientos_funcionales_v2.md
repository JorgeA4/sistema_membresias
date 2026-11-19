# Requerimientos funcionales

## Reglas generales de acceso

La interfaz administrativa es utilizada por entidades `USUARIO` con distintos
roles:

- **Administrador:** puede consultar y modificar todas las funciones incluidas
  en el alcance actual.
- **Cajero:** opera las funciones necesarias para atender a un cliente en
  tienda, pero no configura el sistema ni consulta informes administrativos.
- **Miembro:** consulta su información y sus beneficios desde la interfaz de
  miembro. Las operaciones comerciales se realizan con apoyo de un Cajero o
  Administrador.

La interfaz no contiene reglas de negocio. Los servicios validan el rol, la
identidad, la vigencia, los saldos, los límites y los estados antes de realizar
una operación.

## Gestión de miembros

- **RF-01:** Registrar nuevos miembros. El Administrador y el Cajero pueden
  registrar un miembro para atender su alta en tienda.
- **RF-02:** Consultar la información de los miembros. El Administrador puede
  consultar cualquier miembro; el Cajero solo consulta la información necesaria
  para atender una operación en tienda.
- **RF-03:** Modificar la información de los miembros. Esta operación está
  disponible para el Administrador.

## Gestión de usuarios y roles

- **RF-04:** Registrar usuarios administrativos con un rol asignado. Esta
  operación está disponible para el Administrador.
- **RF-05:** Consultar y modificar la información de los usuarios
  administrativos. Esta operación está disponible para el Administrador.
- **RF-06:** Asignar permisos de acuerdo con el rol del usuario. Solo el
  Administrador puede crear usuarios o modificar sus roles.

El Cajero no puede crear usuarios, asignar permisos ni modificar roles.

## Configuración de planes

- **RF-07:** Crear, consultar y modificar planes de membresía. Esta operación
  está disponible para el Administrador.
- **RF-08:** Definir si un plan es gratuito por su naturaleza base mediante
  `es_gratuita`.
- **RF-09:** Crear versiones regulares o promocionales de un plan. Esta
  operación está disponible para el Administrador.
- **RF-10:** Definir para cada versión su precio, plazo, tasa de acumulación de
  puntos, porcentaje de descuento y configuración de cashback.
- **RF-11:** Definir la vigencia de cada versión mediante fecha de inicio y
  fecha final.
- **RF-12:** Definir el `limite_canjes` de una versión de plan por miembro.

El Cajero no puede crear, modificar ni finalizar planes o versiones de planes.
Solo puede seleccionar versiones vigentes durante una contratación, renovación
o cambio de plan autorizado.

Las condiciones de una versión de plan son inmutables después de creada. Para
cambiar condiciones se crea una nueva versión.

## Configuración de recompensas

- **RF-13:** Crear, consultar y modificar recompensas base. Esta operación está
  disponible para el Administrador.
- **RF-14:** Crear versiones temporales de recompensas. Esta operación está
  disponible para el Administrador.
- **RF-15:** Definir para cada versión el costo en puntos y su período de
  disponibilidad.
- **RF-16:** Definir el límite de canjes de una versión por miembro.

Solo puede existir una versión vigente de cada recompensa base al mismo
tiempo. El Cajero no puede crear, modificar ni configurar recompensas o sus
versiones; únicamente puede seleccionar una versión vigente para atender un
canje.

## Registro de compras y actividad

- **RF-17:** Registrar una compra asociada a una membresía mediante su número.
  El Administrador y el Cajero pueden registrar compras.
- **RF-18:** Registrar el usuario administrativo que realizó la compra.
- **RF-19:** Generar la transacción de puntos correspondiente cuando aplique.
- **RF-20:** Consultar el historial de compras de los miembros. Esta consulta
  administrativa está disponible para el Administrador.
- **RF-21:** Consultar los puntos acumulados y el historial de transacciones de
  puntos de los miembros. Esta consulta administrativa está disponible para el
  Administrador.
- **RF-22:** Consultar el historial de canjes realizados por los miembros. Esta
  consulta administrativa está disponible para el Administrador.
- **RF-23:** Consultar las versiones de plan aplicadas a cada membresía. Esta
  consulta administrativa está disponible para el Administrador.

El Cajero puede consultar únicamente los datos operativos necesarios para
identificar una membresía y completar una operación en tienda. No puede
consultar informes de actividad de membresías ni de usuarios.

## Operaciones de tienda

Estas operaciones son realizadas por el Cajero o el Administrador en atención
directa al cliente.

- Asociar la compra del cliente con su membresía al momento del pago.
- Aplicar cashback disponible como bonificación de la compra.
- Registrar el código de una recompensa solicitado por el cliente y realizar
  el canje si la membresía tiene puntos suficientes y la recompensa está
  vigente.
- Renovar la membresía del cliente.
- Cambiar el plan del cliente mediante una renovación anticipada.
- Registrar un nuevo miembro y contratar su primer plan.

## Contratación inicial y renovaciones

- La contratación inicial utiliza también un registro `Renovacion`.
- La contratación inicial puede utilizar una `VersionPlan` cuya aplicación sea
  `CONTRATACION` o `AMBAS`.
- La contratación inicial crea la membresía y registra su primer periodo.
- Por ahora la contratación inicial no se asocia con una `Compra`.
- Una renovación puede pagarse anticipadamente.
- Una renovación anticipada no cambia inmediatamente el plan vigente.
- El nuevo plan se activa cuando termina el periodo actualmente activo.
- El cambio de plan solo se hace efectivo al iniciar el nuevo periodo.
- La renovación de una membresía `SUSPENDIDA` la reactiva.
- Una membresía `CANCELADA` no se reactiva; para volver a participar se crea
  una nueva membresía mediante una nueva contratación.

## Estados de membresía

- Una membresía permanece `ACTIVA` durante su periodo vigente.
- Cuando termina el periodo vigente sin una renovación aplicable, pasa a
  `SUSPENDIDA`.
- Una membresía suspendida puede reactivarse mediante una renovación realizada
  por el Cajero o el Administrador.
- Si transcurre un mes sin renovación, pasa a `CANCELADA`.
- El cliente puede solicitar la cancelación en tienda.
- La cancelación solicitada por el cliente solo puede realizarla el
  Administrador.
- El Cajero no puede suspender ni cancelar manualmente una membresía.

La actualización de estados se evalúa cuando el sistema consulta u opera la
membresía; no depende de un proceso externo ejecutándose en segundo plano.

## Cashback

- El cashback se genera sobre el monto final de una compra, de acuerdo con la
  configuración de la versión de plan.
- El cashback generado se acumula por mes.
- Durante el mes, el sistema verifica el cashback generado en ese mismo mes
  cada vez que el cliente intenta utilizarlo.
- Cuando el cashback generado durante el mes supera el umbral mínimo mensual,
  se desbloquea todo el cashback generado durante ese mes.
- El cliente puede utilizar el cashback desbloqueado en una compra mediante el
  Cajero o el Administrador.
- Si el cashback generado durante el mes no supera el umbral al terminar el
  mes, se pierde el cashback generado durante ese mes.
- La expiración se registra mediante un movimiento negativo de cashback.
- El saldo desbloqueado de meses anteriores conserva su disponibilidad según
  las reglas de la membresía.
- El Cajero no puede realizar ajustes manuales de cashback.
- El Administrador puede realizar ajustes de cashback.

## Puntos y canjes

- El miembro puede consultar su saldo y sus recompensas disponibles.
- El canje lo registra el Cajero o el Administrador en la operación de tienda.
- El cliente proporciona el código de la recompensa base.
- El sistema localiza automáticamente la única versión vigente de esa
  recompensa.
- El sistema valida la vigencia, el costo en puntos y el límite de canjes.
- Si el saldo es insuficiente, el canje se rechaza.
- El movimiento negativo de puntos se registra al cerrar la operación de
  tienda.
- El Cajero no puede ajustar puntos manualmente.
- El Administrador puede realizar ajustes de puntos.

## Interfaz de miembro

- **RF-24:** Consultar su información personal.
- **RF-25:** Consultar la información y estado de su membresía.
- **RF-26:** Consultar el plan base y la versión vigente aplicada a su
  membresía.
- **RF-27:** Consultar los beneficios y condiciones de la versión vigente.
- **RF-28:** Consultar la información de una renovación o solicitar atención
  en tienda para renovarla. La renovación efectiva la realiza un Cajero o
  Administrador.
- **RF-29:** Solicitar la cancelación en tienda. La cancelación efectiva solo
  la realiza un Administrador.
- **RF-30:** Consultar su historial de compras.
- **RF-31:** Consultar su saldo de puntos disponibles.
- **RF-32:** Consultar el historial de sus transacciones de puntos.
- **RF-33:** Consultar las versiones de recompensas vigentes.
- **RF-34:** Consultar el costo en puntos de cada versión disponible.
- **RF-35:** Solicitar un canje en tienda. El canje efectivo lo realiza un
  Cajero o Administrador.
- **RF-36:** Consultar su historial de canjes realizados.

## Operaciones exclusivas del Administrador

El Administrador puede realizar todas las operaciones del Cajero y además:

- Crear, modificar y administrar usuarios y roles.
- Crear y modificar planes y versiones de planes.
- Crear y modificar recompensas y versiones de recompensas.
- Consultar informes de actividad de membresías.
- Consultar informes de actividad de usuarios y ventas registradas.
- Suspender o cancelar membresías manualmente cuando corresponda.
- Realizar ajustes de puntos.
- Realizar ajustes de cashback.

## Funciones fuera del alcance actual del modelo

Las siguientes funciones conservan su referencia, pero no se implementarán
mientras no existan los atributos correspondientes en el modelo actual:

- **RF-08:** Definir si un plan es gratuito mediante `Plan.es_gratuita`.
- **RF-12:** Definir un límite de canjes de una versión de plan por miembro.
- **RF-23:** Mantener una relación histórica independiente de todas las
  versiones de plan aplicadas a cada membresía.
