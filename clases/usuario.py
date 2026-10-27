class Usuario:
    def __init__(self, num, nombre, primer_apellido, segundo_apellido, telefono, correo, contrasena, rol):
        self.num = num
        self.nombre = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido        
        self.telefono = telefono
        self.correo = correo
        self.contrasena = contrasena
        self.rol = rol

    def info(self):
        print(f"Numero de usuario: {self.num}")
        print(f"Numero de rol: {self.rol}")
        print(f"Nombre: {self.nombre}")
        print(f"Primer apellido: {self.primer_apellido}")
        print(f"Segundo apellido: {self.segundo_apellido}")
        print(f"Correo: {self.correo}")
        print(f"Contrasena: {self.contrasena}")
        print(f"Telefono: {self.telefono}")
