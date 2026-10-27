from enum import Enum

class Membresia:
    class Estado(Enum):
        ACTIVA = 1
        SUSPENDIDA = 2
        CANCELADA = 3

    def __init__(self, num, fecha_activacion, fecha_vencimiento, miembro, estado):
        self.num = num
        self.fecha_activacion = fecha_activacion
        self.fecha_vencimiento = fecha_vencimiento
        self.miembro = miembro  # FK
        self.estado = Membresia.Estado(estado) #self.estado.value = FK

    def definir_estado(self, estado):
        if estado in Membresia.Estado:
            self.estado = estado
        else:
            raise ValueError("El estado ingresado es invalido.")

    def info(self):
        print(f"Numero de membresia: {self.num}")
        print(f"Fecha de activacion: {self.fecha_activacion}")
        print(f"Fecha de vencimiento: {self.fecha_vencimiento}")
        print(f"Miembro: {self.miembro}")
        print(f"Estado de la membresia: {self.estado}")
