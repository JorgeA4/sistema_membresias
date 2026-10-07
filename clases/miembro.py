class miembro:
    def atributos():
        num = 0
        nombre = str(input("Favor de ingresar su nombre: "))
        primer_apellido = str(input("Primer apellido: "))
        segundo_apellido = str(input("Segundo apellido: "))
        telefono = int(input("Ingrese su numero de telefono: "))
        correo = str(input("Ingrese su correo electronico: "))

        return num, nombre, primer_apellido, segundo_apellido, telefono, correo

    def info(num, nombre, primer_apellido, segundo_apellido,  telefono, correo):
        print(f"{num}\n{nombre}\n{primer_apellido}\n{segundo_apellido}\n{telefono}\n{correo}")

    def main():
        num, nombre, primer_apellido, segundo_apellido,  telefono, correo = miembro.atributos()
        miembro.info(num, nombre, primer_apellido, segundo_apellido,  telefono, correo)

miembro.main()