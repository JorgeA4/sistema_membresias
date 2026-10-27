class Compra:
    def __init__(self, num, monto, usuario):
        self.num = num
        self.monto = monto
        self.usuario = usuario

    def info(self):
        print(f"Numero de compra: {self.num}")
        print(f"Numero de usuario admin: {self.usuario}")
        print(f"Monto de la compra: {self.monto}")
