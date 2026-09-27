sistema_membresias/
│
├── main.py
│
├── clases/
│   ├── miembro.py
│   ├── plan.py
│   ├── membresia.py
│   ├── transaccion_puntos.py
│   ├── compra.py
│   ├── recompensa.py
│   ├── renovación.py
│   ├── canje.py
│   ├── rol.py
│   └── usuario_admin.py
│
├── servicios/
│   ├── servicio_miembro.py
│   ├── servicio_plan.py
│   ├── servicio_membresia.py
│   ├── servicio_recompensa.py
│   └── servicio_usuario_admin.py
│
├── base_de_datos/
    └── ...
│
├── interfaz/
│   ├── menu.py
│
└── utilidades/
    └── ...

# main.py
Importa los el módulo que ejecuta la interfaz inicial y lo corre. Importa keys si hacen falta.

# clases/
Guarda las clases centrales del sistema. Cada módulo es una clase.

## miembro.py
Se crea cuando el administrador registra un nuevo miembro.
Atributos: num. telefono. correo. nombre. primer_apellido, segundo_apellido. fecha_registro. contraseña.
Funciones: info().

## plan.py
Se crea cuando el administrador crea un nuevo tipo de membresía.
Atributos: codigo. nombre. descripcion. es_gratuita. precio. plazo_meses. puntos_por_peso. porcentaje_descuento.
Funciones: info(). 

## membresia.py
Se crea cuando un miembro activa una membresía.
Atributos: num. num_miembro. num_plan. estado(Enum). fecha_activacion. fecha_vencimiento.
Funciones: info(). esta_vencida().

## transaccion_puntos.py
Se crea cuando un miembro acumula o gasta puntos.
Atributos: num. num_miembro. num_membresia. cantidad. fecha. tipo(Enum).
Funciones: info().

### transaccion_puntos.transaccion_compra
Se crea para asociar una transacción con una compra.
Atributos: num_transaccion. num_compra.
Funciones: 

### transaccion_puntos.transaccion_canje
Se crea para asociar una transacción con un canje.
Atributos: num_transaccion. num_canje.
Funciones: 

## compra.py
Se crea cuando una compra es asociada a la cuenta de un miembro.
Atributos: num. num_membresia. num_usuario_admin. monto.
Funciones: info().

## recompensa.py
Se crea cuando el administrador crea una nueva recompensa.
Atributos: codigo. nombre. descripción. costo_puntos. esta_activa.
Funciones: info().

## renovación.py
Se crea cuando un miembro renueva su membresía.
Atributos: num. num_membresia. monto_pagado. fecha.
Funciones: info().

## canje.py
Se crea cuando un miembro canjea sus puntos por una recompensa.
Atributos: num. num_membresia. num_recompensa.
Funciones: info().

## rol.py
Se crea cuando el administrador define un tipo de usuario administrativo.
Atributos: num. nombre. descripcion.
Funciones: info().

## usuario_admin.py
Se crea cuando el administrador registra un nuevo usuario administrativo.
Atributos: num. num_rol. nombre. primer_apellido. segundo_apellido. correo. telefono. contraseña.
Funciones: info().

# servicios/
Guarda funciones que utilizan más de una clase y no es correcto asignar como método a ninguna de las 2.

## servicio_miembro.py
Guarda los servicios que involucran a miembro.
Funciones: eliminar(num). modificar(num, datos).

## servicio_plan.py
Guarda los servicios que involucran a plan.
Funciones: eliminar(num). modificar(num, datos).

## servicio_membresia.py
Guarda los servicios que involucran a membresia.
Funciones: renovar(id). cancelar(id).

## servicio_recompensa.py
Guarda los servicios que involucran a recompensa.
Funciones: eliminar(id). modificar(num, datos). activar_desactivar(num).

## servicio_usuario_admin.py
Guarda los servicios que involucran a usuario_admin.
Funciones: eliminar(num). modificar(num, datos).

# base_de_datos/
Lógica que conecta el código con la base de datos. Hace consultas.

# interfaz/
Programación encargada del frontend y su lógica.

## menu.py
Menú principal. (Aún en planeación)

# utilidades/
Funciones reutilizables en cualquier parte del código, que no se relacionan de manera directa con el funcionamiento del sistema.
