from datetime import date


class VersionRecompensa:
    _atributos_inmutables = (
        "num",
        "fecha_inicio",
        "fecha_final",
        "costo_puntos",
        "limite_canjes",
        "recompensa",
    )

    def __init__(self, num, costo_puntos, fecha_inicio, fecha_final, limite_canjes, recompensa):
        self.num = num
        self.costo_puntos = costo_puntos
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.limite_canjes = limite_canjes
        self.recompensa = recompensa
        self._inicializada = True

    def __setattr__(self, nombre, valor):
        if getattr(self, "_inicializada", False) and nombre in self._atributos_inmutables:
            raise AttributeError("Las condiciones de una version de recompensa son inmutables.")
        object.__setattr__(self, nombre, valor)

    def esta_vigente(self, fecha=None):
        if fecha is None:
            fecha = date.today()
        return self.fecha_inicio <= fecha <= self.fecha_final

    def finalizar_vigencia(self, fecha):
        if fecha < self.fecha_inicio or fecha > self.fecha_final:
            raise ValueError("La fecha final debe estar dentro de la vigencia actual.")
        object.__setattr__(self, "fecha_final", fecha)
