# Plan de interfaz con Qt

## 1. Decisiones técnicas

La interfaz será una aplicación local de escritorio para ejecutarse en un solo
ordenador.

- Python como lenguaje principal.
- PySide6 como enlace de Python para Qt.
- Qt Widgets como tecnología de interfaz.
- MariaDB (XAMPP/LAMP) como fuente de datos.
- Sin navegador, servidor web ni aplicación móvil.
- Sin necesidad de acceso simultáneo desde varios dispositivos.
- Qt Style Sheets únicamente para el pulido visual posterior.
- Qt Designer no será necesario al inicio; las primeras pantallas se escribirán
  directamente en Python.

La elección de PySide6 sobre PyQt6 se basa en que es el enlace oficial de Qt
para Python y ofrece una opción adecuada para este proyecto.

## 2. Principios de arquitectura

La interfaz no debe contener consultas SQL ni reglas principales del negocio.

```text
Pantalla Qt
    ↓
Servicio
    ↓
Base de datos
```

La interfaz recoge datos y muestra resultados. Los servicios validan permisos,
vigencias, límites, saldos y operaciones.

Estructura real (ajustada respecto al borrador inicial):

```text
interfaz/
    ventana_inicio.py           ✅ punto de entrada; monta el QStackedWidget principal
    pantallas/
        bienvenida.py           ✅ pantalla de selección Miembro / Usuario (nueva)
        inicio_sesion.py        ✅ formulario de login con señales login_exitoso y volver
        miembro/                ✅ carpeta para la interfaz de miembro
            principal.py        ✅ esqueleto con mensaje de confirmación y cerrar sesión
            membresia.py
            puntos.py
            recompensas.py
            historial.py
        usuario/                ✅ carpeta compartida para Administrador y Cajero
            principal.py        ✅ esqueleto con mensaje de confirmación y cerrar sesión
            miembros.py
            planes.py
            compras.py
            actividad.py
    componentes/                ✅ carpeta creada
        mensajes.py             ✅ advertencia(), error(), informacion(), confirmar()
        botones.py              ✅ boton_volver(), boton_cerrar_sesion()
        tabla.py
        formulario.py
        dialogos.py
    estilos/
        tema.qss
```

La estructura podrá ajustarse cuando se implementen los servicios y la base de
datos.

## 3. Navegación

La aplicación utilizará una ventana principal con:

- Menú lateral.
- Área central de contenido.
- Encabezado con el usuario y su rol.
- `QStackedWidget` para cambiar entre pantallas. ✅
- Diálogos para confirmar operaciones.
- Mensajes consistentes para operaciones exitosas y errores. ✅ (en componentes/mensajes.py)

Las secciones se mostrarán dentro de la ventana principal en lugar de abrir una
nueva ventana para cada acción. ✅

### Patrón de navegación entre pantallas ✅

Cada pantalla emite señales hacia arriba; `ventana_inicio.py` las escucha y mueve el
stack. Las pantallas no se conocen entre sí.

```text
QStackedWidget principal
├── [0] PantallaBienvenida      → emite: seleccion_hecha(tipo)
├── [1] PantallaInicioSesion    → emite: login_exitoso(tipo), volver
├── [2] PantallaPrincipalMiembro → emite: cerrar_sesion
└── [3] PantallaPrincipalUsuario → emite: cerrar_sesion
```

Flujo de navegación:
- Bienvenida → elige tipo → InicioSesion
- InicioSesion → volver → Bienvenida
- InicioSesion → login exitoso → Miembro o Usuario según tipo
- Miembro / Usuario → cerrar sesión → Bienvenida

Cuando las interfaces de miembro y usuario crezcan, cada una tendrá su propio
`QStackedWidget` interno con menú lateral. El stack principal solo cambiará
entre bienvenida, login y la interfaz correspondiente.

## 4. Alcance mínimo

### 4.1 Inicio de sesión ✅ (parcial — sin autenticación real aún)

Debe permitir:

- Introducir correo o identificador. ✅
- Introducir contraseña. ✅
- Seleccionar tipo de acceso (Miembro o Usuario) antes del formulario. ✅
- Validar que los campos no estén vacíos. ✅
- Validar las credenciales. (pendiente — requiere servicio de autenticación)
- Redirigir según el rol. ✅ (estructura lista; destino simulado por ahora)
- Mostrar únicamente las opciones permitidas. (pendiente)

Roles contemplados:

- `Administrador`.
- `Cajero`.
- `Miembro`.

### 4.2 Usuarios (Administrador y Cajero)

