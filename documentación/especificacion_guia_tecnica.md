# Especificación para la guía técnica

> **Tipo de documento:** Pendiente

## Propósito

Definir cómo debe redactarse una guía técnica de Nexum para que los integrantes
del equipo puedan estudiar el código y preparar una exposición ante profesores.
La guía debe explicar el funcionamiento actual del proyecto con claridad y de
forma concisa, sin convertirse en una referencia exhaustiva de cada archivo o
función.

Este documento sirve como instrucción para un agente de IA encargado de crear o
mantener la guía técnica.

## Alcance de la guía

La guía debe describir únicamente el estado actual que pueda verificarse en el
código y en la documentación vigente del proyecto. Debe concentrarse en:

- La arquitectura implementada.
- Las responsabilidades de cada capa.
- Las entidades y relaciones relevantes.
- Los servicios y sus reglas de negocio.
- Los flujos principales de operación.
- La persistencia y el mapeo entre MariaDB y los objetos Python.
- La autenticación, autorización y control de acceso.
- Los conceptos técnicos menos evidentes para un integrante del equipo.

No debe incluir funcionalidades descartadas, trabajo pendiente, planes futuros
ni diferencias históricas del proyecto.

## Criterios de redacción

- Escribir en español.
- Usar los nombres reales de clases, módulos, funciones y carpetas.
- Explicar decisiones técnicas y relaciones entre componentes, no conceptos
  básicos que un miembro del equipo ya conoce.
- Evitar definiciones intuitivas de términos como miembro, compra o membresía.
- Priorizar ejemplos de flujo y relaciones causa-efecto sobre listados extensos
  de atributos.
- No explicar cada línea de código.
- Distinguir claramente entre una entidad, un servicio, una consulta y una
  operación de interfaz.
- No inventar clases, roles, servicios o comportamientos que no estén presentes
  en el proyecto actual.
- Cuando exista una ambigüedad entre documentación y código, verificar primero
  el código y describir el comportamiento implementado.

## Orden de la guía

La guía debe poder estudiarse de principio a fin sin un plan de estudio externo.
Las secciones deben aparecer en este orden:

### 1. Arquitectura y recorrido del sistema

Explicar las capas actuales y el recorrido de una operación desde la interfaz
hasta la base de datos:

```text
Interfaz de terminal → Servicios → Clases del dominio
                    → Consultas y mapeadores → MariaDB
```

Describir las responsabilidades de `clases/`, `servicios/`,
`base_de_datos/`, `interfaz_term/` y `utilidades/`. Relacionar esta explicación
con los archivos principales del proyecto.

**Resumen de sección:** incluir una lista breve de las capas y la responsabilidad
principal de cada una.

**Anexo externo:** indicar aquí la inclusión de un diagrama de arquitectura,
pero no dibujarlo dentro de la guía.

### 2. Roles, identidad y autorización

Explicar los tres perfiles actuales:

- **Administrador:** acceso completo a la configuración, gestión, operaciones,
  informes y ajustes autorizados.
- **Cajero:** operaciones necesarias para la atención en tienda, sin administrar
  la configuración general ni ejecutar ajustes administrativos.
- **Gerente de Sucursal:** acceso a las operaciones de tienda, miembros,
  membresías, actividad y ajustes definidos para su rol; consulta planes y
  recompensas, pero no administra usuarios ni configura esos catálogos.

Explicar que Administrador, Cajero y Gerente de Sucursal son roles de `Usuario`,
mientras que `Miembro` es una entidad independiente.

Explicar la estructura de identidad neutral, su uso como primer argumento de los
servicios y la diferencia entre autenticación y autorización. Incluir cómo se
verifica la contraseña y cómo se impide que un miembro consulte información de
otro miembro.

**Resumen de sección:** incluir una matriz breve de rol, operaciones permitidas
y operaciones restringidas.

### 3. Modelo de dominio y relaciones

Presentar las clases agrupadas por responsabilidad, sin repetir todos sus
atributos. Explicar únicamente las relaciones que sean necesarias para entender
los flujos:

- Identidad: `Miembro`, `Usuario`, `Rol`.
- Configuración: `Plan`, `VersionPlan` y sus configuraciones de beneficios.
- Recompensas: `Recompensa` y `VersionRecompensa`.
- Participación: `Membresia` y `Renovacion`.
- Operaciones: `Compra`, `TransaccionPuntos` y
  `TransaccionCashback`.

Explicar especialmente que `Plan` y `Recompensa` representan identidades base,
mientras que sus clases de versión representan condiciones aplicables durante
un periodo determinado.

**Resumen de sección:** incluir las relaciones esenciales entre las clases.

**Anexo externo:** indicar aquí la inclusión de un diagrama del modelo de
entidades y relaciones.

### 4. Versiones y vigencias

Esta sección debe ser una de las más detalladas porque contiene conceptos que no
son evidentes.

Explicar:

- Qué representa una `VersionPlan` frente a un `Plan`.
- Qué representa una `VersionRecompensa` frente a una `Recompensa`.
- Cómo se definen las fechas de inicio y final.
- Qué significa que una versión esté vigente.
- Cómo se relacionan las promociones con una versión regular base.
- Por qué las condiciones históricas no se sustituyen directamente.
- Qué condiciones se validan para evitar solapamientos.
- Cómo se selecciona una versión para contratación, renovación o canje.

No describir las versiones como simples copias de una entidad. Explicar que son
registros temporales de condiciones comerciales y que permiten conservar el
resultado histórico de las operaciones.

**Resumen de sección:** incluir una comparación breve entre entidad base y
versión temporal.

