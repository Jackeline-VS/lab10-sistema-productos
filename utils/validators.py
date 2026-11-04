"""Funciones de validación y sanitización de entradas del usuario."""

from __future__ import annotations

from .exceptions import ValidationError

CATEGORIAS_VALIDAS: tuple[str, ...] = ("electronico", "libro")

_EQUIVALENCIAS: dict[str, str] = {
    "electrónico": "electronico",
    "electronica": "electronico",
    "electrónica": "electronico",
    "e": "electronico",
    "1": "electronico",
    "l": "libro",
    "2": "libro",
}


def validar_numero(
    valor: str,
    tipo: type = float,
    min_val: float = 0,
    max_val: float | None = None,
) -> float:
    """Convierte ``valor`` al ``tipo`` indicado y verifica que esté en rango."""
    try:
        num = tipo(str(valor).strip())
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Formato numérico inválido: '{valor}'") from exc

    if num < min_val or (max_val is not None and num > max_val):
        limite = max_val if max_val is not None else "∞"
        raise ValidationError(f"Valor fuera de rango: {min_val} - {limite}")
    return num


def validar_texto(valor: str, campo: str, min_len: int = 2, max_len: int = 60) -> str:
    """Sanitiza un texto (quita espacios extra) y valida su longitud."""
    limpio = " ".join(str(valor).split())
    if not min_len <= len(limpio) <= max_len:
        raise ValidationError(
            f"El campo '{campo}' debe tener entre {min_len} y {max_len} caracteres"
        )
    return limpio


def validar_categoria(categoria: str) -> str:
    """Normaliza la categoría y la valida contra ``CATEGORIAS_VALIDAS``."""
    normalizada = categoria.strip().lower()
    normalizada = _EQUIVALENCIAS.get(normalizada, normalizada)
    if normalizada not in CATEGORIAS_VALIDAS:
        raise ValidationError(
            f"Categoría '{categoria}' no válida. Use: {', '.join(CATEGORIAS_VALIDAS)}"
        )
    return normalizada


def validar_si_no(valor: str) -> bool:
    """Convierte respuestas s/n en booleano."""
    respuesta = valor.strip().lower()
    if respuesta in ("s", "si", "sí", "y", "yes"):
        return True
    if respuesta in ("n", "no"):
        return False
    raise ValidationError("Responda 's' (sí) o 'n' (no)")
