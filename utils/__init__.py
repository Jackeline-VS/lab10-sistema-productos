"""Paquete de utilidades: excepciones, validaciones y formateo."""

from .exceptions import NotFoundError, ProductoError, ValidationError
from .formatters import formatear_moneda, linea, titulo
from .validators import (
    CATEGORIAS_VALIDAS,
    validar_categoria,
    validar_numero,
    validar_si_no,
    validar_texto,
)

__all__ = [
    "ProductoError",
    "ValidationError",
    "NotFoundError",
    "CATEGORIAS_VALIDAS",
    "validar_numero",
    "validar_texto",
    "validar_categoria",
    "validar_si_no",
    "formatear_moneda",
    "linea",
    "titulo",
]