Cajero y Administrador son ambos **usuarios administrativos** y comparten la
misma interfaz en `usuario/`. Solo difieren en las opciones que ven: eso se
controla en la Fase 3 según el rol devuelto por el servicio de autenticación.
No hay dos interfaces de usuario; hay una sola que se adapta al rol.

La primera versión incluirá:

- Inicio. ✅ (esqueleto creado en usuario/principal.py)
- Miembros.
- Planes.
- Recompensas.
- Compras.
- Actividad.
- Usuarios y roles, si el tiempo lo permite.

Los módulos principales deberán incluir, según corresponda:

- Tabla de registros.
- Creación.
- Consulta.
- Modificación.
- Búsqueda o filtro básico.

El cajero verá únicamente el subconjunto de opciones que le corresponde
(principalmente compras); el administrador verá todo. Esto se implementará en
la Fase 3.

### 4.3 Miembro

La primera versión incluirá:

- Resumen de membresía.
- Información personal.
- Saldo de puntos.
- Recompensas disponibles.
- Historial de compras.
- Historial de puntos.
- Historial de canjes.

El canje, la renovación y la cancelación se conectarán después de que los
servicios correspondientes estén funcionando.

## 5. Fases de implementación

### Fase 1: Prototipo visual aislado ✅ (en progreso)

Crear una aplicación Qt sin base de datos que incluya:

- Ventana principal. ✅
- Pantalla de bienvenida (selección de tipo). ✅
- Pantalla de inicio de sesión con campos y validación básica. ✅
- Navegación entre pantallas con QStackedWidget y señales. ✅
- Botón Volver y botón Cerrar sesión. ✅
- Esqueleto de interfaz de miembro. ✅
- Esqueleto de interfaz de usuario. ✅
- Menú lateral.
- Tabla de ejemplo.
- Formulario de ejemplo.
- Diálogo de confirmación.
- Tema visual básico.

Objetivo: comprender `QApplication`, `QMainWindow`, `QWidget`, layouts,
señales, botones, `QStackedWidget`, tablas y diálogos.

### Fase 2: Componentes reutilizables ✅ (parcial)

Crear componentes comunes para:

- Mensajes de éxito, advertencia y error. ✅ (componentes/mensajes.py)
- Botones reutilizables (Volver, Cerrar sesión). ✅ (componentes/botones.py)
- Tablas de registros.
- Formularios.
- Diálogos de confirmación.
- Tarjetas de resumen.

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

Este flujo validará la integración entre Qt, servicios y base de datos.

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

Realizar el pulido visual después de completar la funcionalidad principal:

- Colores del proyecto.
- Tipografía.
- Espaciado.
- Estados de membresía.
- Botones destructivos.
- Tablas más claras.
- Mensajes consistentes.
- Archivo `tema.qss`.

## 6. Dirección visual

Se buscará una interfaz sencilla y consistente:

- Fondo claro o gris suave.
- Menú lateral oscuro.
- Color principal para acciones normales.
- Verde para operaciones exitosas.
- Rojo únicamente para cancelaciones o eliminaciones.
- Tarjetas para membresías activas, puntos, compras y canjes.
- Tablas con búsqueda y acciones visibles.

No se priorizarán animaciones ni un dashboard excesivamente complejo.

## 7. Riesgos que se evitarán

- No aprender QML durante la primera versión.
- No mezclar Qt Designer con código Python hasta dominar lo básico.
- No poner SQL dentro de botones o ventanas. ✅
- No crear una ventana distinta para cada acción. ✅
- No diseñar todas las pantallas antes de conectar una funcionalmente.
- No invertir tiempo en animaciones antes de completar la Capa 1.
- No utilizar modelos y vistas complejos si una tabla sencilla permite avanzar.
- No bloquear la interfaz con operaciones largas; si fuera necesario, se
  incorporará `QThread` posteriormente.

## 8. Criterios para terminar la primera etapa

El prototipo inicial estará completo cuando pueda:

1. Abrir una ventana Qt. ✅
2. Mostrar el inicio de sesión. ✅
3. Cambiar al menú correcto según el rol. ✅ (estructura lista; sin autenticación real aún)
4. Navegar entre al menos tres pantallas. ✅
5. Mostrar una tabla.
6. Abrir un formulario.
7. Validar campos. ✅ (campos vacíos en login)
8. Mostrar mensajes de éxito y error. ✅ (componentes/mensajes.py)
9. Confirmar una operación mediante un diálogo.
10. Mantener una estructura preparada para conectarse con los servicios. ✅

Este prototipo será el primer objetivo antes de implementar toda la interfaz.
