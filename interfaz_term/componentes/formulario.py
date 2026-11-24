"""
Componentes de formulario para la interfaz de terminal.

Ofrece dos funciones:
  - pedir_campo()      → solicita un campo individual con etiqueta.
  - pedir_formulario() → solicita varios campos, muestra resumen y pide confirmación.
"""

import getpass
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from interfaz_term.estilos.tema import COLOR_ENCABEZADO, ESTILO_TABLA
import questionary

_consola = Console()
_COMANDO_CANCELAR = "/cancel"


def pedir_campo(
    etiqueta: str,
    requerido: bool = True,
    contrasena: bool = False,
) -> str | None:
    """
    Muestra la etiqueta con Rich y recoge el valor con input() o getpass.

    Parámetros:
        etiqueta   — texto descriptivo del campo.
        requerido  — indica al formulario si el campo puede quedar vacío.
        contrasena — si es True, usa getpass para no mostrar el texto.

    Devuelve el valor ingresado o None si el usuario cancela.
    """
    _consola.print(f"[{COLOR_ENCABEZADO}]{etiqueta}:[/{COLOR_ENCABEZADO}]", end=" ")
    try:
        if contrasena:
            valor = getpass.getpass("")
        else:
            valor = input()
    except KeyboardInterrupt:
        _consola.print()
        return None

    if valor.strip().casefold() == _COMANDO_CANCELAR:
        _consola.print("[yellow]Formulario cancelado.[/yellow]")
        return None

    return valor.strip()


def pedir_formulario(campos: list[dict], iniciar_en_resumen: bool = False) -> dict | None:
    """
    Solicita una lista de campos, muestra un resumen y pide confirmación.

    Cada elemento de `campos` es un dict con las claves:
        - clave      (str) — nombre interno del campo, usado como clave del dict devuelto.
        - etiqueta   (str) — texto mostrado al usuario.
        - requerido  (bool, opcional, default True)
        - contrasena (bool, opcional, default False)
        - confirmar  (bool, opcional, default False) — repite el valor y exige coincidencia.
        - validador  (callable, opcional) — recibe (valor, valores) y devuelve un error o None.
        - antes_de_pedir (callable, opcional) — recibe los valores acumulados.

    Flujo:
        1. Dibuja todos los campos y pide sus valores en orden; `/cancel` o Ctrl+C cancela en cualquier campo.
        2. Redibuja la tabla después de cada entrada y muestra los errores antes de repetir un campo.
        3. Muestra un resumen con Rich (oculta contraseñas).
        4. Pregunta si confirmar o corregir.
           - Si confirma → devuelve el dict de valores.
           - Si elige corregir → permite editar campo por campo y repite el resumen.
           - Si cancela → devuelve None.

    Ejemplo:
        resultado = pedir_formulario([
            {"clave": "nombre",  "etiqueta": "Nombre completo"},
            {"clave": "correo",  "etiqueta": "Correo electrónico"},
            {"clave": "contra",  "etiqueta": "Contraseña", "contrasena": True},
        ])
    """
    valores: dict = {
        campo["clave"]: campo["valor_inicial"]
        for campo in campos
        if "valor_inicial" in campo
    }

    # En edición los valores iniciales ya están completos y se empieza en el resumen.
    if not iniciar_en_resumen:
        for campo in campos:
            clave = campo["clave"]
            if campo.get("confirmar"):
                valor = _pedir_valor_con_confirmacion(campo, campos, valores)
            else:
                valor = _pedir_valor_campo(campo, campos, valores)
            if valor is None:
                return None
            valores[clave] = valor

    while True:
        # Paso 2: mostrar resumen
        _mostrar_resumen(campos, valores)

        # Paso 3: confirmar, corregir o cancelar
        accion = questionary.select(
            "¿Qué deseas hacer?",
            choices=["Confirmar", "Corregir un campo", "Cancelar"],
        ).ask()

        if accion == "Confirmar":
            return valores

        if accion == "Cancelar":
            confirmar = questionary.select(
                "¿Estás seguro de cancelar el formulario?",
                choices=[
                    "No, volver al formulario",
                    "Sí, cancelar formulario",
                ],
            ).ask()
            if confirmar == "Sí, cancelar formulario":
                _consola.print("[yellow]Formulario cancelado.[/yellow]")
                return None
            continue

        # Corregir: elegir qué campo editar
        etiquetas = [c["etiqueta"] for c in campos]
        etiqueta_elegida = questionary.select(
            "Selecciona el campo a corregir:",
            choices=etiquetas,
        ).ask()

        campo_elegido = next(c for c in campos if c["etiqueta"] == etiqueta_elegida)
        clave      = campo_elegido["clave"]
        if campo_elegido.get("confirmar"):
            valor = _pedir_valor_con_confirmacion(campo_elegido, campos, valores)
        else:
            valor = _pedir_valor_campo(campo_elegido, campos, valores)
        if valor is None:
            return None
        valores[clave] = valor


