
from base_de_datos.ejecutor import usar_conexion


# guarda una compra nueva o actualizada
def guardar_compra(compra):
    with usar_conexion() as conexion:
        valores = (
            compra.monto_base, compra.porcentaje_descuento,
            compra.descuento_nominal, compra.cashback_aplicado,
            compra.monto_final, compra.membresia.num, compra.usuario.num,
        )
        with conexion.cursor() as cursor:
            if compra.num is None:
                cursor.execute(
                    """
                    INSERT INTO compra
                        (
                            monto_base,
                            porcentaje_descuento,
                            descuento_nominal,
                            cashback_aplicado,
                            monto_final,
                            membresia,
                            usuario
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                compra.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE compra
                    SET
                        monto_base = %s,
                        porcentaje_descuento = %s,
                        descuento_nominal = %s,
                        cashback_aplicado = %s,
                        monto_final = %s,
                        membresia = %s,
                        usuario = %s
                    WHERE
                        num = %s
                    """,
                    valores + (compra.num,),
                )
