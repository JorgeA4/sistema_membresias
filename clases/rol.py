class Rol:
    def __init__(self, codigo, nombre, descripcion):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion

    def info(self):
        print(f"Numero de rol: {self.codigo}")
        print(f"Rol: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
