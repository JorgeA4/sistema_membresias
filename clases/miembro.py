class Miembro:
    def __init__(self, num, nombre, primer_apellido, segundo_apellido, telefono, correo):
        self.num = num
        self.nombre = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.telefono = telefono
        self.correo = correo

    def info(self):
        print(f"Numero: {self.num}")
        print(f"Nombre de usuario: {self.nombre}")
        print(f"Primer Apellido: {self.primer_apellido}")
        print(f"Segundo Apellido: {self.segundo_apellido}")
        print(f"Numero de Telefono: {self.telefono}")
        print(f"Correo Electronico: {self.correo}")
