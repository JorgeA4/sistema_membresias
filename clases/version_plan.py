from datetime import date, datetime

class VersionPlan:
    def __init__(self, num, fecha_inicio, fecha_final, precio, puntos_por_peso, porcentaje_descuento, limite_canjes, plazo_meses, plan):
        self.num = num
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.precio = precio
        self.puntos_por_peso = puntos_por_peso
        self.porcentaje_descuento = porcentaje_descuento
        self.limite_canjes = limite_canjes
        self.plazo_meses = plazo_meses
        self.plan = plan #FK

    def esta_vigente(self):
        return self.fecha_inicio <= date.today() <= self.fecha_final

    def info(self):
        print(f"Numero de version: {self.num}")
        print(f"Precio: {self.precio}")
        print(f"Plazo en meses: {self.plazo_meses}")
        print(f"Puntos por peso: {self.puntos_por_peso}")
        print(f"Porcentaje de descuento: {self.porcentaje_descuento}")
        print(f"Limite de canjes: {self.limite_canjes}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Fecha de finalizacion: {self.fecha_final}")
