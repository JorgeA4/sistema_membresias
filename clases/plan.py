class Plan:
    def __init__(self, es_gratuita, num, nombre, descripcion):
        self.es_gratuita = False if es_gratuita == "False" else True
        self.num = num
        self.nombre = nombre
        self.descripcion = descripcion

    def info(self):
        if self.es_gratuita == True:
            print("Su plan es gratuito")
        else:
            print("Su plan es de pago")

        print(f"Numero de plan: {self.num}")
        print(f"Nombre de usuario: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
