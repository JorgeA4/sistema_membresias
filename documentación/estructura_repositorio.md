# Estructura del repositorio

Nexum es una aplicación Python organizada por capas. Cada capa tiene una
responsabilidad concreta y debe evitar asumir responsabilidades de otra capa.

```text
sistema_membresias/
├── main.py
├── clases/
├── servicios/
├── base_de_datos/
├── interfaz_term/
├── interfaz_qt/
├── utilidades/
├── documentación/
└── requirements.txt
```

## `main.py`

Es el punto de entrada de la aplicación. Inicia la interfaz principal de
terminal.

## `clases/`

Contiene las clases del dominio de Nexum. Las clases representan entidades y
objetos del modelo de datos. Su lógica debe limitarse a invariantes y
comportamientos que pertenecen naturalmente al objeto.

## `servicios/`

Contiene la lógica de negocio que coordina varias clases, como registrar
compras, renovar membresías, aplicar versiones de planes o validar límites de
uso. Esta carpeta todavía se encuentra en desarrollo.

## `base_de_datos/`

Contiene la persistencia y las consultas del sistema. Actualmente incluye una
base de datos simulada en memoria, datos de prueba y consultas simuladas. La
conexión con MariaDB se encuentra pendiente de completar.

## `interfaz_term/`

Contiene la interfaz de usuario para terminal, sus componentes, estilos y el
flujo de navegación de la aplicación.

## `interfaz_qt/`

Contiene una interfaz de escritorio basada en PySide6. Se mantiene separada de
la interfaz de terminal y actualmente está detenida.

## `utilidades/`

Contiene funciones auxiliares reutilizables que no pertenecen al dominio ni a
una capa específica.

## `documentación/`

Contiene los requisitos, decisiones de diseño, modelos de datos y planes de
interfaz del proyecto.

## `requirements.txt`

Registra las dependencias externas del proyecto.
