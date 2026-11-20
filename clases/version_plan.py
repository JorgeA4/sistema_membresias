from datetime import date
from enum import Enum

from utilidades.excepciones import DatosInvalidos


class TipoAplicacionPlan(Enum):
    CONTRATACION = "CONTRATACION"
    RENOVACION = "RENOVACION"
    AMBAS = "AMBAS"


class ConfigCashback:
    def __init__(self, num, porcentaje, limite_min_mensual=None):
        self.num = num
        self.porcentaje = porcentaje
        self.limite_min_mensual = limite_min_mensual


class ConfigPuntos:
    def __init__(self, num, porcentaje, vigencia_meses=None):
        self.num = num
        self.porcentaje = porcentaje
        self.vigencia_meses = vigencia_meses


class ConfigDescuento:
    def __init__(self, num, porcentaje, monto_minimo=None, dias_aplicables=None):
        self.num = num
        self.porcentaje = porcentaje
        self.monto_minimo = monto_minimo
        self.dias_aplicables = [] if dias_aplicables is None else dias_aplicables


class DiaAplicableDesc:
    def __init__(self, config_descuento, dia_semana):
        self.config_descuento = config_descuento
        self.dia_semana = dia_semana


class VersionPlan:
    _atributos_inmutables = (
        "num",
        "fecha_inicio",
        "fecha_final",
        "precio",
        "plazo_meses",
        "aplica_en",
        "plan",
        "config_cashback",
        "config_puntos",
        "config_descuento",
        "version_base_de_promo",
    )

    def __init__(
        self,
        num,
        fecha_inicio,
        fecha_final,
        precio,
        plazo_meses,
        aplica_en,
        plan,
        config_cashback=None,
        config_puntos=None,
        config_descuento=None,
        version_base_de_promo=None,
    ):
        self.num = num
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.precio = precio
        self.plazo_meses = plazo_meses
        self.aplica_en = TipoAplicacionPlan(aplica_en)
        self.plan = plan
        self.config_cashback = config_cashback
        self.config_puntos = config_puntos
        self.config_descuento = config_descuento
        self.version_base_de_promo = version_base_de_promo
        self._inicializada = True

    def __setattr__(self, nombre, valor):
        if getattr(self, "_inicializada", False) and nombre in self._atributos_inmutables:
            raise AttributeError("Las condiciones de una version de plan son inmutables.")
        object.__setattr__(self, nombre, valor)

    def esta_vigente(self, fecha=None):
        if fecha is None:
            fecha = date.today()
        return self.fecha_inicio <= fecha <= self.fecha_final

    def finalizar_vigencia(self, fecha):
        if fecha < self.fecha_inicio or fecha > self.fecha_final:
            raise DatosInvalidos("La fecha final debe estar dentro de la vigencia actual.")
        object.__setattr__(self, "fecha_final", fecha)