### 5. Servicios y reglas de negocio

Explicar que los servicios coordinan varias entidades y validan reglas antes de
delegar la persistencia. Usar como ejemplos los servicios de autenticación,
miembros y planes, y relacionarlos con los servicios de membresías, compras,
recompensas y caja que estén presentes en el código.

Describir las reglas más importantes del comportamiento actual:

- Validación de identidad y rol.
- Validación de estados de membresía.
- Selección de versiones vigentes.
- Conservación del historial.
- Cálculo de periodos de renovación.
- Aplicación de descuentos, puntos y cashback.
- Validación de saldos y límites.
- Uso de operaciones atómicas cuando una acción modifica varias entidades.

Explicar que una regla que coordina varias clases pertenece al servicio y no a
una sola entidad.

**Resumen de sección:** incluir una lista de regla, servicio responsable y
entidades afectadas.

### 6. Flujos operativos principales

Explicar mediante pasos numerados los flujos actuales más representativos:

1. Autenticación de un miembro o usuario administrativo.
2. Registro y contratación inicial de un miembro.
3. Renovación o cambio diferido de plan.
4. Actualización del estado de una membresía.
5. Registro de una compra.
6. Generación y consulta de puntos.
7. Generación, desbloqueo y uso de cashback.
8. Canje de una recompensa.

En cada flujo se debe indicar:

- Quién puede iniciarlo.
- Qué servicio lo coordina.
- Qué validaciones se realizan.
- Qué entidades se crean o modifican.
- Qué registros históricos se generan.

**Resumen de sección:** incluir una tabla de flujo, actor, servicio y resultado.

**Anexo externo:** indicar aquí la inclusión de diagramas de flujo para compra,
renovación y canje.

### 7. Persistencia, consultas y mapeadores

Explicar la conexión con MariaDB, el uso de `PyMySQL`, las transacciones, el
`commit`, el `rollback` y la traducción de errores de base de datos a
excepciones del dominio.

Explicar el papel de:

- `base_de_datos/conexion.py`.
- `base_de_datos/consultas.py`.
- `base_de_datos/mapeadores.py`.
- Los scripts SQL de creación y carga de datos.

Definir **mapeador** como el componente que convierte una fila o conjunto de
filas de MariaDB en una instancia de una clase del dominio. Mostrar al menos un
ejemplo conceptual de ida y vuelta entre base de datos y objeto Python.

También explicar por qué los servicios no deben modificar directamente las
estructuras internas de persistencia ni ejecutar SQL de forma directa.

**Resumen de sección:** incluir el recorrido `fila SQL → mapeador → objeto` y
`objeto → consulta de guardado → fila SQL`.

### 8. Seguridad y excepciones

Explicar el uso de `bcrypt` para las contraseñas, la validación de credenciales y
la separación entre errores de entrada, permisos, vigencia, saldos y
persistencia.

Presentar solo las excepciones que existan en el código actual y asociarlas con
el tipo de error que representan.

**Resumen de sección:** incluir una tabla de excepción y situación que la
produce.

### 9. Recorrido guiado del código

Cerrar la guía con un recorrido concreto desde `main.py` hasta una operación de
negocio completa. Se recomienda utilizar el flujo de registro de compra porque
permite relacionar interfaz, identidad, servicios, membresía, beneficios,
transacciones y persistencia.

El recorrido debe citar rutas y funciones relevantes, pero no reproducir bloques
extensos de código.

**Resumen de sección:** incluir un mapa de archivos y funciones visitados.

## Glosario

El glosario debe limitarse a tecnicismos y conceptos abstractos del sistema que
puedan causar confusión. Debe incluir, como mínimo, cuando aparezcan en la
guía:

- Identidad neutral.
- Servicio de aplicación.
- Mapeador.
- Persistencia.
- Vigencia.
- Versión temporal.
- Operación atómica.
- Saldo derivado de movimientos.
- Inmutabilidad de condiciones.

No incluir definiciones básicas de términos como miembro, compra o membresía.

## Anexos externos

La guía debe contener referencias textuales a anexos, pero los diagramas deben
mantenerse fuera del documento. Los anexos recomendados son:

- Diagrama de arquitectura.
- Diagrama de clases y relaciones.
- Diagrama del flujo de compra.
- Diagrama del flujo de renovación.
- Diagrama del flujo de canje.

Cada referencia debe indicar qué sección complementa y qué aspecto debe poder
entenderse observando el diagrama.

## Fuentes que debe consultar el agente

Antes de redactar o actualizar la guía, el agente debe revisar:

- `AGENTS.md`.
- `documentación/estructura_repositorio.md`.
- `documentación/modelo_clases.md`.
- `documentación/implementacion.md`.
- `documentación/requerimientos_funcionales_v2.md`.
- `base_de_datos/consultas.py`.
- `base_de_datos/mapeadores.py`.
- Los servicios y clases existentes.
- `main.py` y la navegación de la interfaz.

El código vigente tiene prioridad para describir comportamientos implementados.
La documentación debe utilizarse para entender contratos, nombres y reglas,
pero no para afirmar comportamientos que no puedan verificarse en el proyecto.

## Restricciones finales

- No incluir una sección sobre el objetivo de la guía.
- No incluir una visión general básica del sistema.
- No incluir un plan explícito de estudio de tres días.
- No incluir preguntas frecuentes.
- No incluir funcionalidades pendientes, descartadas o futuras.
- No incluir diagramas dentro del documento.
- No convertir la guía en una lista exhaustiva de firmas de funciones.
- Mantener un resumen al final de cada sección principal.
