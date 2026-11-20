"""Consultas reales de Nexum y adaptación a los objetos del dominio."""

from contextlib import contextmanager
from contextvars import ContextVar

import pymysql

from base_de_datos.conexion import obtener_conexion
from base_de_datos.mapeadores import (
    mapear_compra,
    mapear_configuracion_cashback,
    mapear_configuracion_descuento,
    mapear_configuracion_puntos,
    mapear_membresia,
    mapear_miembro,
    mapear_plan,
    mapear_recompensa,
    mapear_renovacion,
    mapear_rol,
    mapear_transaccion_cashback,
    mapear_transaccion_puntos,
    mapear_usuario,
    mapear_version_plan,
    mapear_version_recompensa,
)
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    ErrorPersistencia,
    OperacionNoPermitida,
)

# Imports anteriores conservados para referencia y compatibilidad documental.
# from base_de_datos.bd_simulada import transaccion
# from base_de_datos.consultas_simuladas import buscar_miembro_por_correo
# from base_de_datos.consultas_simuladas import buscar_miembro_por_num
# from base_de_datos.consultas_simuladas import obtener_todos_los_miembros
# from base_de_datos.consultas_simuladas import guardar_miembro
# from base_de_datos.consultas_simuladas import eliminar_miembro
# from base_de_datos.consultas_simuladas import buscar_usuario_por_correo
# from base_de_datos.consultas_simuladas import buscar_usuario_por_num
# from base_de_datos.consultas_simuladas import obtener_todos_los_usuarios
# from base_de_datos.consultas_simuladas import guardar_usuario
# from base_de_datos.consultas_simuladas import eliminar_usuario
# from base_de_datos.consultas_simuladas import buscar_plan_por_codigo
# from base_de_datos.consultas_simuladas import obtener_todos_los_planes
# from base_de_datos.consultas_simuladas import guardar_plan
# from base_de_datos.consultas_simuladas import eliminar_plan
# from base_de_datos.consultas_simuladas import obtener_versiones_de_plan
# from base_de_datos.consultas_simuladas import buscar_version_plan_por_num
# from base_de_datos.consultas_simuladas import buscar_version_plan_vigente
# from base_de_datos.consultas_simuladas import guardar_version_plan
# from base_de_datos.consultas_simuladas import buscar_membresia_por_num
# from base_de_datos.consultas_simuladas import buscar_membresia_de_miembro
# from base_de_datos.consultas_simuladas import guardar_membresia
# from base_de_datos.consultas_simuladas import buscar_recompensa_por_codigo
# from base_de_datos.consultas_simuladas import obtener_todas_las_recompensas
# from base_de_datos.consultas_simuladas import guardar_recompensa
# from base_de_datos.consultas_simuladas import eliminar_recompensa
# from base_de_datos.consultas_simuladas import obtener_versiones_de_recompensa
# from base_de_datos.consultas_simuladas import buscar_version_recompensa_por_num
# from base_de_datos.consultas_simuladas import buscar_version_recompensa_vigente
# from base_de_datos.consultas_simuladas import guardar_version_recompensa
# from base_de_datos.consultas_simuladas import buscar_compra_por_num
# from base_de_datos.consultas_simuladas import guardar_compra
# from base_de_datos.consultas_simuladas import obtener_compras_de_membresia
# from base_de_datos.consultas_simuladas import guardar_renovacion
# from base_de_datos.consultas_simuladas import obtener_renovaciones_de_membresia
# from base_de_datos.consultas_simuladas import guardar_transaccion_puntos
# from base_de_datos.consultas_simuladas import obtener_transacciones_de_miembro
# from base_de_datos.consultas_simuladas import obtener_saldo_de_miembro
# from base_de_datos.consultas_simuladas import guardar_transaccion_cashback
# from base_de_datos.consultas_simuladas import obtener_transacciones_cashback_de_membresia
# from base_de_datos.consultas_simuladas import obtener_saldo_cashback_de_membresia
# from base_de_datos.consultas_simuladas import buscar_rol_por_codigo
# from base_de_datos.consultas_simuladas import obtener_todos_los_roles

