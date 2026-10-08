class VersionPlan:
    def __init__(self, num, precio, plazo_mese, puntos_por_peso, porcentaje_descuento, limite_canjes, fecha_inicio, fecha_final):
        self.num = num
        self.precio = precio
        self.plazo_mese = plazo_mese
        self.puntos_por_peso = puntos_por_peso
        self.porcentaje_descuento = porcentaje_descuento
        self.limite_canjes = limite_canjes
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final

    def esta_vigente(self, fecha_actual):
        if self.fecha_inicio <= fecha_actual <= self.fecha_final:
            return True
        else:
            return False

    def info(self):
        print(f"Numero de version: {self.num}")
        print(f"Precio: {self.precio}")
        print(f"Plazo en meses: {self.plazo_mese}")
        print(f"Puntos por peso: {self.puntos_por_peso}")
        print(f"Porcentaje de descuento: {self.porcentaje_descuento}")
        print(f"Limite de canjes: {self.limite_canjes}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Fecha de finalizacion: {self.fecha_final}")
