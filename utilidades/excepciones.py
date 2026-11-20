"""Excepciones de dominio compartidas por los servicios de Nexum."""


class ErrorDominio(Exception):
    """Base común para errores esperados de las reglas de negocio."""


class ErrorPersistencia(ErrorDominio):
    """No fue posible completar una operación contra la base de datos."""


class DatosInvalidos(ErrorDominio, ValueError):
    """Los datos no cumplen el contrato de una operación."""


class EntidadNoEncontrada(DatosInvalidos):
    """La entidad solicitada no existe."""


class OperacionNoPermitida(ErrorDominio, PermissionError):
    """La identidad o el estado actual impide la operación."""


class VersionNoVigente(DatosInvalidos):
    """La versión solicitada está fuera de su período de vigencia."""


class SaldoInsuficiente(OperacionNoPermitida):
    """El saldo disponible no alcanza para la operación."""


class LimiteExcedido(OperacionNoPermitida):
    """La operación supera un límite de negocio."""
