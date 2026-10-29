# Plan de interfaz en terminal (TUI)

## Estado

**Esta es la interfaz activa del proyecto.** Se tomó la decisión de implementar
la interfaz en terminal en lugar de la interfaz gráfica con Qt. El código de
`interfaz_qt/` se conserva como referencia pero no está en uso y no es necesario
completarlo.

## 1. Decisiones técnicas

La interfaz será una aplicación de terminal que se ejecuta en un solo ordenador.

- Python como lenguaje principal.
- **Rich** para todo lo visual: tablas, paneles, mensajes, colores y estilos.
- **questionary** para toda la interacción: menús con flechas, confirmaciones y
  prompts con validación.
- `input()` de Python para los campos de formulario (texto libre).
- MariaDB (XAMPP/LAMP) como fuente de datos.
- Sin navegador, servidor web ni aplicación móvil.
- Sin necesidad de acceso simultáneo desde varios dispositivos.
- Los estilos de color y formato de Rich se centralizan en `estilos/tema.py`.

## 2. Principios de arquitectura

La interfaz no debe contener consultas SQL ni reglas principales del negocio.

```text
Pantalla (función)
    ↓
Servicio
    ↓
Base de datos
```

La interfaz recoge datos y muestra resultados. Los servicios validan permisos,
vigencias, límites, saldos y operaciones.

Estructura de carpetas:

```text
interfaz_term/
    ventana_inicio.py       punto de entrada; contiene ejecutar_aplicacion()
                            y el loop principal de navegación
    pantallas/
        __init__.py
        bienvenida.py       pantalla de selección Miembro / Usuario
        inicio_sesion.py    formulario de login con validación básica
        miembro/
            __init__.py
            principal.py    menú principal del miembro
            membresia.py
            puntos.py
            recompensas.py
            historial.py
        usuario/
            __init__.py
            principal.py    menú principal del usuario (Admin y Cajero)
            miembros.py
            planes.py
            compras.py
            actividad.py
    componentes/
        __init__.py
        mensajes.py         advertencia(), error(), informacion(), confirmar()
        tabla.py            mostrar_tabla() con Rich
        formulario.py       pedir_campo(), pedir_formulario()
    estilos/
        __init__.py
        tema.py             constantes de color y estilos de Rich
```

La estructura podrá ajustarse cuando se implementen los servicios y la base de
datos.

## 3. Navegación

### Concepto central

Cada pantalla es una **función Python** que:

1. Dibuja su contenido con Rich.
2. Pide al usuario que elija una acción con questionary.
3. **Devuelve una tupla `(interfaz, pantalla)`** que indica a dónde ir a
   continuación.

`ventana_inicio.py` contiene un loop que mantiene un objeto `sesion` compartido
y llama a la función correcta según esos valores. Las pantallas no se conocen
entre sí — solo reciben `sesion` y devuelven la tupla.

### El objeto `sesion`

```python
sesion = {
    "interfaz": None,   # str o None: "miembro" | "usuario" | None
    "historial": []     # list[int]: pila de números de pantalla visitados
}
```

Todas las funciones de pantalla reciben `sesion` como único argumento y lo
usan para leer el contexto actual (p. ej. `sesion["interfaz"]` para saber el
tipo de acceso activo).

### Números de pantalla

| Número | Pantalla                          |
|--------|-----------------------------------|
| 1      | Bienvenida                        |
| 2      | Inicio de sesión                  |
| 3      | Menú principal (miembro o usuario)|
| 4      | Volver (acción especial)          |
| 5      | Salir (rompe el loop)             |

### Tabla de despacho (`flujo`)

El loop usa un diccionario de dos niveles `flujo[interfaz][numero_pantalla]`
para resolver qué función llamar. El mismo número `3` apunta a funciones
distintas según la interfaz activa:

```python
flujo = {
    None: {
        1: mostrar_bienvenida
    },
    "miembro": {
        2: mostrar_login_con_volver,
        3: mostrar_miembro,
        4: volver
    },
    "usuario": {
        2: mostrar_login_con_volver,
        3: mostrar_usuario,
        4: volver
    }
}
```

