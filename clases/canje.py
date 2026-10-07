class Canje:
    def atributos():
        num = 0
        num_membresia = 0.0
        num_version_recompensa = 0.0
        return num, num_membresia, num_version_recompensa

    #Funciones
    def info():
        print("Informacion basica: Puedes consultar tus puntos actuales aqui!")

    def main():
        num, num_membresia, num_version_recompensa = Canje.atributos()
        Canje.info(num, num_membresia, num_version_recompensa)
    main()