_conexion_actual = ContextVar("conexion_nexum", default=None)


def _traducir_error_sql(error):
    """Convierte errores conocidos de MariaDB en errores del dominio."""
    if not isinstance(error, pymysql.MySQLError):
        return error

    codigo = error.args[0] if error.args else None
    if codigo == 1062:
        return DatosInvalidos("Ya existe un registro con esos datos.")
    if codigo == 1451:
        return OperacionNoPermitida(
            "No se puede eliminar o modificar un registro con historial relacionado."
        )
    if codigo == 1452:
        return EntidadNoEncontrada("La entidad relacionada no existe.")
    if codigo in (1048, 1265, 1406, 3819):
        return DatosInvalidos("Los datos no cumplen las restricciones de la base de datos.")
    return ErrorPersistencia("No fue posible completar la operación en la base de datos.")


@contextmanager
def _usar_conexion():
    conexion = _conexion_actual.get()
    propia = conexion is None
    if propia:
        conexion = obtener_conexion()
    try:
        yield conexion
        if propia:
            conexion.commit()
    except Exception as error:
        if propia:
            conexion.rollback()
        error_dominio = _traducir_error_sql(error)
        if error_dominio is not error:
            raise error_dominio from error
        raise
    finally:
        if propia:
            conexion.close()


@contextmanager
def transaccion():
    """Agrupa varias operaciones en una única transacción MariaDB."""
    conexion_existente = _conexion_actual.get()
    if conexion_existente is not None:
        yield
        return

    conexion = obtener_conexion()
    token = _conexion_actual.set(conexion)
    try:
        yield
        conexion.commit()
    except Exception as error:
        conexion.rollback()
        error_dominio = _traducir_error_sql(error)
        if error_dominio is not error:
            raise error_dominio from error
        raise
    finally:
        _conexion_actual.reset(token)
        conexion.close()


def _fila(cursor):
    return cursor.fetchone()


def _filas(cursor):
    return cursor.fetchall()


def _obtener_rol_conexion(conexion, codigo):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM rol WHERE codigo = %s", (codigo,))
        return mapear_rol(_fila(cursor))


def _obtener_usuario_conexion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM usuario WHERE num = %s", (num,))
        fila = _fila(cursor)
    return mapear_usuario(fila, _obtener_rol_conexion(conexion, fila["rol"])) if fila else None


def _obtener_miembro_conexion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM miembro WHERE num = %s", (num,))
        return mapear_miembro(_fila(cursor))


def _obtener_plan_conexion(conexion, codigo):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM plan WHERE codigo = %s", (codigo,))
        return mapear_plan(_fila(cursor))


def _obtener_recompensa_conexion(conexion, codigo):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM recompensa WHERE codigo = %s", (codigo,))
        return mapear_recompensa(_fila(cursor))


