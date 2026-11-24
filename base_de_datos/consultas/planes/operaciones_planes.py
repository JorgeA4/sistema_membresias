"""Acceso persistente de planes."""

from base_de_datos.ejecutor import usar_conexion

# Guarda una configuración nueva o actualiza la existente.
def _guardar_configuracion(conexion, configuracion, tabla, columnas, valores):
    if configuracion is None:
        return None
    with conexion.cursor() as cursor:
        if configuracion.num is None:
            nombres = ",\n".join(
                f"                        {columna}"
                for columna in columnas
            )
            marcadores = ",\n".join(
                "                        %s"
                for _ in valores
            )
            consulta = f"""
                INSERT INTO {tabla}
                    ({nombres})
                VALUES
                    ({marcadores})
            """
            cursor.execute(
                consulta,
                valores,
            )
            configuracion.num = cursor.lastrowid
        else:
            asignaciones = ",\n".join(
                f"                        {columna} = %s"
                for columna in columnas
            )
            consulta = f"""
                UPDATE {tabla}
                SET
                    {asignaciones}
                WHERE
                    num = %s
            """
            cursor.execute(
                consulta,
                valores + (configuracion.num,),
            )
    return configuracion.num

# Guarda un plan nuevo o actualizado.
def guardar_plan(plan):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO plan
                    (
                        codigo,
                        nombre,
                        descripcion
                    )
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = %s,
                    descripcion = %s
                """,
                (plan.codigo, plan.nombre, plan.descripcion, plan.nombre, plan.descripcion),
            )

# Elimina un plan por su código.
def eliminar_plan(codigo):
    consulta = """
        DELETE FROM plan
        WHERE codigo = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo,))

# Guarda una versión de plan y sus configuraciones.
def guardar_version_plan(version_plan):
    with usar_conexion() as conexion:
        cashback = version_plan.config_cashback
        puntos = version_plan.config_puntos
        descuento = version_plan.config_descuento
        valores_cashback = ()
        if cashback is not None:
            valores_cashback = (
                cashback.porcentaje,
                cashback.limite_min_mensual,
            )
        id_cashback = _guardar_configuracion(
            conexion, cashback, "config_cashback",
            ("porcentaje", "limite_min_mensual"),
            valores_cashback,
        )
        valores_puntos = ()
        if puntos is not None:
            valores_puntos = (
                puntos.porcentaje,
                puntos.vigencia_meses,
            )
        id_puntos = _guardar_configuracion(
            conexion, puntos, "config_puntos", ("porcentaje", "vigencia_meses"),
            valores_puntos,
        )
        valores_descuento = ()
        if descuento is not None:
            valores_descuento = (
                descuento.porcentaje,
                descuento.monto_minimo,
            )
        id_descuento = _guardar_configuracion(
            conexion, descuento, "config_descuento",
            ("porcentaje", "monto_minimo"),
            valores_descuento,
        )
        if descuento is not None:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM dia_aplicable_desc
                    WHERE config_descuento = %s
                    """,
                    (id_descuento,),
                )
                for dia in descuento.dias_aplicables:
                    valor = dia
                    if hasattr(dia, "dia_semana"):
                        valor = dia.dia_semana
                    cursor.execute(
                        """
                        INSERT INTO dia_aplicable_desc
                            (
                                config_descuento,
                                dia_semana
                            )
                        VALUES
                            (%s, %s)
                        """,
                        (id_descuento, valor),
                    )
        base = version_plan.version_base_de_promo
        id_base = None
        if base is not None:
            id_base = base.num
        valores = (
            version_plan.fecha_inicio, version_plan.fecha_final,
            version_plan.precio, version_plan.plazo_meses,
            version_plan.aplica_en.value, version_plan.plan.codigo,
            id_cashback, id_puntos, id_descuento, id_base,
        )
        with conexion.cursor() as cursor:
            if version_plan.num is None:
                cursor.execute(
                    """
                    INSERT INTO version_plan
                        (
                            fecha_inicio,
                            fecha_final,
                            precio,
                            plazo_meses,
                            aplica_en,
                            plan,
                            config_cashback,
                            config_puntos,
                            config_descuento,
                            version_base_de_promo
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores,
                )
                object.__setattr__(version_plan, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    """
                    UPDATE version_plan
                    SET
                        fecha_inicio = %s,
                        fecha_final = %s,
                        precio = %s,
                        plazo_meses = %s,
                        aplica_en = %s,
                        plan = %s,
                        config_cashback = %s,
                        config_puntos = %s,
                        config_descuento = %s,
                        version_base_de_promo = %s
                    WHERE
                        num = %s
                    """,
                    valores + (version_plan.num,),
                )

# Elimina una versión de plan por su número.
def eliminar_version_plan(num):
    consulta = """
        DELETE FROM version_plan
        WHERE num = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num,))