### Firmas de las pantallas

```text
mostrar_bienvenida(sesion)       → ("miembro" | "usuario" | None, 2 | 5)
mostrar_login_con_volver(sesion) → (tipo, 3 | 4)
mostrar_miembro(sesion)          → (None, 1)
mostrar_usuario(sesion)          → (None, 1)
volver(sesion)                   → (interfaz, None)   ← función interna del loop
```

### Función `volver`

`volver` elimina **dos entradas** del historial con `del sesion["historial"][-2:]`:
el `4` que representa la propia llamada a volver y la pantalla de origen. De
este modo el loop regresa a la pantalla anterior correcta.

### Flujo de navegación

```text
Bienvenida (1) → elige tipo → Login (2)
Login (2)      → Volver     → volver (4) → Bienvenida (1)
Login (2)      → credenciales correctas  → Menú principal (3)
Menú (3)       → Cerrar sesión           → Bienvenida (1)
Bienvenida (1) → Salir                   → 5 → break
```

Cuando las interfaces de miembro y usuario crezcan, cada una tendrá su propio
loop interno con menú lateral. `ejecutar_aplicacion()` solo navegará entre
bienvenida, login y la interfaz correspondiente.

## 4. Componentes reutilizables

### 4.1 mensajes.py

Funciones que dibujan un `Panel` de Rich con el color apropiado y luego
esperan que el usuario presione Enter para continuar.

- `informacion(texto)` — panel azul.
- `advertencia(texto)` — panel amarillo.
- `error(texto)` — panel rojo.
- `exito(texto)` — panel verde.
- `confirmar(pregunta)` — devuelve `True` / `False` usando `questionary.confirm()`.

### 4.2 tabla.py

- `mostrar_tabla(titulo, columnas, filas)` — construye y muestra un `Table` de
  Rich con los parámetros recibidos.

### 4.3 formulario.py

- `pedir_campo(etiqueta, requerido, contrasena)` — muestra la etiqueta con Rich
  y recoge el valor con `input()`. Si `contrasena=True` usa `getpass` para no
  mostrar el texto.
- `pedir_formulario(campos)` — recibe una lista de definiciones de campo, los
  pide en orden, muestra el resumen con Rich, y devuelve el dict de valores
  solo cuando el usuario confirma. Si el usuario elige corregir, permite editar
  campo por campo.

### 4.4 estilos/tema.py

Centraliza las constantes de estilo de Rich para que el cambio visual se
aplique desde un solo lugar:

- Colores por tipo de mensaje (info, advertencia, error, éxito).
- Color del encabezado.
- Estilo de las tablas.
- Estilo de los paneles.

## 5. Alcance mínimo

### 5.1 Inicio de sesión

Debe permitir:

- Seleccionar tipo de acceso (Miembro o Usuario).
- Introducir correo o identificador.
- Introducir contraseña (sin mostrar caracteres).
- Validar que los campos no estén vacíos.
- Validar las credenciales. (pendiente — requiere servicio de autenticación)
- Redirigir según el rol.
- Mostrar únicamente las opciones permitidas. (pendiente — Fase 3)

Roles contemplados: `Administrador`, `Cajero`, `Miembro`.

### 5.2 Usuarios (Administrador y Cajero)

Cajero y Administrador comparten la interfaz en `usuario/`. La diferenciación
de opciones visibles según rol se implementa en la Fase 3.

La primera versión incluirá:

- Menú principal con opciones numeradas.
- Miembros (tabla + alta + consulta + modificación).
- Planes.
- Versiones de planes.
- Recompensas.
- Versiones de recompensas.
- Compras.
- Actividad.
- Usuarios y roles, si el tiempo lo permite.

El cajero verá únicamente compras; el administrador verá todo.

### 5.3 Miembro

La primera versión incluirá:

- Resumen de membresía.
- Información personal.
- Saldo de puntos.
- Recompensas disponibles.
- Historial de compras.
- Historial de puntos.
- Historial de canjes.

El canje, la renovación y la cancelación se conectarán cuando los servicios
estén disponibles.

## 6. Fases de implementación

### Fase 1: Prototipo visual aislado