def _consulta_version_plan(conexion, num):
    consulta = """
        SELECT vp.num, vp.fecha_inicio, vp.fecha_final, vp.precio,
               vp.plazo_meses, vp.aplica_en, vp.plan,
               vp.config_cashback, vp.config_puntos, vp.config_descuento,
               vp.version_base_de_promo,
               cc.num AS config_cashback_num,
               cc.porcentaje AS config_cashback_porcentaje,
               cc.limite_min_mensual AS config_cashback_limite,
               cp.num AS config_puntos_num,
               cp.porcentaje AS config_puntos_porcentaje,
               cp.vigencia_meses AS config_puntos_vigencia,
               cd.num AS config_descuento_num,
               cd.porcentaje AS config_descuento_porcentaje,
               cd.monto_minimo AS config_descuento_minimo
        FROM version_plan vp
        JOIN plan p ON p.codigo = vp.plan
        LEFT JOIN config_cashback cc ON cc.num = vp.config_cashback
        LEFT JOIN config_puntos cp ON cp.num = vp.config_puntos
        LEFT JOIN config_descuento cd ON cd.num = vp.config_descuento
        WHERE vp.num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    plan = _obtener_plan_conexion(conexion, fila["plan"])
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT dia_semana FROM dia_aplicable_desc "
            "WHERE config_descuento = %s ORDER BY dia_semana",
            (fila["config_descuento_num"],),
        )
        dias = [registro["dia_semana"] for registro in _filas(cursor)]
    version_base = (
        _consulta_version_plan(conexion, fila["version_base_de_promo"])
        if fila["version_base_de_promo"] is not None else None
    )
    return mapear_version_plan(
        fila,
        plan,
        mapear_configuracion_cashback(fila),
        mapear_configuracion_puntos(fila),
        mapear_configuracion_descuento(fila, dias),
        version_base,
    )


def _consulta_version_recompensa(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM version_recompensa WHERE num = %s", (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_version_recompensa(
        fila, _obtener_recompensa_conexion(conexion, fila["recompensa"])
    )


def _consulta_membresia(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM membresia WHERE num = %s", (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_membresia(
        fila,
        _obtener_miembro_conexion(conexion, fila["miembro"]),
        _consulta_version_plan(conexion, fila["version_plan_actual"])
        if fila["version_plan_actual"] is not None else None,
    )


# Miembro
def buscar_miembro_por_correo(correo):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM miembro WHERE correo = %s", (correo,))
            return mapear_miembro(_fila(cursor))


def buscar_miembro_por_num(num):
    with _usar_conexion() as conexion:
        return _obtener_miembro_conexion(conexion, num)


def obtener_todos_los_miembros():
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM miembro ORDER BY num")
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_obtener_miembro_conexion(conexion, num) for num in numeros]


def buscar_miembros(filtros):
    """Busca miembros usando filtros opcionales y su membresía actual."""
    consulta = """
        SELECT mi.num
        FROM miembro mi
        LEFT JOIN membresia me ON me.num = (
            SELECT m2.num
            FROM membresia m2
            WHERE m2.miembro = mi.num
            ORDER BY (m2.estado = 'CANCELADA'), m2.num DESC
            LIMIT 1
        )
        WHERE 1 = 1
    """
    parametros = []
    filtros_texto = (
        ("nombre", "mi.nombre"),
        ("primer_apellido", "mi.primer_apellido"),
        ("correo", "mi.correo"),
        ("telefono", "mi.telefono"),
    )
    for clave, columna in filtros_texto:
        valor = filtros.get(clave)
        if valor:
            consulta += f" AND {columna} LIKE %s"
            parametros.append(f"%{valor}%")

    if filtros.get("estado"):
        consulta += " AND me.estado = %s"
        parametros.append(filtros["estado"])
    if filtros.get("version_plan_actual") is not None:
        consulta += " AND me.version_plan_actual = %s"
        parametros.append(filtros["version_plan_actual"])
    consulta += " ORDER BY mi.num"

    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, parametros)
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_obtener_miembro_conexion(conexion, num) for num in numeros]


def guardar_miembro(miembro):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            valores = (
                miembro.nombre, miembro.primer_apellido,
                miembro.segundo_apellido, miembro.telefono, miembro.correo,
                miembro.contraseña, miembro.fecha_registro,
            )
            if miembro.num is None:
                cursor.execute(
                    "INSERT INTO miembro "
                    "(nombre, primer_apellido, segundo_apellido, telefono, "
                    "correo, `contraseña`, fecha_registro) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)", valores,
                )
                miembro.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE miembro SET nombre=%s, primer_apellido=%s, "
                    "segundo_apellido=%s, telefono=%s, correo=%s, "
                    "`contraseña`=%s, fecha_registro=%s WHERE num=%s",
                    valores + (miembro.num,),
                )


def eliminar_miembro(num):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM miembro WHERE num = %s", (num,))


def tiene_historial_miembro(num):
    """Indica si el miembro tiene al menos una membresía registrada."""
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM membresia WHERE miembro=%s) "
                "AS tiene_historial",
                (num,),
            )
            return bool(_fila(cursor)["tiene_historial"])


# Usuario
def buscar_usuario_por_correo(correo):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
            fila = _fila(cursor)
        return mapear_usuario(fila, _obtener_rol_conexion(conexion, fila["rol"])) if fila else None


def buscar_usuario_por_num(num):
    with _usar_conexion() as conexion:
        return _obtener_usuario_conexion(conexion, num)


def obtener_todos_los_usuarios():
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM usuario ORDER BY num")
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_obtener_usuario_conexion(conexion, num) for num in numeros]


def guardar_usuario(usuario):
    with _usar_conexion() as conexion:
        valores = (
            usuario.nombre, usuario.primer_apellido, usuario.segundo_apellido,
            usuario.telefono, usuario.correo, usuario.contraseña,
            usuario.fecha_registro, usuario.rol.codigo,
        )
        with conexion.cursor() as cursor:
            if usuario.num is None:
                cursor.execute(
                    "INSERT INTO usuario (nombre, primer_apellido, "
                    "segundo_apellido, telefono, correo, `contraseña`, "
                    "fecha_registro, rol) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    valores,
                )
                usuario.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE usuario SET nombre=%s, primer_apellido=%s, "
                    "segundo_apellido=%s, telefono=%s, correo=%s, "
                    "`contraseña`=%s, fecha_registro=%s, rol=%s WHERE num=%s",
                    valores + (usuario.num,),
                )


def eliminar_usuario(num):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM usuario WHERE num = %s", (num,))


def tiene_historial_usuario(num):
    """Indica si el usuario tiene al menos una compra registrada."""
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM compra WHERE usuario=%s) "
                "AS tiene_historial",
                (num,),
            )
            return bool(_fila(cursor)["tiene_historial"])


# Plan y VersionPlan
def buscar_plan_por_codigo(codigo):
    with _usar_conexion() as conexion:
        return _obtener_plan_conexion(conexion, codigo)


def obtener_todos_los_planes():
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT codigo FROM plan ORDER BY codigo")
            codigos = [fila["codigo"] for fila in _filas(cursor)]
        return [_obtener_plan_conexion(conexion, codigo) for codigo in codigos]


def guardar_plan(plan):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO plan (codigo, nombre, descripcion) VALUES "
                "(%s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s, descripcion=%s",
                (plan.codigo, plan.nombre, plan.descripcion, plan.nombre, plan.descripcion),
            )


def eliminar_plan(codigo):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM plan WHERE codigo = %s", (codigo,))


def obtener_versiones_de_plan(codigo_plan):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_plan WHERE plan = %s ORDER BY num",
                (codigo_plan,),
            )
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_version_plan(conexion, num) for num in numeros]


def buscar_version_plan_por_num(num):
    with _usar_conexion() as conexion:
        return _consulta_version_plan(conexion, num)


def buscar_version_plan_vigente(codigo_plan):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_plan WHERE plan=%s "
                "AND CURDATE() BETWEEN fecha_inicio AND fecha_final "
                "ORDER BY num DESC LIMIT 1",
                (codigo_plan,),
            )
            fila = _fila(cursor)
        return _consulta_version_plan(conexion, fila["num"]) if fila else None


def _guardar_configuracion(conexion, configuracion, tabla, columnas, valores):
    if configuracion is None:
        return None
    with conexion.cursor() as cursor:
        if configuracion.num is None:
            nombres = ", ".join(columnas)
            marcadores = ", ".join(["%s"] * len(valores))
            cursor.execute(
                f"INSERT INTO {tabla} ({nombres}) VALUES ({marcadores})", valores
            )
            configuracion.num = cursor.lastrowid
        else:
            asignaciones = ", ".join(f"{columna}=%s" for columna in columnas)
            cursor.execute(
                f"UPDATE {tabla} SET {asignaciones} WHERE num=%s",
                valores + (configuracion.num,),
            )
    return configuracion.num


def guardar_version_plan(version_plan):
    with _usar_conexion() as conexion:
        cashback = version_plan.config_cashback
        puntos = version_plan.config_puntos
        descuento = version_plan.config_descuento
        id_cashback = _guardar_configuracion(
            conexion, cashback, "config_cashback",
            ("porcentaje", "limite_min_mensual"),
            (cashback.porcentaje, cashback.limite_min_mensual) if cashback else (),
        )
        id_puntos = _guardar_configuracion(
            conexion, puntos, "config_puntos", ("porcentaje", "vigencia_meses"),
            (puntos.porcentaje, puntos.vigencia_meses) if puntos else (),
        )
        id_descuento = _guardar_configuracion(
            conexion, descuento, "config_descuento",
            ("porcentaje", "monto_minimo"),
            (descuento.porcentaje, descuento.monto_minimo) if descuento else (),
        )
        if descuento is not None:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM dia_aplicable_desc WHERE config_descuento=%s",
                    (id_descuento,),
                )
                for dia in descuento.dias_aplicables:
                    valor = dia.dia_semana if hasattr(dia, "dia_semana") else dia
                    cursor.execute(
                        "INSERT INTO dia_aplicable_desc "
                        "(config_descuento, dia_semana) VALUES (%s, %s)",
                        (id_descuento, valor),
                    )
        base = version_plan.version_base_de_promo
        id_base = base.num if base is not None else None
        valores = (
            version_plan.fecha_inicio, version_plan.fecha_final,
            version_plan.precio, version_plan.plazo_meses,
            version_plan.aplica_en.value, version_plan.plan.codigo,
            id_cashback, id_puntos, id_descuento, id_base,
        )
        with conexion.cursor() as cursor:
            if version_plan.num is None:
                cursor.execute(
                    "INSERT INTO version_plan "
                    "(fecha_inicio, fecha_final, precio, plazo_meses, aplica_en, "
                    "plan, config_cashback, config_puntos, config_descuento, "
                    "version_base_de_promo) VALUES "
                    "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                object.__setattr__(version_plan, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    "UPDATE version_plan SET fecha_inicio=%s, fecha_final=%s, "
                    "precio=%s, plazo_meses=%s, aplica_en=%s, plan=%s, "
                    "config_cashback=%s, config_puntos=%s, config_descuento=%s, "
                    "version_base_de_promo=%s WHERE num=%s",
                    valores + (version_plan.num,),
                )


def eliminar_version_plan(num):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM version_plan WHERE num=%s", (num,))


# Membresia
def buscar_membresia_por_num(num):
    with _usar_conexion() as conexion:
        return _consulta_membresia(conexion, num)


def buscar_membresia_de_miembro(num_miembro):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM membresia WHERE miembro=%s "
                "ORDER BY (estado = 'CANCELADA'), num DESC LIMIT 1",
                (num_miembro,),
            )
            fila = _fila(cursor)
        return _consulta_membresia(conexion, fila["num"]) if fila else None


def guardar_membresia(membresia):
    with _usar_conexion() as conexion:
        valores = (
            membresia.fecha_contratacion, membresia.estado.value,
            membresia.miembro.num,
            membresia.version_plan_actual.num
            if membresia.version_plan_actual is not None else None,
        )
        with conexion.cursor() as cursor:
            if membresia.num is None:
                cursor.execute(
                    "INSERT INTO membresia "
                    "(fecha_contratacion, estado, miembro, version_plan_actual) "
                    "VALUES (%s,%s,%s,%s)", valores,
                )
                membresia.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE membresia SET fecha_contratacion=%s, estado=%s, "
                    "miembro=%s, version_plan_actual=%s WHERE num=%s",
                    valores + (membresia.num,),
                )


# Recompensa y VersionRecompensa
def buscar_recompensa_por_codigo(codigo):
    with _usar_conexion() as conexion:
        return _obtener_recompensa_conexion(conexion, codigo)


def obtener_todas_las_recompensas():
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT codigo FROM recompensa ORDER BY codigo")
            codigos = [fila["codigo"] for fila in _filas(cursor)]
        return [_obtener_recompensa_conexion(conexion, codigo) for codigo in codigos]


def guardar_recompensa(recompensa):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO recompensa (codigo,nombre,descripcion) VALUES "
                "(%s,%s,%s) ON DUPLICATE KEY UPDATE nombre=%s, descripcion=%s",
                (recompensa.codigo, recompensa.nombre, recompensa.descripcion,
                 recompensa.nombre, recompensa.descripcion),
            )


def eliminar_recompensa(codigo):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM recompensa WHERE codigo=%s", (codigo,))


def obtener_versiones_de_recompensa(codigo_recompensa):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_recompensa WHERE recompensa=%s ORDER BY num",
                (codigo_recompensa,),
            )
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_version_recompensa(conexion, num) for num in numeros]


def buscar_version_recompensa_por_num(num):
    with _usar_conexion() as conexion:
        return _consulta_version_recompensa(conexion, num)


def buscar_version_recompensa_vigente(codigo_recompensa):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_recompensa WHERE recompensa=%s "
                "AND CURDATE() BETWEEN fecha_inicio AND fecha_final "
                "ORDER BY num DESC LIMIT 1", (codigo_recompensa,),
            )
            fila = _fila(cursor)
        return _consulta_version_recompensa(conexion, fila["num"]) if fila else None


def guardar_version_recompensa(version_recompensa):
    with _usar_conexion() as conexion:
        valores = (
            version_recompensa.fecha_inicio, version_recompensa.fecha_final,
            version_recompensa.costo_puntos, version_recompensa.limite_canjes,
            version_recompensa.recompensa.codigo,
        )
        with conexion.cursor() as cursor:
            if version_recompensa.num is None:
                cursor.execute(
                    "INSERT INTO version_recompensa "
                    "(fecha_inicio,fecha_final,costo_puntos,limite_canjes,recompensa) "
                    "VALUES (%s,%s,%s,%s,%s)", valores,
                )
                object.__setattr__(version_recompensa, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    "UPDATE version_recompensa SET fecha_inicio=%s, "
                    "fecha_final=%s, costo_puntos=%s, limite_canjes=%s, "
                    "recompensa=%s WHERE num=%s", valores + (version_recompensa.num,),
                )


def eliminar_version_recompensa(num):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM version_recompensa WHERE num=%s", (num,))


# Compras, renovaciones y transacciones
def _consulta_compra(conexion, num):
    consulta = """
        SELECT c.* FROM compra c WHERE c.num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_compra(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _obtener_usuario_conexion(conexion, fila["usuario"]),
    )


