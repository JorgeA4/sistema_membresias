class Renovacion:
    def __init__(self, num, fecha, monto_pagado, membresia):
        self.num = num
        self.fecha = fecha
        self.monto_pagado = monto_pagado
        self.membresia = membresia #FK

    def info(self):
        print(f"Numero de miembro: {self.num}")
        print(f"Numero de membresia: {self.membresia}")
        print(f"Monto pagado: {self.monto_pagado}")
        print(f"Fecha de renovacion: {self.fecha}")