Crear la aplicación sin base de datos que incluya:

- Loop principal de navegación en `ventana_inicio.py`.
- Pantalla de bienvenida con selector de tipo.
- Pantalla de login con campos y validación de vacíos.
- Esqueleto de menú de miembro.
- Esqueleto de menú de usuario.
- Componente de mensajes (info, advertencia, error, confirmar).
- Componente de tabla de ejemplo.
- Componente de formulario de ejemplo (campo por campo + resumen + confirmar).
- Tema visual básico en `estilos/tema.py`.

Objetivo: comprender `Console` de Rich, `Panel`, `Table`, `questionary.select()`,
`questionary.confirm()`, `input()`, y el patrón de navegación con retorno de
funciones.

### Fase 2: Componentes reutilizables

Pulir y completar los componentes comunes:

- Mensajes consistentes con colores del tema.
- Tabla reutilizable con columnas configurables.
- Formulario con resumen y corrección de campos.
- Confirmaciones con questionary.

### Fase 3: Inicio de sesión y permisos

Conectar la interfaz con la autenticación y los roles.

Pruebas mínimas:

- El administrador ve todas las opciones.
- El cajero solo ve las funciones de compras.
- El miembro no ve funciones administrativas.
- Un usuario no autenticado no puede acceder al menú principal.

### Fase 4: Primer flujo completo

Implementar un flujo vertical completo antes de construir todas las pantallas:

```text
Iniciar sesión
→ consultar miembros
→ registrar miembro
→ modificar miembro
→ guardar en MariaDB
→ mostrar los datos actualizados
```

Este flujo validará la integración entre la TUI, los servicios y la base de
datos.

### Fase 5: Módulos administrativos

Implementar en este orden:

1. Miembros.
2. Planes.
3. Versiones de planes.
4. Recompensas.
5. Versiones de recompensas.
6. Compras.
7. Consultas de actividad.
8. Usuarios y roles.

### Fase 6: Interfaz de miembro

Agregar:

- Resumen de membresía.
- Puntos.
- Recompensas.
- Historiales.
- Canje.
- Renovación.
- Cancelación.

### Fase 7: Diseño visual

Realizar el pulido visual después de completar la funcionalidad:

- Paleta de colores del proyecto en `tema.py`.
- Estilos de tabla (bordes, colores de cabecera).
- Colores por estado de membresía (activa, vencida, cancelada).
- Paneles de resumen (tarjetas de membresía, puntos, compras).
- Mensajes consistentes en toda la aplicación.

## 7. Dirección visual

Se buscará una interfaz sencilla y consistente:

- Encabezado con nombre del sistema y usuario activo.
- Paneles con bordes para agrupar información relacionada.
- Color verde para operaciones exitosas.
- Color rojo para errores, cancelaciones y eliminaciones.
- Color amarillo para advertencias.
- Tablas con cabecera coloreada y filas alternas.
- Menús claros con opciones numeradas o con flechas.

No se priorizarán animaciones ni efectos complejos.

## 8. Riesgos que se evitarán

- No poner SQL dentro de las funciones de pantalla.
- No mezclar lógica de negocio con presentación.
- No duplicar estilos; todos los colores van en `tema.py`.
- No diseñar todas las pantallas antes de conectar una funcionalmente.
- No bloquear el loop principal con operaciones largas; si fuera necesario, se
  evaluará el uso de hilos o async posteriormente.

## 9. Criterios para terminar la primera etapa

El prototipo inicial estará completo cuando pueda:

1. Iniciar la aplicación con `python main.py`.
2. Mostrar la pantalla de bienvenida.
3. Completar el flujo de login (simulado, sin BD).
4. Navegar al menú de miembro o de usuario según la selección.
5. Mostrar una tabla de ejemplo con Rich.
6. Completar un formulario de ejemplo (campo por campo + resumen + confirmar).
7. Validar campos vacíos.
8. Mostrar mensajes de éxito y error con el componente de mensajes.
9. Confirmar una operación con `questionary.confirm()`.
10. Volver al inicio desde cualquier punto del flujo.
11. Mantener una estructura lista para conectarse con los servicios.
