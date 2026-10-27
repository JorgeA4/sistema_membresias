from enum import Enum

class TransaccionPuntos:
    class Tipo(Enum):
        INGRESO = 1
        EGRESO = 2
        AJUSTE = 3

    def __init__(self, num, fecha, cantidad, saldo, miembro, membresia, tipo, compra, canje):
        self.num = num # PK
        self.fecha = fecha
        self.cantidad = cantidad
        self.saldo = saldo
        self.miembro = miembro # FK
        self.membresia = membresia # FK
        self.tipo = TransaccionPuntos.Tipo(tipo) # FK
        self.compra = compra # FK
        self.canje = canje # FK
    
    def definir_estado(self, tipo):
        if tipo in TransaccionPuntos.Tipo:
            self.tipo = tipo
        else:
            raise ValueError("El tipo de transaccion ingresado es invalido.")
    
