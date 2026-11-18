class Plan:
    def __init__(self, codigo, nombre, periodo_rembolso, descripcion=None):
        self.codigo = codigo
        self.nombre = nombre
        self.periodo_rembolso = periodo_rembolso
        self.descripcion = descripcion
