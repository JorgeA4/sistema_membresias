
from base_de_datos.ejecutor import usar_conexion


# guarda una membresia nueva o actualizada
def guardar_membresia(membresia):
    version_plan = None
    if membresia.version_plan_actual is not None:
        version_plan = membresia.version_plan_actual.num
    with usar_conexion() as conexion:
        valores = (
            membresia.fecha_contratacion, membresia.estado.value,
            membresia.miembro.num,
            version_plan,
        )
        with conexion.cursor() as cursor:
            if membresia.num is None:
                cursor.execute(
                    """
                    INSERT INTO membresia
                        (
                            fecha_contratacion,
                            estado,
                            miembro,
                            version_plan_actual
                        )
                    VALUES
                        (%s, %s, %s, %s)
                    """,
                    valores,
                )
                membresia.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE membresia
                    SET
                        fecha_contratacion = %s,
                        estado = %s,
                        miembro = %s,
                        version_plan_actual = %s
                    WHERE
                        num = %s
                    """,
                    valores + (membresia.num,),
                )

# guarda una renovacion nueva o actualizada
def guardar_renovacion(renovacion):
    with usar_conexion() as conexion:
        valores = (
            renovacion.fecha_pago, renovacion.monto_pagado,
            renovacion.fecha_inicio_periodo, renovacion.fecha_fin_periodo,
            renovacion.membresia.num, renovacion.version_plan_comprado.num,
        )
        with conexion.cursor() as cursor:
            if renovacion.num is None:
                cursor.execute(
                    """
                    INSERT INTO renovacion
                        (
                            fecha_pago,
                            monto_pagado,
                            fecha_inicio_periodo,
                            fecha_fin_periodo,
                            membresia,
                            version_plan_comprado
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                renovacion.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE renovacion
                    SET
                        fecha_pago = %s,
                        monto_pagado = %s,
                        fecha_inicio_periodo = %s,
                        fecha_fin_periodo = %s,
                        membresia = %s,
                        version_plan_comprado = %s
                    WHERE
                        num = %s
                    """,
                    valores + (renovacion.num,),
                )
