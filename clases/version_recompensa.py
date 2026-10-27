from datetime import date, datetime

class VersionRecompensa:
    def __init__(self, num, costo_puntos, fecha_inicio, fecha_final, limite_canjes, recompensa):
        self.num = num
        self.costo_puntos = costo_puntos
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.limite_canjes = limite_canjes
        self.recompensa = recompensa

    def esta_vigente(self):
        return self.fecha_inicio <= date.today() <= self.fecha_final
        
    def info(self):
        print(f"Numero de version: {self.num}")
        print(f"Costo en puntos: {self.costo_puntos}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Fecha de finalizacion: {self.fecha_final}")
        print(f"Limite de canjes: {self.limite_canjes}")
