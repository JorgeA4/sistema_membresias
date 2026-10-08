class TransaccionPuntos:
    def __init__(self, num, num_miembro, num_membresia, cantidad, fecha, tipo, descripcion):
        self.num = num
        self.num_miembro = num_miembro
        self.num_membresia = num_membresia
        self.cantidad = cantidad
        self.fecha = fecha
        self.descripcion = descripcion

    class tipo(Enum):
        JA = 1
        JE = 2
        JI = 3
        JOrgito_observa = 4
    JA = tipo.JA
    JE = tipo.JE
    JI = tipo.JI
    JOrgito_observa = tipo.JOrgito_observa
    
    def definir_estado(self, tipo):
        if tipo in TransaccionPuntos.tipo:
            self.tipo = tipo
        else:
            raise ValueError("El tipo ingresado es invalido.")
    