def buscar_compra_por_num(num):
    with _usar_conexion() as conexion:
        return _consulta_compra(conexion, num)


def guardar_compra(compra):
    with _usar_conexion() as conexion:
        valores = (
            compra.monto_base, compra.porcentaje_descuento,
            compra.descuento_nominal, compra.cashback_aplicado,
            compra.monto_final, compra.membresia.num, compra.usuario.num,
        )
        with conexion.cursor() as cursor:
            if compra.num is None:
                cursor.execute(
                    "INSERT INTO compra (monto_base,porcentaje_descuento,"
                    "descuento_nominal,cashback_aplicado,monto_final,membresia,usuario) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                compra.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE compra SET monto_base=%s, porcentaje_descuento=%s, "
                    "descuento_nominal=%s, cashback_aplicado=%s, monto_final=%s, "
                    "membresia=%s, usuario=%s WHERE num=%s",
                    valores + (compra.num,),
                )


def obtener_compras_de_membresia(num_membresia):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM compra WHERE membresia=%s ORDER BY num", (num_membresia,))
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_compra(conexion, num) for num in numeros]


def _consulta_renovacion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM renovacion WHERE num=%s", (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_renovacion(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _consulta_version_plan(conexion, fila["version_plan_comprado"]),
    )


def guardar_renovacion(renovacion):
    with _usar_conexion() as conexion:
        valores = (
            renovacion.fecha_pago, renovacion.monto_pagado,
            renovacion.fecha_inicio_periodo, renovacion.fecha_fin_periodo,
            renovacion.membresia.num, renovacion.version_plan_comprado.num,
        )
        with conexion.cursor() as cursor:
            if renovacion.num is None:
                cursor.execute(
                    "INSERT INTO renovacion (fecha_pago,monto_pagado,"
                    "fecha_inicio_periodo,fecha_fin_periodo,membresia,version_plan_comprado) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", valores,
                )
                renovacion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE renovacion SET fecha_pago=%s,monto_pagado=%s,"
                    "fecha_inicio_periodo=%s,fecha_fin_periodo=%s,membresia=%s,"
                    "version_plan_comprado=%s WHERE num=%s",
                    valores + (renovacion.num,),
                )


