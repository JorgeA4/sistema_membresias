class Recompensa:
    def __init__(self, num, nombre, descripcion):
        self.num = num
        self.nombre = nombre
        self.descripcion = descripcion

    def info(self):
        print(f"Numero de recompensa: {self.num}")
        print(f"Recompensa: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