def _pedir_valor_campo(
    campo: dict,
    campos: list[dict],
    valores: dict,
    mensaje_inicial: str | None = None,
) -> str | None:
    """Solicita un campo hasta que su formato sea válido o se cancele."""
    clave = campo["clave"]
    etiqueta = campo["etiqueta"]
    requerido = campo.get("requerido", True)
    contrasena = campo.get("contrasena", False)

    mensaje = mensaje_inicial
    while True:
        _dibujar_formulario(campos, valores, mensaje)
        antes_de_pedir = campo.get("antes_de_pedir")
        if antes_de_pedir is not None:
            antes_de_pedir(valores)
        valor = pedir_campo(etiqueta, requerido=requerido, contrasena=contrasena)
        if valor is None:
            return None
        if not valor and "valor_inicial" in campo:
            return str(campo["valor_inicial"])
        if not valor and not requerido:
            return valor
        if requerido and not valor:
            mensaje = "Este campo es obligatorio."
            continue
        mensaje = _validar_valor(clave, valor, etiqueta)
        if mensaje is None:
            validador = campo.get("validador")
            if validador is not None:
                try:
                    mensaje = validador(valor, valores)
                except (ValueError, PermissionError) as exc:
                    mensaje = str(exc)
        if mensaje is None:
            return valor


def _pedir_valor_con_confirmacion(
    campo: dict,
    campos: list[dict],
    valores: dict,
) -> str | None:
    """Solicita dos veces un valor sensible y reinicia el bloque si difiere."""
    mensaje = None
    while True:
        valor = _pedir_valor_campo(
            campo,
            campos,
            valores,
            mensaje_inicial=mensaje,
        )
        if valor is None:
            return None

        valores_temporales = dict(valores)
        valores_temporales[campo["clave"]] = valor
        campo_confirmacion = dict(campo)
        campo_confirmacion["etiqueta"] = f"Confirmar {campo['etiqueta'].lower()}"
        campo_confirmacion["confirmar"] = False
        confirmacion = _pedir_valor_campo(
            campo_confirmacion,
            campos,
            valores_temporales,
        )
        if confirmacion is None:
            return None
        if confirmacion == valor:
            return valor
        mensaje = "Las contraseñas no coinciden. Escribe ambas nuevamente."