def obtener_renovaciones_de_membresia(num_membresia):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM renovacion WHERE membresia=%s ORDER BY num",
                (num_membresia,),
            )
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_renovacion(conexion, num) for num in numeros]


def _consulta_transaccion_puntos(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM transaccion_puntos WHERE num=%s", (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_transaccion_puntos(
        fila,
        _consulta_compra(conexion, fila["compra"]) if fila["compra"] else None,
        _consulta_version_recompensa(conexion, fila["version_recompensa"])
        if fila["version_recompensa"] else None,
        _consulta_membresia(conexion, fila["membresia"]),
    )


def guardar_transaccion_puntos(transaccion):
    with _usar_conexion() as conexion:
        valores = (
            transaccion.movimiento, transaccion.saldo, transaccion.fecha,
            transaccion.concepto, transaccion.compra.num
            if transaccion.compra else None,
            transaccion.version_recompensa.num
            if transaccion.version_recompensa else None,
            transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    "INSERT INTO transaccion_puntos "
                    "(movimiento,saldo,fecha,concepto,compra,version_recompensa,membresia) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE transaccion_puntos SET movimiento=%s,saldo=%s,fecha=%s,"
                    "concepto=%s,compra=%s,version_recompensa=%s,membresia=%s WHERE num=%s",
                    valores + (transaccion.num,),
                )


