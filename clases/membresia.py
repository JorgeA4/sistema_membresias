class Membresia:
    def __init__(self, num, num_miembro, fecha_activacion, fecha_vencimiento, num_plan):
        self.num = num
        self.num_miembro = num_miembro
        self.fecha_activacion = fecha_activacion
        self.fecha_vencimiento = fecha_vencimiento
        self.num_plan = num_plan

    class estado(Enum):
        ACTIVA = 1
        SUSPENDIDA = 2
        CANCELADA = 3
    ACTIVA = estado.ACTIVA
    SUSPENDIDA = estado.SUSPENDIDA
    CANCELADA = estado.CANCELADA

    def definir_estado(self, estado):
        if estado in Membresia.estado:
            self.estado = estado
        else:
            raise ValueError("El estado ingresado es invalido.")

    def info():
        print(f"Numero de membresia: {self.num}")
        print(f"Numero de miembro: {self.num_miembro}")
        print(f"Fecha de activacion: {self.fecha_activacion}")
        print(f"Fecha de vencimiento: {self.fecha_vencimiento}")
        print(f"Numero de plan: {self.num_plan}")
        print(f"Estado de la membresia: {self.estado}")
