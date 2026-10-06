# Proyecto
Sistema de gestión de membresías y programas de fidelización.

# Nombre
Nexum — del latín *nexus*, que significa vínculo o unión. El nombre refleja
la relación que el sistema establece entre un negocio y sus clientes a través
de las membresías.

# Problemática
Los negocios que ofrecen programas de membresía a sus clientes —ya sean
gratuitos o de pago— necesitan gestionar el registro de miembros, la vigencia
de sus membresías, el seguimiento de su actividad, la acumulación de puntos y
el canje de recompensas. Sin un sistema dedicado, esta gestión se vuelve
manual, propensa a errores y difícil de escalar.

# Descripción
Nexum es un sistema para la gestión de membresías y programas de fidelización.
Permite a un negocio administrar a sus miembros, los planes, los beneficios y
las recompensas asociadas, así como dar seguimiento a la actividad de cada
cliente dentro del programa.

El sistema contempla distintos tipos de acceso. El personal administrativo se
encarga de la operación y configuración del programa, mientras que los miembros
pueden consultar su información, su membresía, sus puntos y los beneficios
disponibles.

La operación del programa se apoya en un modelo de datos que distingue entre
entidades base y sus versiones temporales, lo que permite conservar el historial
de las condiciones aplicadas a lo largo del tiempo.

# Interfaces

## Interfaz de usuario
Utilizada por las entidades `USUARIO`. El acceso depende del rol asignado:

- El rol `Administrador` tiene acceso completo a la gestión del sistema.
- El rol `Cajero` unicamente puede registrar compras asociadas a membresías.


## Interfaz de miembro
Utilizada por las entidades `MIEMBRO` para consultar su membresía, la versión
de plan vigente, sus puntos, las versiones de recompensas disponibles y su
historial de actividad.

# Funcionalidades principales

## Funciones disponibles según el rol de usuario
- Gestión de miembros: registro, consulta y modificación.
- Configuración de planes y sus versiones temporales.
- Definición de vigencias, precios, beneficios y límites de uso.
- Gestión de recompensas base y sus versiones disponibles.
- Gestión de usuarios administrativos y roles.
- Consulta de compras, transacciones de puntos y canjes.
- Registro de compras asociadas a una membresía mediante su número.

## Funciones del miembro
- Consulta de su información personal y estado de membresía.
- Consulta del plan base y de la versión vigente aplicada.
- Consulta de puntos y transacciones.
- Consulta y canje de versiones de recompensas disponibles.
- Solicitud de renovación o cancelación de la membresía.
