"""Jerarquía de excepciones personalizadas del dominio."""


class ProductoError(Exception):
    """Excepción base del Sistema de Gestión de Productos."""


class ValidationError(ProductoError):
    """Se lanza cuando un dato de entrada no cumple las reglas de negocio."""


class NotFoundError(ProductoError):
    """Se lanza cuando no existe un producto con el ID solicitado."""