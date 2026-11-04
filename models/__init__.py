"""Paquete de modelos: expone las clases públicas para importación limpia."""

from .producto import (
    DescuentoMixin,
    Electronico,
    ElectronicoOferta,
    Libro,
    LibroOferta,
    Producto,
)

__all__ = [
    "Producto",
    "Electronico",
    "Libro",
    "DescuentoMixin",
    "ElectronicoOferta",
    "LibroOferta",
]