def obtener_transacciones_de_miembro(num_miembro):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT tp.num FROM transaccion_puntos tp "
                "JOIN membresia m ON m.num=tp.membresia WHERE m.miembro=%s "
                "ORDER BY tp.fecha,tp.num", (num_miembro,),
            )
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_transaccion_puntos(conexion, num) for num in numeros]


def obtener_saldo_de_miembro(num_miembro):
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo if transacciones else 0


def _consulta_transaccion_cashback(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM transaccion_cashback WHERE num=%s", (num,))
        fila = _fila(cursor)
    if fila is None:
        return None
    return mapear_transaccion_cashback(
        fila,
        _consulta_compra(conexion, fila["compra"]) if fila["compra"] else None,
        _consulta_membresia(conexion, fila["membresia"]),
    )


def guardar_transaccion_cashback(transaccion):
    with _usar_conexion() as conexion:
        valores = (
            transaccion.monto, transaccion.saldo, transaccion.fecha,
            transaccion.concepto, transaccion.compra.num
            if transaccion.compra else None, transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    "INSERT INTO transaccion_cashback "
                    "(monto,saldo,fecha,concepto,compra,membresia) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE transaccion_cashback SET monto=%s,saldo=%s,fecha=%s,"
                    "concepto=%s,compra=%s,membresia=%s WHERE num=%s",
                    valores + (transaccion.num,),
                )


def obtener_transacciones_cashback_de_membresia(num_membresia):
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM transaccion_cashback WHERE membresia=%s "
                "ORDER BY fecha,num", (num_membresia,),
            )
            numeros = [fila["num"] for fila in _filas(cursor)]
        return [_consulta_transaccion_cashback(conexion, num) for num in numeros]


def obtener_saldo_cashback_de_membresia(num_membresia):
    transacciones = obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        from decimal import Decimal
        return Decimal("0")
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo


# Rol
def buscar_rol_por_codigo(codigo):
    with _usar_conexion() as conexion:
        return _obtener_rol_conexion(conexion, codigo)


def obtener_todos_los_roles():
    with _usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM rol ORDER BY codigo")
            return [mapear_rol(fila) for fila in _filas(cursor)]
