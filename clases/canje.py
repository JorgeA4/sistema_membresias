class Canje:
    def __init__(self, num, num_membresia, num_version_recompensa):
        self.num = num
        self.num_membresia = num_membresia
        self.num_version_recompensa = num_version_recompensa

    def info(self):
        print(f"Numero de usuario: {self.num}")
        print(f"Numero de membresia: {self.num_membresia}")
        print(f"Version de recompensa: {self.num_version_recompensa}")