def _validar_valor(clave: str, valor: str, etiqueta: str) -> str | None:
    """Valida formatos básicos antes de permitir avanzar al siguiente campo."""
    clave = clave.casefold()
    etiqueta = etiqueta.casefold()

    if clave in {
        "num",
        "num_membresia",
        "num_version",
        "plazo_meses",
        "vigencia_meses",
        "costo_puntos",
        "limite_canjes",
        "version_plan_actual",
    } or (clave == "movimiento" and "puntos" in etiqueta):
        try:
            numero = int(valor)
        except ValueError:
            return "Este campo debe ser un número entero."
        if clave == "movimiento" and numero == 0:
            return "El movimiento debe ser distinto de cero."
        if clave != "movimiento" and numero <= 0:
            return "Este número debe ser mayor que cero."
        return None

    if clave in {
        "monto_base",
        "cashback_aplicado",
        "precio",
        "porcentaje",
        "monto_minimo",
        "limite_min_mensual",
    } or (clave == "movimiento" and "cashback" in etiqueta):
        try:
            numero = Decimal(valor)
            if not numero.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            return "Este campo debe ser un número decimal válido."
        if clave == "porcentaje" and not 0 <= numero <= 1:
            return "El porcentaje debe estar entre cero y uno."
        if clave in {"monto_base", "precio"} and numero <= 0:
            return "Este importe debe ser mayor que cero."
        if clave in {"cashback_aplicado", "monto_minimo", "limite_min_mensual"} and numero < 0:
            return "Este importe no puede ser negativo."
        if clave == "movimiento" and numero == 0:
            return "El movimiento debe ser distinto de cero."
        return None

    if clave in {"fecha_inicio", "fecha_final"}:
        try:
            date.fromisoformat(valor)
        except ValueError:
            return "La fecha debe tener formato AAAA-MM-DD."
        return None

    if clave == "correo" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
        return "Ingresa un correo electrónico válido."

    if clave == "telefono" and not re.fullmatch(r"\d{10}", valor):
        return "El teléfono debe contener exactamente 10 dígitos."

    if clave == "aplica_en" and valor.upper() not in {"CONTRATACION", "RENOVACION", "AMBAS"}:
        return "Usa CONTRATACION, RENOVACION o AMBAS."

    if clave == "estado" and valor.upper() not in {"ACTIVA", "SUSPENDIDA", "CANCELADA"}:
        return "Usa ACTIVA, SUSPENDIDA o CANCELADA."

    if clave == "dias_aplicables":
        try:
            dias = [int(dia.strip()) for dia in valor.split(",")]
        except ValueError:
            return "Los días deben ser números separados por comas."
        if any(dia < 1 or dia > 7 for dia in dias):
            return "Los días aplicables deben estar entre 1 y 7."

    return None


def _mostrar_resumen(campos: list[dict], valores: dict) -> None:
    """Muestra un resumen de los valores del formulario con Rich."""
    _consola.clear()
    _mostrar_tabla_campos(campos, valores, "Resumen")


def _dibujar_formulario(
    campos: list[dict],
    valores: dict,
    mensaje_error: str | None = None,
) -> None:
    """Redibuja el formulario completo antes de solicitar un valor."""
    _consola.clear()
    _mostrar_tabla_campos(campos, valores, "Formulario")
    if mensaje_error:
        _consola.print(f"[yellow]Error: {mensaje_error}[/yellow]")
    _mostrar_pie_formulario()


def _mostrar_tabla_campos(
    campos: list[dict],
    valores: dict,
    titulo: str,
) -> None:
    """Muestra todos los campos y los valores capturados hasta el momento."""
    tabla = Table(title=titulo, header_style=ESTILO_TABLA, show_lines=True)
    tabla.add_column("Campo")
    tabla.add_column("Valor")

    for campo in campos:
        clave      = campo["clave"]
        if clave.startswith("_"):
            continue
        etiqueta   = campo["etiqueta"]
        contrasena = campo.get("contrasena", False)
        valor = valores.get(clave, "")
        valor_mostrado = "••••••••" if contrasena and valor else valor
        tabla.add_row(etiqueta, "" if valor_mostrado is None else str(valor_mostrado))

    _consola.print(tabla)


def _mostrar_pie_formulario() -> None:
    """Muestra la ayuda del formulario separada de los prompts de entrada."""
    _consola.print(
        Panel(
            f"Escribe [bold]{_COMANDO_CANCELAR}[/bold] en cualquier campo para cancelar.",
            border_style="dim",
            title="Ayuda",
            title_align="left",
        )
    )
