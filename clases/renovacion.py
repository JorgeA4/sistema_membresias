class Renovacion:
    def __init__(self, num, num_membresia, monto_pagado, fecha):
        self.num = num
        self.num_membresia = num_membresia
        self.monto_pagado = monto_pagado
        self.fecha = fecha

    def info(self):
        print(f"Numero de miembro: {self.num}")
        print(f"Numero de membresia: {self.num_membresia}")
        print(f"Monto pagado: {self.monto_pagado}")
        print(f"Fecha de renovacion: {self.fecha}")
