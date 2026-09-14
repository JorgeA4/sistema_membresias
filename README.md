# sistema_membresias
Un sistema que configure y gestione las tarjetas de membresia y fidelización que ofrece un negocio a sus clientes. Además de brindarle al cliente una interfaz para gestionar su membresia.

# estructura del sistema
sistema_membresias/
│
├── main.py
│
├── models/
│   ├── miembro.py
│   ├── plan_membresia.py
│   ├── membresia.py
│   ├── compra.py
│   ├── recompensa.py
│   ├── renovación.py
│   └── canje.py
│
├── services/
    └── ...
│
├── database/
    └── ...
│
├── cli/
│   ├── menu.py
│
└── utils/
    └── ...

# Explicación desglosada
models/
Guarda las clases centrales del sistema. Cada módulo es una clase.

miembro.py
Se crea cuando el administrador registra un nuevo miembro.
Atributos: id. nombre. membresias. puntos. compras. canjes. renovaciones.
Funciones: Mostrar su información. Modificar su información. Desactivarse. Eliminarse. Suma puntos. Canjea puntos.

plan_membresia.py
Se crea cuando el administrador crea un nuevo tipo de membresía.
Atributos: id. precio. plazo. regla_puntos. regla_descuento.
Funciones: Mostrar su información. Modificar su información. Eliminarse.

membresia.py
Se crea cuando un miembro activa una membresía.
Atributos: id. id_miembro. id_plan_membresia. estado. fecha_activacion. fecha_vencimiento.
Funciones: Mostrar su información. Renovarse. Cancelarse.

compra.py
Se crea cuando una compra es asociada a la cuenta de un miembro.
Atributos: id_membresia. monto. fecha. puntos_generados.
Funciones: Mostrar su información.

recompensa.py
Se crea cuando el administrador crea una nueva recompensa.
Atributos: id, descripción. costo_puntos. activa.
Funciones: Mostrar su información. Modificar su información. Eliminarse.

renovación.py
Se crea cuando un miembro renueva su membresía.
Atributos: id_membresia. fecha.
Funciones: Mostrar su información.

canje.py
Se crea cuando un miembro canjea sus puntos.
Atributos: id_membresia. id_recompensa. puntos_canjeados. fecha.
Funciones: Mostrar su información.
