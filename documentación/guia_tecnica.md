# Guía técnica de Nexum

## Temario

1. [Arquitectura y recorrido del sistema](#1-arquitectura-y-recorrido-del-sistema)
2. [Roles, identidad y autorización](#2-roles-identidad-y-autorización)
3. [Modelo de dominio y relaciones](#3-modelo-de-dominio-y-relaciones)
4. [Versiones y vigencias](#4-versiones-y-vigencias)
5. [Servicios y reglas de negocio](#5-servicios-y-reglas-de-negocio)
6. [Flujos operativos principales](#6-flujos-operativos-principales)
7. [Persistencia, consultas y mapeadores](#7-persistencia-consultas-y-mapeadores)
8. [Seguridad y excepciones](#8-seguridad-y-excepciones)
9. [Recorrido guiado del código](#9-recorrido-guiado-del-código)
10. [Glosario](#glosario)
11. [Anexos externos](#anexos-externos)

## 1. Arquitectura y recorrido del sistema

Nexum está organizado por capas. La interfaz de terminal inicia una operación,
los servicios coordinan las reglas de negocio, las clases representan el
dominio y `base_de_datos/` consulta o modifica MariaDB:

```text
Interfaz de terminal → Servicios → Clases del dominio
                     → Consultas y mapeadores → MariaDB
```

### Punto de entrada y navegación

`main.py` importa y ejecuta `ejecutar_aplicacion()` desde
`interfaz_term/ventana_inicio.py`. Esta función crea el diccionario de sesión,
mantiene el historial de pantallas y selecciona la función que debe mostrar la
siguiente pantalla.

La navegación comienza en `mostrar_bienvenida`, continúa con
`mostrar_login_con_volver` y, después de autenticar, entra en la interfaz de
`miembro` o de `usuario`. La sesión conserva una identidad neutral, pero no
almacena instancias de las entidades del dominio. Al cerrar sesión se eliminan
la identidad y el historial de navegación.

### Capas y responsabilidades

#### `interfaz_term/`

Contiene la interfaz de terminal, los componentes visuales y la navegación.
`questionary` obtiene entradas y selecciones; `rich` presenta paneles, tablas y
mensajes. Las pantallas convierten los formularios en diccionarios y llaman a
servicios. No deben decidir reglas como la vigencia de un plan o el saldo de
puntos.

Las pantallas principales son:

- `pantallas/inicio_sesion.py`: solicita credenciales y crea la identidad de sesión.
- `pantallas/miembro/principal.py`: consultas personales de información,
  membresía, beneficios, historial y solicitudes en tienda.
- `pantallas/usuario/principal.py`: operaciones de tienda, miembros,
  membresías, planes, recompensas, usuarios y ajustes según el rol.
- `componentes/formulario.py`, `mensajes.py` y `tabla.py`: reutilizan la
  interacción y la presentación.

### Librerías externas y su función técnica

Las dependencias externas utilizadas por el programa final aparecen en
`requirements.txt`. Cada una resuelve una responsabilidad concreta y se usa
desde una capa determinada:

- **Rich:** construye la presentación de terminal. `Console` imprime contenido,
  `Panel` organiza encabezados y mensajes, y `Table` muestra datos tabulares.
  La interfaz concentra estos componentes en módulos como
  `interfaz_term/componentes/tabla.py`, `mensajes.py` y las pantallas
  principales. Rich no consulta la base de datos ni decide permisos.
- **questionary:** proporciona controles interactivos para la terminal. Las
  pantallas usan `select` para menús y `text` para entradas; los formularios
  reutilizables agrupan varias preguntas y devuelven un `dict` que después
  recibe un servicio.
- **PyMySQL:** es el adaptador entre Python y MariaDB. La capa de persistencia
  abre conexiones, crea cursores, ejecuta consultas parametrizadas y obtiene
  filas como diccionarios mediante `DictCursor`.
- **bcrypt:** protege las contraseñas. `hashear_contraseña` genera un hash y
  `verificar_contraseña` compara una contraseña recibida contra el hash guardado,
  sin recuperar la contraseña original.

La librería no sustituye a la capa que la utiliza: `questionary` y Rich
pertenecen a la interacción, PyMySQL a la persistencia y bcrypt a la seguridad.
Los servicios permanecen entre esas capas para coordinar el comportamiento del
negocio.

#### `servicios/`

Contiene la lógica de aplicación que coordina varias entidades. Los servicios
reciben una identidad y datos de entrada, validan permisos y reglas, consultan
las entidades necesarias y delegan la persistencia en `base_de_datos/`.

Las responsabilidades se distribuyen así:

- `autenticacion/`: busca la identidad por correo y verifica la contraseña.
- `autorizacion/`: valida roles, autenticación y propiedad de una membresía.
- `miembro/` y `usuario/`: registran, consultan y modifican identidades.
- `plan/` y `recompensa/`: administran catálogos y sus versiones temporales.
- `membresia/`: contrata, renueva, cancela, suspende y reactiva membresías.
- `compra/`: calcula importes y genera movimientos de puntos y cashback.
- `caja/`: coordina una venta y un canje como una atención única.
- `ajuste/`: registra ajustes administrativos de puntos y cashback.

#### `clases/`

Contiene las clases del dominio: `Miembro`, `Usuario`, `Rol`, `Plan`,
`VersionPlan`, `Recompensa`, `VersionRecompensa`, `Membresia`, `Renovacion`,
`Compra`, `TransaccionPuntos` y `TransaccionCashback`. También contiene las
configuraciones de beneficios asociadas con `VersionPlan`.

Una clase conserva sus datos, relaciones e invariantes naturales. La lógica que
requiere coordinar varias clases pertenece a los servicios. Por ejemplo,
`Membresia` conserva el estado actual, pero `servicio_membresia.py` decide qué
versión debe aplicarse durante una renovación.

#### `base_de_datos/`

Es la capa de persistencia. `conexion.py` abre conexiones con PyMySQL,
`consultas.py` ejecuta SQL parametrizado y `mapeadores.py` transforma filas en
objetos del dominio. Las consultas también coordinan transacciones y traducen
errores conocidos de MariaDB a excepciones de dominio.

Los scripts `CREACIÓN_BD_NEXUM.sql`, `INSERTS_BD_NEXUM.sql` y
`REINICIAR_BD_NEXUM.sql` contienen, respectivamente, la creación del esquema,
la carga de datos y el reinicio de la base de datos.

#### `utilidades/`

`utilidades/seguridad.py` encapsula el hash y la verificación de contraseñas con
`bcrypt`. `utilidades/excepciones.py` concentra las excepciones compartidas por
los servicios, evitando que cada módulo defina su propio contrato de errores.

### Recorrido de una operación

En una compra, `mostrar_operaciones_tienda` recopila los datos y llama a
`registrar_operacion_caja`. El servicio de caja invoca a
`registrar_compra`, que autoriza al operador, obtiene la membresía, actualiza
su estado y calcula descuentos, puntos y cashback. Después solicita a
`base_de_datos.consultas` guardar la compra y sus transacciones. Las consultas
usan `mapeadores.py` al reconstruir objetos y MariaDB conserva los registros.

### Resumen de sección

- **Interfaz:** captura entradas, muestra resultados y controla la navegación.
- **Servicios:** coordinan casos de uso, permisos y reglas de negocio.
- **Clases:** representan entidades, relaciones e invariantes del dominio.
- **Persistencia:** ejecuta SQL, administra transacciones y mapea resultados.
- **Utilidades:** centralizan seguridad y errores compartidos.

**Anexo externo:** incluir un diagrama de arquitectura que muestre el recorrido
desde `interfaz_term/` hasta MariaDB y el sentido de las dependencias entre
capas.

## 2. Roles, identidad y autorización

### Roles administrativos

`Administrador`, `Cajero` y `Gerente de Sucursal` son valores de `Rol` asignados
a un `Usuario`. `Miembro` no es un rol administrativo: es una entidad
independiente que representa a quien consulta sus propios datos y beneficios.

- **Administrador:** puede administrar usuarios, miembros, planes,
  recompensas, operaciones de tienda, informes y ajustes.
- **Cajero:** puede atender operaciones presenciales: registrar miembros,
  ventas, contrataciones, renovaciones, cambios de plan, cashback y canjes. No
  administra catálogos, usuarios, ajustes administrativos ni informes.
- **Gerente de Sucursal:** puede operar en tienda, administrar miembros y
  membresías, consultar actividad y ejecutar ajustes. Puede consultar planes y
  recompensas, pero no administrar usuarios ni configurar esos catálogos.

Los códigos de rol que reconoce `servicio_autorizacion.py` son `ADM`, `CAJ` y
`GER`; las comprobaciones también aceptan el nombre del rol sin distinguir
mayúsculas y minúsculas.

### Identidad neutral

La autenticación no entrega a la interfaz una entidad completa. Devuelve un
diccionario con un formato común:

```python
{"tipo": "usuario", "num": 12, "nombre": "Ana", "rol": "CAJ"}
```

Para un miembro, `tipo` es `miembro` y se conservan `num` y `nombre`. Para un
usuario administrativo se agregan `rol` y `rol_nombre`. Esta identidad es el
primer argumento de las operaciones protegidas, por ejemplo
`registrar_compra(identidad, datos)`.

La separación es importante:

- **Autenticación:** `autenticar_miembro` o `autenticar_usuario` comprueban que
  las credenciales corresponden a una identidad.
- **Autorización:** `servicio_autorizacion.py` vuelve a resolver la entidad y
  comprueba que el rol, el tipo de identidad y el estado permiten la operación.

### Protección de la información personal

Cuando una identidad de tipo `miembro` consulta un registro, los servicios
comparan `identidad["num"]` con el número solicitado. Si no coinciden, se
lanza `OperacionNoPermitida`. Para consultar una membresía o actividad también
se valida que la membresía pertenezca al miembro autenticado. Un usuario
administrativo pasa por las comprobaciones de rol correspondientes.

### Matriz de acceso

| Rol o identidad | Operaciones permitidas | Operaciones restringidas |
|---|---|---|
| Administrador | Configuración, usuarios, miembros, tienda, informes y ajustes | Ninguna dentro de las reglas de autorización actuales |
| Cajero | Miembros, contrataciones, renovaciones, cambios de plan, ventas, cashback y canjes | Configurar catálogos, administrar usuarios, ajustes e informes administrativos |
| Gerente de Sucursal | Tienda, miembros, membresías, actividad, ajustes y consulta de catálogos | Administrar usuarios y configurar planes o recompensas |
| Miembro | Consultar sus datos, membresía, puntos, recompensas e historiales; solicitar atención en tienda | Consultar o modificar información de otro miembro; ejecutar directamente renovaciones, cancelaciones o canjes |

### Resumen de sección

- `Usuario` representa una identidad administrativa y siempre debe tener un `Rol`.
- `Miembro` es una identidad de negocio separada de los roles administrativos.
- La identidad neutral desacopla la sesión de las entidades completas.
- La autorización se aplica dentro de los servicios, no solo en los menús.

## 3. Modelo de dominio y relaciones

### Identidad

`Miembro` contiene los datos y credenciales de una persona participante.
`Usuario` contiene los datos y credenciales de una persona administrativa y
referencia un `Rol`. `Rol` identifica el conjunto de permisos de esa persona.

La autenticación localiza `Miembro` o `Usuario` por correo. La sesión solo
conserva la identidad neutral; los servicios vuelven a consultar la entidad
cuando deben autorizar o ejecutar una operación.

### Configuración de planes

`Plan` es la identidad base de un producto comercial. `VersionPlan` contiene
las condiciones que se pueden contratar durante un periodo: precio, plazo,
tipo de aplicación y configuraciones de descuento, puntos y cashback.

Las configuraciones asociadas son `ConfigPuntos`, `ConfigDescuento`,
`ConfigCashback` y `DiaAplicableDesc`. Una configuración de descuento puede
limitarse a un importe mínimo y a determinados días de la semana.

### Recompensas

`Recompensa` es la identidad base del beneficio que se puede canjear.
`VersionRecompensa` define, para un periodo, su costo en puntos y su límite de
canjes. Un canje no requiere una entidad adicional: se conserva como una
`TransaccionPuntos` negativa vinculada a la versión de recompensa.

### Participación

`Membresia` vincula un `Miembro` con su participación actual y conserva su
estado (`ACTIVA`, `SUSPENDIDA` o `CANCELADA`) y su `version_plan_actual`.
`Renovacion` registra cada periodo contratado, la versión comprada, el importe
y las fechas del periodo. Por eso una membresía puede conservar varios
periodos históricos mediante sus renovaciones.

### Operaciones y movimientos

`Compra` vincula una operación con una `Membresia` y el `Usuario` que la
registró. Guarda los importes calculados, no solo el monto original.

`TransaccionPuntos` representa movimientos positivos o negativos de puntos y
guarda el saldo resultante. Puede referenciar una `Compra` o una
`VersionRecompensa`. `TransaccionCashback` aplica el mismo principio a un
saldo monetario de cashback.

### Resumen de sección

- `Miembro` y `Usuario` son identidades distintas; `Usuario` referencia `Rol`.
- `Plan` y `Recompensa` son identidades base.
- `VersionPlan` y `VersionRecompensa` contienen condiciones temporales.
- `Membresia` conecta un miembro con el plan actual.
- `Renovacion`, `Compra` y las transacciones conservan la historia operativa.

**Anexo externo:** incluir un diagrama de clases y relaciones que muestre las
referencias entre identidad, versiones, membresías, renovaciones, compras y
movimientos.

## 4. Versiones y vigencias

### Entidad base y condición temporal

`Plan` identifica un producto y conserva sus características generales, como
nombre y descripción. No contiene el precio que necesariamente se aplicará en
una operación concreta. Ese precio, el plazo y los beneficios se encuentran en
una `VersionPlan`.

Del mismo modo, `Recompensa` identifica el beneficio, mientras que
`VersionRecompensa` define cuánto cuesta y durante qué periodo puede canjearse.

Una versión no es una copia reemplazable de la entidad base. Es un registro de
condiciones comerciales aplicables a un intervalo. Al guardar la versión usada
en una renovación, compra o canje, el sistema puede reconstruir qué condiciones
produjeron el resultado histórico.

### Fechas y vigencia

Cada versión tiene `fecha_inicio` y `fecha_final`. El método `esta_vigente()`
considera vigente una versión cuando la fecha consultada se encuentra dentro
del intervalo, incluidos sus extremos. Las versiones rechazan una fecha final
anterior a la inicial.

`finalizar_vigencia()` puede acortar la disponibilidad sin cambiar el precio,
el costo ni las configuraciones. Para cambiar condiciones se crea otra versión.
Una nueva condición no debe alterar retroactivamente operaciones que ya fueron
registradas.

### Versiones regulares y promociones

Una versión regular de plan no tiene `version_base_de_promo`. Las versiones
promocionales sí referencian una versión regular del mismo `Plan` mediante
`version_base_de_promo`.

Las promociones deben permanecer dentro de las fechas de su versión regular y
no pueden basarse en otra promoción. Pueden distinguirse por `aplica_en`:
`CONTRATACION`, `RENOVACION` o `AMBAS`. Las condiciones regulares se crean para
`AMBAS` y no pueden solaparse entre sí.

Para una recompensa solo puede existir una versión vigente por recompensa
base. Las versiones de recompensa tampoco pueden solaparse.

### Validación de solapamientos

`servicio_plan.py` valida que:

1. Las fechas sean válidas y estén ordenadas.
2. Las condiciones regulares no se solapen.
3. Una promoción pertenezca al mismo plan que su versión base.
4. Una promoción quede completamente dentro de la vigencia regular.
5. Las promociones del mismo tipo no ocupen el mismo periodo.

`servicio_recompensa.py` aplica las mismas validaciones generales de fechas y
rechaza cualquier periodo que se solape con una versión de la misma recompensa.

### Selección de una versión

En contratación, `contratar_membresia` recibe el número de una versión y
comprueba que esté vigente y permita `CONTRATACION` o `AMBAS`. En una renovación,
`renovar_membresia` realiza la comprobación equivalente para `RENOVACION` o
`AMBAS`.

Las versiones seleccionables para operaciones se obtienen mediante
`obtener_versiones_plan_para_operacion`. Al consultar una recompensa para un
canje, caja obtiene una única versión vigente; si no existe o hay más de una,
la operación se rechaza. El canje vuelve a validar la vigencia antes de crear
el movimiento.

### Resumen de sección

| Elemento | Función | Puede cambiar sin perder historial |
|---|---|---|
| `Plan` o `Recompensa` | Identidad base del catálogo | Sí, en sus datos generales permitidos |
| `VersionPlan` | Condiciones comerciales de un plan en un intervalo | No; solo puede finalizarse su vigencia |
| `VersionRecompensa` | Costo y disponibilidad de una recompensa en un intervalo | No; solo puede finalizarse su vigencia |
| Nueva versión | Sustituye condiciones para un periodo posterior | Se crea sin modificar las operaciones anteriores |

## 5. Servicios y reglas de negocio

Los servicios son la frontera de los casos de uso. Una función de servicio
recibe una identidad y datos simples, valida el contexto, obtiene las entidades
que necesita, coordina la operación y llama a las consultas de persistencia.
No modifica estructuras internas de persistencia ni ejecuta SQL directamente.

### Servicios principales

- `servicio_autenticacion.py` valida datos no vacíos, busca por correo y usa
  `verificar_contraseña`.
- `servicio_autorizacion.py` resuelve el usuario o miembro asociado a la
  identidad y ofrece comprobaciones reutilizables como
  `requiere_administrador`, `requiere_operador_tienda` y
  `requiere_administrador_o_propietario`.
- `servicio_miembro.py` hashea contraseñas al registrar o modificar miembros y
  protege las consultas por propiedad.
- `servicio_plan.py` y `servicio_recompensa.py` controlan catálogos, versiones,
  vigencias, solapamientos, costos y límites.
- `servicio_membresia.py` coordina periodos, estados, contratación y renovación.
- `servicio_compra.py` calcula importes y registra beneficios derivados.
- `servicio_caja.py` agrupa una venta y un canje en una operación atómica.
- `servicio_ajuste.py` registra movimientos manuales autorizados y evita saldos
  negativos.

### Reglas de negocio relevantes

| Regla | Servicio responsable | Entidades afectadas |
|---|---|---|
| La identidad debe tener el tipo y rol adecuados | `autorizacion` | `Usuario`, `Rol`, `Miembro` |
| Solo una identidad puede consultar su propia información | `miembro`, `membresia`, `compra`, `recompensa` | `Miembro`, `Membresia`, movimientos |
| La versión elegida debe estar vigente y aplicar al caso | `plan`, `recompensa`, `membresia` | `VersionPlan`, `VersionRecompensa` |
| Las condiciones históricas no se reemplazan | `plan`, `recompensa` | Versiones y operaciones históricas |
| Una renovación anticipada inicia después del periodo vigente | `membresia` | `Renovacion`, `Membresia` |
| Una membresía vencida se suspende y luego puede cancelarse | `membresia` | `Membresia`, `Renovacion` |
| Una compra exige membresía activa | `compra` | `Compra`, `Membresia` |
| El descuento se aplica antes del cashback utilizado | `compra` | `Compra`, `VersionPlan` |
| Los puntos se truncan a entero y el dinero se redondea a dos decimales | `compra` | `Compra`, `TransaccionPuntos`, `TransaccionCashback` |
| El canje exige saldo y respeta el límite por versión | `recompensa` | `TransaccionPuntos`, `VersionRecompensa` |
| Las operaciones compuestas se confirman o revierten completas | `caja` y `base_de_datos.consultas` | Compra, canje y transacciones |

### Beneficios, puntos y cashback

En una compra, `servicio_compra.py` convierte importes a `Decimal`, aplica el
descuento si se cumple el monto mínimo y el día aplicable, resta el cashback
utilizado y redondea el resultado con `ROUND_HALF_UP`.

Los puntos se calculan sobre el monto final y se truncan a entero. La vigencia
se calcula desde la última compra que generó puntos y la cantidad de meses de
`ConfigPuntos`. Si el saldo vence, se registra un movimiento negativo de
expiración.

El cashback generado se calcula sobre el monto final. El cashback utilizado se
valida contra el saldo disponible y no puede superar el monto de la compra. Si
el importe generado durante un mes no supera el umbral configurado, al cerrar
ese mes puede registrarse su expiración como movimiento negativo.

### Resumen de sección

Los servicios concentran reglas que atraviesan varias entidades. Las clases
aportan datos e invariantes propios; la persistencia guarda el resultado; la
interfaz no debe duplicar estas decisiones.

## 6. Flujos operativos principales

### 6.1 Autenticación de un miembro o usuario administrativo

1. El actor elige el tipo de acceso en `mostrar_bienvenida`.
2. `mostrar_login_con_volver` solicita correo y contraseña.
3. `autenticar_miembro` o `autenticar_usuario` rechaza campos vacíos.
4. El servicio consulta la entidad por correo y verifica el hash con bcrypt.
5. Si las credenciales son válidas, devuelve una identidad neutral.
6. `ventana_inicio.py` dirige al menú de miembro o de usuario.

El miembro inicia el flujo para consultar su información. El usuario
administrativo inicia el flujo para acceder a operaciones permitidas por su
rol. No se crean entidades ni registros históricos.

### 6.2 Registro y contratación inicial

1. Un Administrador, Gerente o Cajero inicia el registro desde operaciones de
   tienda.
2. `registrar_miembro` comprueba correo único y hashea la contraseña.
3. `contratar_membresia` valida que el miembro exista y que la versión esté
   vigente y permita contratación.
4. Si existe una membresía no cancelada, se rechaza la contratación.
5. Se crea una `Membresia` activa con la versión seleccionada.
6. Se crea una `Renovacion` para registrar el pago y el primer periodo.

La contratación inicial usa `Renovacion` y no se asocia a una `Compra`.

### 6.3 Renovación o cambio diferido de plan

1. Un operador de tienda selecciona la membresía y una versión aplicable a
   renovación.
2. `renovar_membresia` rechaza membresías canceladas y versiones no vigentes.
3. El servicio calcula el inicio: el día posterior al último periodo si la
   membresía aún tiene cobertura, o el día del pago si ya terminó.
4. Calcula el final a partir del plazo de la versión.
5. Registra una `Renovacion` con las fechas y el monto.
6. Si el nuevo periodo comienza de inmediato, actualiza la versión y el estado;
   si es anticipado, la membresía actual no se sustituye hasta que corresponda.

El resultado histórico es la nueva renovación; las anteriores permanecen.

### 6.4 Actualización del estado de una membresía

1. Una consulta u operación obtiene la membresía.
2. `actualizar_estado_membresia` determina el periodo aplicable a la fecha.
3. Durante el periodo, activa la versión correspondiente.
4. Después del final del periodo, cambia el estado a `SUSPENDIDA`.
5. Si transcurre el mes de suspensión sin renovación, cambia a `CANCELADA`.
6. Guarda la membresía cuando el estado o la versión cambian.

No hay un proceso externo en segundo plano: la actualización se produce al
consultar u operar la membresía.

### 6.5 Registro de una compra

1. Un Administrador, Cajero o Gerente inicia la operación en caja.
2. `registrar_compra` autoriza al usuario y abre una transacción.
3. Obtiene la membresía, actualiza estado y vigencia de puntos, y exige estado
   `ACTIVA`.
4. Valida el monto, calcula descuento y valida el cashback aplicado.
5. Crea y guarda `Compra` con los importes resultantes.
6. Genera `TransaccionPuntos` y `TransaccionCashback` cuando las configuraciones
   del plan corresponden.
7. Confirma la transacción; cualquier error provoca rollback.

### 6.6 Generación y consulta de puntos

1. Una compra activa la configuración de puntos del plan.
2. El servicio calcula los puntos sobre `monto_final` y trunca el resultado.
3. Guarda un movimiento positivo con su saldo acumulado y referencia a la compra.
4. Al consultar, `obtener_transacciones_de_miembro` valida la propiedad y
   actualiza la vigencia.
5. El saldo se obtiene del último movimiento ordenado por fecha y número de
   transacción.

### 6.7 Generación, desbloqueo y uso de cashback

1. Una compra genera cashback sobre el monto final si el plan lo configura.
2. Si se usa cashback, el servicio valida configuración, importe y saldo.
3. Registra primero el movimiento negativo por el importe aplicado.
4. Registra después el cashback generado por la misma compra.
5. La consulta del saldo devuelve el saldo del último movimiento ordenado.
6. El umbral mensual se evalúa al intentar usarlo; al superar el umbral se
   habilita lo generado en ese mes.

### 6.8 Canje de una recompensa

1. Un Administrador, Cajero o Gerente inicia el canje en caja; el miembro solo
   puede solicitarlo desde su interfaz.
2. `servicio_caja.py` localiza una única versión vigente por código.
3. `validar_canje` actualiza estado y vigencia de puntos y exige membresía activa.
4. Comprueba vigencia, límite de canjes y saldo suficiente.
5. `canjear_recompensa` crea una `TransaccionPuntos` negativa con la recompensa
   y, si corresponde, la compra de la misma atención.
6. Caja confirma venta y canje juntos o revierte ambos.

### Resumen de sección

| Flujo | Actor que lo inicia | Servicio coordinador | Resultado principal |
|---|---|---|---|
| Autenticación | Miembro o usuario | `autenticacion` | Identidad neutral en sesión |
| Contratación | Operador de tienda | `membresia` | `Membresia` y `Renovacion` |
| Renovación | Operador de tienda | `membresia` | Nuevo periodo histórico |
| Estado | Consulta u operación | `membresia` | Estado y versión actualizados |
| Compra | Operador de tienda | `caja` y `compra` | `Compra` y movimientos de beneficios |
| Puntos | Compra o consulta | `compra` | Movimientos y saldo derivado |
| Cashback | Compra o caja | `compra` | Movimientos monetarios y saldo |
| Canje | Operador de tienda | `caja` y `recompensa` | Movimiento negativo de puntos |

**Anexo externo:** incluir diagramas separados para compra, renovación y canje.
Cada diagrama debe mostrar actor, validaciones, servicios, entidades afectadas
y punto de confirmación o rollback.

## 7. Persistencia, consultas y mapeadores

### Conexión con MariaDB

`base_de_datos/conexion.py` define `obtener_conexion()`. Lee las variables
`NEXUM_DB_USUARIO`, `NEXUM_DB_CONTRASENA`, `NEXUM_DB_NOMBRE` y
`NEXUM_DB_SOCKET`. La conexión usa `PyMySQL`, `utf8mb4`, cursores
`DictCursor` y `autocommit=False`.

El uso de `autocommit=False` permite que una operación compuesta confirme todos
los cambios mediante `commit()` o los descarte con `rollback()`.

### API interna de persistencia

En este proyecto, la palabra **API** se refiere al conjunto de funciones Python
que `base_de_datos/consultas.py` ofrece a los servicios. No es una API HTTP ni
un servicio separado: es una interfaz interna que oculta los detalles de SQL,
conexiones, cursores y mapeadores.

El recorrido de una operación es:

```text
Servicio → base_de_datos.consultas → PyMySQL → MariaDB
```

Por ejemplo, un servicio no construye un `SELECT` para buscar un miembro. Usa
la función de la API que corresponde:

```python
miembro = bd.buscar_miembro_por_num(num_miembro)
```

La función recibe un identificador, ejecuta internamente una consulta
parametrizada, aplica `mapear_miembro` y devuelve un `Miembro` o `None`. El
servicio trabaja con el objeto Python y no con la fila SQL.

### Operaciones de lectura

Las funciones de lectura siguen nombres que expresan la intención de la
consulta:

```python
miembro = bd.buscar_miembro_por_correo(correo)
version = bd.buscar_version_plan_por_num(num_version)
compras = bd.obtener_compras_de_membresia(num_membresia)
transacciones = bd.obtener_transacciones_de_miembro(num_miembro)
```

Sus resultados tienen un contrato sencillo:

- `buscar_*` devuelve una entidad o `None` si no existe.
- `obtener_*` devuelve una lista, que puede estar vacía.
- Las consultas relacionadas reconstruyen los objetos conectados. Una compra,
  por ejemplo, puede incluir su membresía y usuario mediante consultas y
  mapeadores adicionales.

El servicio debe validar el resultado. Que una función devuelva `None` no
significa que la operación de negocio sea válida; normalmente el servicio lo
convierte en `EntidadNoEncontrada` cuando la entidad era obligatoria.

### Operaciones de escritura

Las funciones `guardar_*` reciben objetos del dominio ya validados por el
servicio:

```python
bd.guardar_miembro(miembro)
bd.guardar_compra(compra)
bd.guardar_transaccion_puntos(transaccion)
```

Si el objeto tiene `num=None`, la consulta ejecuta un `INSERT` y asigna el
identificador generado. Si ya tiene identificador, la función ejecuta un
`UPDATE` cuando ese tipo de entidad lo permite. La función de guardado no
calcula descuentos, decide permisos ni selecciona versiones: esas decisiones
pertenecen al servicio.

### De SQL directo a la API Python

Una consulta SQL directa como esta:

```sql
SELECT * FROM miembro WHERE correo = %s;
```

se encapsula en una función como `buscar_miembro_por_correo(correo)`. Dentro de
`consultas.py`, el cursor recibe la sentencia y sus valores por separado:

```python
cursor.execute(
    "SELECT * FROM miembro WHERE correo = %s",
    (correo,),
)
```

El marcador `%s` no se reemplaza mediante concatenación de texto. PyMySQL
envía la sentencia y los parámetros de forma separada, lo que evita construir
SQL con datos externos. Por esta razón, los servicios deben pasar valores a
las funciones de la API y no insertar esos valores dentro de una cadena SQL.

Para una persona que conoce SQL, la equivalencia conceptual es:

| SQL directo | API de `base_de_datos.consultas` |
|---|---|
| `SELECT` de un miembro por número | `buscar_miembro_por_num(num)` |
| `SELECT` de todos los planes | `obtener_todos_los_planes()` |
| `SELECT` de compras por membresía | `obtener_compras_de_membresia(num_membresia)` |
| `INSERT` o `UPDATE` de una compra | `guardar_compra(compra)` |
| `INSERT` de un movimiento de puntos | `guardar_transaccion_puntos(transaccion)` |
| `COMMIT` o `ROLLBACK` de varias escrituras | `with bd.transaccion():` |

La API agrega dos pasos que una consulta SQL aislada no proporciona: convierte
filas en objetos del dominio y conserva las relaciones entre esos objetos.

### Cursores y parámetros

El cursor se crea dentro de `consultas.py` con `conexion.cursor()`. Se usa como
contexto para garantizar su cierre:

```python
with conexion.cursor() as cursor:
    cursor.execute(consulta, parametros)
    fila = cursor.fetchone()
```

Los servicios no reciben conexiones ni cursores. Esta decisión evita que una
función de negocio mezcle reglas con detalles de PyMySQL y permite cambiar la
consulta interna sin cambiar la llamada del servicio.

### Transacciones desde la API

Cuando una sola escritura es suficiente, `_usar_conexion()` abre una conexión,
ejecuta la operación y hace `commit()` al terminar. Si ocurre una excepción,
hace `rollback()` y traduce los errores SQL conocidos.

Cuando un caso de uso necesita varias escrituras, el servicio usa:

```python
with bd.transaccion():
    bd.guardar_compra(compra)
    bd.guardar_transaccion_puntos(transaccion)
```

`transaccion()` mantiene la conexión en un `ContextVar`. Las llamadas internas a
`_usar_conexion()` reutilizan esa conexión en lugar de confirmar cada escritura
por separado. Si todo termina bien se hace un solo `commit()`; si falla una
parte, se hace un solo `rollback()`.

### Consultas y transacciones

`base_de_datos/consultas.py` es la única capa que ejecuta SQL. Las funciones
buscan, guardan y eliminan entidades, siempre con parámetros separados de las
consultas. También resuelven relaciones: por ejemplo, una versión de plan
recupera su plan y sus configuraciones antes de mapearse.

`_usar_conexion()` abre una conexión cuando la operación es independiente,
confirma al terminar correctamente y revierte ante una excepción. El contexto
`transaccion()` permite que varios servicios compartan una misma conexión.
Esto es lo que usa caja para garantizar que una venta y un canje no queden en
un estado parcial.

### Mapeadores

Un mapeador convierte una fila o conjunto de filas de MariaDB en una instancia
de una clase del dominio. Por ejemplo, `mapear_miembro` toma las columnas de
una fila y construye `Miembro`; `mapear_version_plan` combina la fila de la
versión con el `Plan` y sus configuraciones ya recuperadas.

El recorrido de lectura es:

```text
Fila SQL → consulta relacionada → mapeador → objeto del dominio
```

El recorrido de escritura es inverso en responsabilidad, aunque no existe un
serializador genérico único:

```text
Objeto del dominio → consulta guardar_* → parámetros SQL → fila MariaDB
```

Por ejemplo, `guardar_compra` recibe una `Compra` con sus importes calculados,
la inserta mediante una consulta parametrizada y conserva el número generado
para relacionar sus movimientos de puntos y cashback.

### Errores de persistencia

`_traducir_error_sql` convierte códigos conocidos de MariaDB. Una clave única
duplicada se traduce a `DatosInvalidos`; una restricción de clave foránea o
historial relacionado se traduce a `EntidadNoEncontrada` u
`OperacionNoPermitida`; otros errores se encapsulan como `ErrorPersistencia`.

Los servicios no deben ejecutar SQL directamente porque eso duplicaría reglas,
rompería la gestión de transacciones y mezclaría el modelo de negocio con los
detalles del esquema. Tampoco deben modificar estructuras internas de
persistencia: deben usar las funciones de `consultas.py`.

### Scripts de base de datos

- `CREACIÓN_BD_NEXUM.sql` define tablas, relaciones y restricciones.
- `INSERTS_BD_NEXUM.sql` carga registros iniciales o de prueba.
- `REINICIAR_BD_NEXUM.sql` permite reconstruir la base conforme al esquema y
  los datos definidos por el proyecto.

### Resumen de sección

- **Conexión:** abre MariaDB con la configuración del entorno.
- **Consulta:** ejecuta SQL y coordina objetos relacionados.
- **Mapeador:** traduce filas a entidades del dominio.
- **Transacción:** agrupa cambios y decide `commit` o `rollback`.
- **Servicio:** usa consultas, pero no conoce ni ejecuta SQL directamente.

## 8. Seguridad y excepciones

### Contraseñas y credenciales

`hashear_contraseña` genera hashes con `bcrypt.gensalt()` y nunca guarda la
contraseña en texto plano durante el registro o la modificación. La
autenticación usa `verificar_contraseña`, que llama a `bcrypt.checkpw` y
devuelve `False` para tipos inválidos o hashes mal formados.

`autenticar_miembro` y `autenticar_usuario` rechazan correo o contraseña vacíos.
Si la búsqueda no encuentra una entidad o la contraseña no coincide, devuelven
`None` sin revelar cuál de los dos datos falló.

### Clases de errores

| Excepción | Situación que representa |
|---|---|
| `ErrorDominio` | Base común de errores esperados por las reglas de negocio |
| `ErrorPersistencia` | Error técnico no expuesto directamente por MariaDB |
| `DatosInvalidos` | Entrada que no cumple el contrato o las restricciones |
| `EntidadNoEncontrada` | Registro solicitado que no existe; hereda de `DatosInvalidos` |
| `OperacionNoPermitida` | Identidad, estado o relación que impide la operación |
| `VersionNoVigente` | Versión fuera del periodo aplicable |
| `SaldoInsuficiente` | Puntos o cashback insuficientes; hereda de `OperacionNoPermitida` |
| `LimiteExcedido` | Límite de canjes o importe superado |

La compatibilidad con `ValueError` y `PermissionError` permite que la interfaz
term responda a errores de entrada y permisos mientras los servicios mantienen
excepciones semánticas más específicas.

### Resumen de sección

La seguridad combina hashes bcrypt, identidad neutral, autorización dentro de
los servicios, validación de propiedad y errores separados por causa. La
interfaz puede mostrar el mensaje, pero no debe sustituir las comprobaciones
del servicio.

## 9. Recorrido guiado del código

El siguiente recorrido sigue una operación de caja que registra una venta y,
opcionalmente, un canje.

1. `main.py` ejecuta `ejecutar_aplicacion()`.
2. `interfaz_term/ventana_inicio.py` crea `sesion`, muestra la bienvenida y
   dirige el historial de pantallas.
3. Después del login, `interfaz_term/pantallas/usuario/principal.py` muestra
   `mostrar_operaciones_tienda` y recopila el número de membresía, monto y
   cashback.
4. La pantalla llama a `registrar_operacion_caja` en
   `servicios/caja/servicio_caja.py`.
5. Caja llama a `requiere_operador_tienda` para verificar que la identidad sea
   Administrador, Cajero o Gerente de Sucursal.
6. Si hay canje, caja obtiene la recompensa vigente y ejecuta
   `validar_canje` antes de abrir la operación principal.
7. Dentro de `bd.transaccion()`, caja llama a `registrar_compra` en
   `servicios/compra/servicio_compra.py`.
8. Compra carga la membresía mediante `bd.buscar_membresia_por_num`, invoca
   `actualizar_estado_membresia` y valida que esté activa.
9. Compra calcula descuento con la configuración de `VersionPlan`, aplica el
   cashback solicitado y crea `Compra`.
10. `bd.guardar_compra` persiste la compra. Luego se crean movimientos mediante
    `bd.guardar_transaccion_puntos` y `bd.guardar_transaccion_cashback`.
11. Si existe canje, `canjear_recompensa` crea un movimiento negativo de
    `TransaccionPuntos` relacionado con la compra.
12. `base_de_datos/consultas.py` confirma con `commit()` si todos los pasos
    terminan bien. Ante un error ejecuta `rollback()` y traduce el error si
    corresponde.
13. La interfaz recibe el resultado y presenta la compra, el canje o el
    mensaje de error.

### Mapa de archivos y funciones

| Archivo | Funciones o elementos visitados | Responsabilidad en el recorrido |
|---|---|---|
| `main.py` | `ejecutar_aplicacion` | Arranque |
| `interfaz_term/ventana_inicio.py` | `ejecutar_menu` | Navegación y sesión |
| `interfaz_term/pantallas/usuario/principal.py` | `mostrar_operaciones_tienda` | Captura de datos |
| `servicios/caja/servicio_caja.py` | `registrar_operacion_caja` | Coordina venta y canje |
| `servicios/autorizacion/servicio_autorizacion.py` | `requiere_operador_tienda` | Control de rol |
| `servicios/compra/servicio_compra.py` | `registrar_compra` | Beneficios y compra |
| `servicios/recompensa/servicio_recompensa.py` | `validar_canje`, `canjear_recompensa` | Validación y movimiento de canje |
| `base_de_datos/consultas.py` | `transaccion`, `guardar_compra`, `guardar_transaccion_*` | SQL, commit y rollback |
| `base_de_datos/mapeadores.py` | `mapear_*` | Reconstrucción de objetos |
| `base_de_datos/conexion.py` | `obtener_conexion` | Conexión PyMySQL |

### Resumen de sección

La interfaz inicia el caso de uso, pero la decisión de negocio ocurre en los
servicios. Las consultas son la única frontera SQL y la transacción de caja
mantiene consistentes la compra, el canje y sus movimientos derivados.

## Glosario

- **Identidad neutral:** diccionario de sesión con tipo, número y datos mínimos;
  permite que los servicios autoricen sin acoplar la interfaz a una entidad.
- **Servicio de aplicación:** módulo que coordina un caso de uso que involucra
  varias entidades y persistencia.
- **Mapeador:** función que convierte filas de MariaDB en objetos del dominio.
- **Persistencia:** almacenamiento y recuperación de entidades en MariaDB.
- **Vigencia:** pertenencia de una fecha al intervalo entre inicio y final de
  una versión.
- **Versión temporal:** registro inmutable de condiciones comerciales para un
  periodo específico.
- **Operación atómica:** conjunto de cambios que se confirma completo o se
  revierte completo.
- **Saldo derivado de movimientos:** valor obtenido del saldo guardado en el
  último movimiento ordenado por fecha y número.
- **Inmutabilidad de condiciones:** regla que impide sustituir las condiciones
  de una versión ya creada; un cambio requiere otra versión.

## Anexos externos

Los siguientes diagramas deben mantenerse fuera de este documento y referenciar
esta guía:

- **Diagrama de arquitectura:** complementa la sección 1 y permite observar el
  flujo entre interfaz, servicios, dominio, consultas, mapeadores y MariaDB.
- **Diagrama de clases y relaciones:** complementa la sección 3 y permite
  observar identidades, versiones, membresías, operaciones y movimientos.
- **Diagrama del flujo de compra:** complementa la sección 6.5 y debe mostrar
  validaciones, cálculo de beneficios y persistencia atómica.
- **Diagrama del flujo de renovación:** complementa la sección 6.3 y debe
  mostrar el periodo vigente, el inicio diferido y el registro histórico.
- **Diagrama del flujo de canje:** complementa la sección 6.8 y debe mostrar la
  selección de versión vigente, la validación de saldo y el movimiento negativo.
