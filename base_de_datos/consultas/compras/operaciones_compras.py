
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

# guarda una transaccion de puntos
def guardar_transaccion_puntos(transaccion):
    compra = None
    if transaccion.compra is not None:
        compra = transaccion.compra.num
    version_recompensa = None
    if transaccion.version_recompensa is not None:
        version_recompensa = transaccion.version_recompensa.num
    with usar_conexion() as conexion:
        valores = (
            transaccion.movimiento, transaccion.saldo, transaccion.fecha,
            transaccion.concepto,
            compra,
            version_recompensa,
            transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    """
                    INSERT INTO transaccion_puntos
                        (
                            movimiento,
                            saldo,
                            fecha,
                            concepto,
                            compra,
                            version_recompensa,
                            membresia
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE transaccion_puntos
                    SET
                        movimiento = %s,
                        saldo = %s,
                        fecha = %s,
                        concepto = %s,
                        compra = %s,
                        version_recompensa = %s,
                        membresia = %s
                    WHERE
                        num = %s
                    """,
                    valores + (transaccion.num,),
                )

# guarda una transaccion de cashback
def guardar_transaccion_cashback(transaccion):
    compra = None
    if transaccion.compra is not None:
        compra = transaccion.compra.num
    with usar_conexion() as conexion:
        valores = (
            transaccion.monto, transaccion.saldo, transaccion.fecha,
            transaccion.concepto,
            compra,
            transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    """
                    INSERT INTO transaccion_cashback
                        (
                            monto,
                            saldo,
                            fecha,
                            concepto,
                            compra,
                            membresia
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE transaccion_cashback
                    SET
                        monto = %s,
                        saldo = %s,
                        fecha = %s,
                        concepto = %s,
                        compra = %s,
                        membresia = %s
                    WHERE
                        num = %s
                    """,
                    valores + (transaccion.num,),
                )
