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
