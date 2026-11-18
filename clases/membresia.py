from enum import Enum

class Membresia:
    class Estado(Enum):
        ACTIVA = "ACTIVA"
        SUSPENDIDA = "SUSPENDIDA"
        CANCELADA = "CANCELADA"

    def __init__(self, num, fecha_contratacion, estado, miembro, version_plan_actual=None):
        self.num = num
        self.fecha_contratacion = fecha_contratacion
        self.estado = Membresia.Estado(estado)
        self.miembro = miembro
        self.version_plan_actual = version_plan_actual
