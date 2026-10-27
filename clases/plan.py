class Plan:
    def __init__(self, codigo, nombre, descripcion, es_gratuita, periodo_rembolso):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.es_gratuita = es_gratuita
        self.periodo_rembolso = periodo_rembolso

    def info(self):
        if self.es_gratuita == True:
            print("Su plan es gratuito")
        else:
            print("Su plan es de pago")

        print(f"Numero de plan: {self.codigo}")
        print(f"Nombre de usuario: {self.nombre}")
        print(f"Descripcion: {self.descripcion}")
