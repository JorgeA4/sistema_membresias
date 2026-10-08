class Administrador:
    def __init__(self, num, num_rol, nombre, primer_apellido, segundo_apellido, correo, contrasena, telefono):
        self.num = num
        self.num_rol = num_rol
        self.nombre = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.correo = correo
        self.contrasena = contrasena
        self.telefono = telefono

    def info(self):
        print(f"Numero de usuario: {self.num}")
        print(f"Numero de rol: {self.num_rol}")
        print(f"Nombre: {self.nombre}")
        print(f"Primer apellido: {self.primer_apellido}")
        print(f"Segundo apellido: {self.segundo_apellido}")
        print(f"Correo: {self.correo}")
        print(f"Contrasena: {self.contrasena}")
        print(f"Telefono: {self.telefono}")
