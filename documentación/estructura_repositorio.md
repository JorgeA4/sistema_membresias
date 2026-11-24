# Estructura del repositorio

Nexum es una aplicación Python organizada por capas. Cada capa tiene una
responsabilidad concreta y debe evitar asumir responsabilidades de otra capa.

```text
sistema_membresias/
├── main.py
├── clases/
├── servicios/
│   ├── autenticacion/
│   ├── autorizacion/
│   ├── miembro/
│   ├── usuario/
│   ├── plan/
│   ├── recompensa/
│   ├── membresia/
│   ├── compra/
│   ├── caja/
│   └── ajuste/
├── base_de_datos/
│   ├── ejecutor.py
│   └── consultas/
│       ├── miembros/
│       │   ├── consultas_miembros.py
│       │   └── operaciones_miembros.py
│       ├── usuarios/
│       │   ├── consultas_usuarios.py
│       │   └── operaciones_usuarios.py
│       ├── membresias/
│       │   ├── consultas_membresias.py
│       │   └── operaciones_membresias.py
│       ├── planes/
│       │   ├── consultas_planes.py
│       │   └── operaciones_planes.py
│       ├── recompensas/
│       │   ├── consultas_recompensas.py
│       │   └── operaciones_recompensas.py
│       └── compras/
│           ├── consultas_compras.py
│           └── operaciones_compras.py
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

Contiene la lógica de negocio que coordina varias clases. Los servicios reciben
identificadores y datos de entrada, validan las reglas del dominio y utilizan
`base_de_datos/` para consultar o guardar información. No deben acceder
directamente a los diccionarios internos de la base simulada.

La separación inicial es la siguiente:

- `autenticacion/`: autenticación de miembros y usuarios administrativos.
- `autorizacion/`: validación de roles y propiedad de membresías.
- `miembro/`: registro, consulta, modificación y eliminación de miembros.
- `usuario/`: registro, consulta, modificación y eliminación de usuarios.
- `plan/`: planes y versiones de planes.
- `recompensa/`: recompensas, versiones de recompensas, canjes e historial de
  canjes.
- `membresia/`: aplicación de versiones, renovación y cancelación.
- `compra/`: registro de compras, descuentos, cashback y generación de puntos.
- `caja/`: operaciones presenciales que coordinan venta y canje.
- `ajuste/`: ajustes manuales de puntos y cashback exclusivos del Administrador.

No se crearán inicialmente servicios independientes para transacciones de
puntos ni transacciones de cashback. Esas transacciones se generan desde los
servicios de compra y recompensa, según corresponda.

## `base_de_datos/`

Contiene la persistencia y las consultas del sistema. Las consultas están
organizadas por dominio dentro de `consultas/`:

- `consultas_*.py`: lecturas y obtención de datos.
- `operaciones_*.py`: inserciones, modificaciones y eliminaciones.

La infraestructura común de conexión, transacciones y errores se mantiene en
`ejecutor.py`. Cada módulo de dominio contiene directamente sus consultas SQL,
operaciones de persistencia y mapeos necesarios. La conexión con MariaDB se
encuentra pendiente de completar.

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
interfaz del proyecto. `implementacion.md` concentra los contratos de servicios
y las decisiones técnicas pendientes de la primera implementación.

## `requirements.txt`

Registra las dependencias externas del proyecto.
