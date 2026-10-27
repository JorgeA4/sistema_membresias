class Recompensa:
    def __init__(self, codigo, nombre, descripcion):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion

    def info(self):
        print(f"Numero de recompensa: {self.codigo}")
        print(f"Recompensa: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
