# Cambio temporal para la exposición: miembros sin filtros

## Motivo

Para la exposición se simplificó el módulo de miembros y membresías. Se
eliminó la búsqueda de miembros por múltiples criterios para evitar explicar
filtros, estados y planes durante la demostración.

## Comportamiento actual

El menú `Miembros y membresías` ofrece:

- Buscar una membresía.
- Mostrar todos los miembros.
- Volver.

La opción `Mostrar todos los miembros` obtiene todos los miembros y muestra
únicamente aquellos que tienen una membresía asociada.

## Código retirado

Se eliminó:

- `buscar_miembros()` de
  `base_de_datos/consultas/miembros/consultas_miembros.py`.
- `buscar_miembros()` de
  `servicios/miembro/servicio_miembro.py`.
- La función `_filtrar_miembros()` y su opción de menú de
  `interfaz_term/pantallas/usuario/principal.py`.

## Restauración posterior

Para restaurar la búsqueda:

1. Reincorporar la función `buscar_miembros(filtros)` en
   `base_de_datos/consultas/miembros/consultas_miembros.py`.
2. Reincorporar el servicio `buscar_miembros(identidad, filtros)`.
3. Restaurar la función `_filtrar_miembros()` en la pantalla administrativa.
4. Añadir nuevamente `Filtrar miembros` al menú `Miembros y membresías`.
5. Restaurar el import correspondiente en `principal.py`.
