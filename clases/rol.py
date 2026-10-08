class Rol:
    def __init__(self, num, nombre, descripcion):
        self.num = num
        self.nombre = nombre
        self.descripcion = descripcion

    def info(self):
        print(f"Numero de rol: {self.num}")
        print(f"Rol: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
