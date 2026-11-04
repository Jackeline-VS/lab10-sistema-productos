"""Funciones de formateo para la salida en consola."""

from __future__ import annotations


def formatear_moneda(monto: float) -> str:
    """Devuelve el monto en soles con dos decimales y separador de miles."""
    return f"S/ {monto:,.2f}"


def linea(ancho: int = 60, caracter: str = "-") -> str:
    """Devuelve una línea separadora."""
    return caracter * ancho


def titulo(texto: str, ancho: int = 60) -> str:
    """Devuelve un título centrado entre líneas."""
    return f"{linea(ancho, '=')}\n{texto.center(ancho)}\n{linea(ancho, '=')}"
