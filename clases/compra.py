class Compra:
    def __init__(self, num, num_membresia, num_usuario_admin, monto):
        self.num = num
        self.num_membresia = num_membresia
        self.num_usuario_admin = num_usuario_admin
        self.monto = monto

    def info(self):
        print(f"Numero de compra: {self.num}")
        print(f"Numero de membresia: {self.num_membresia}")
        print(f"Numero de usuario admin: {self.num_usuario_admin}")
        print(f"Monto de la compra: {self.monto}")
