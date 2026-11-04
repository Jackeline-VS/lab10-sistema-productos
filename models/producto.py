"""Modelos del dominio: Producto (base), Electronico, Libro y DescuentoMixin."""

from __future__ import annotations

try:  # Python 3.12+
    from typing import override
except ImportError:  # Python 3.11: decorador neutro con el mismo nombre

    def override(func):  # type: ignore[no-redef]
        """Marca un método como sobrescrito (sin efecto en 3.11)."""
        return func


from utils.exceptions import ValidationError
from utils.formatters import formatear_moneda

IGV: float = 0.18
DESCUENTO_VOLUMEN: float = 0.05  # Electrónico con stock > 50
UMBRAL_STOCK: int = 50
DESCUENTO_LIBRO_TEXTO: float = 0.10


class Producto:
    """Clase base abstracta de todos los productos del inventario."""

    _total_instancias: int = 0  # atributo de clase

    def __init__(self, nombre: str, precio_base: float, stock: int, **kwargs) -> None:
        super().__init__(**kwargs)  # cooperativo: permite mixins en el MRO
        self.nombre = nombre  # cada asignación pasa por su setter
        self.precio_base = precio_base
        self.stock = stock
        Producto._total_instancias += 1

    # ---------- Encapsulamiento con @property ----------
    @property
    def nombre(self) -> str:
        """Nombre del producto (2 a 60 caracteres)."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValidationError("El nombre debe ser texto")
        limpio = " ".join(valor.split())
        if not 2 <= len(limpio) <= 60:
            raise ValidationError("El nombre debe tener entre 2 y 60 caracteres")
        self._nombre = limpio

    @property
    def precio_base(self) -> float:
        """Precio base sin impuestos (0 < precio <= 100 000)."""
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            raise ValidationError("El precio debe ser numérico")
        if not 0 < valor <= 100_000:
            raise ValidationError("El precio debe estar entre 0.01 y 100000")
        self._precio_base = float(valor)

    @property
    def stock(self) -> int:
        """Unidades disponibles (0 a 10 000)."""
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValidationError("El stock debe ser un número entero")
        if not 0 <= valor <= 10_000:
            raise ValidationError("El stock debe estar entre 0 y 10000")
        self._stock = valor

    @classmethod
    def total_instancias(cls) -> int:
        """Cantidad de productos creados en la sesión."""
        return Producto._total_instancias

    # ---------- Polimorfismo ----------
    def calcular_precio_final(self) -> float:
        """Debe ser implementado por cada subclase."""
        raise NotImplementedError("Subclases deben implementar este método")

    def detalle_extra(self) -> str:
        """Información propia de cada subclase (gancho para __str__)."""
        return ""

    def __str__(self) -> str:
        extra = f" | {self.detalle_extra()}" if self.detalle_extra() else ""
        return (
            f"[{self.__class__.__name__}] {self.nombre} | "
            f"{formatear_moneda(self.precio_base)} | Stock: {self.stock}{extra}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(nombre={self.nombre!r}, "
            f"precio_base={self.precio_base}, stock={self.stock})"
        )

    def __del__(self) -> None:
        # __del__ no es determinista: solo informativo, nunca para lógica crítica.
        print(f"🗑️  Destruyendo instancia: {getattr(self, '_nombre', '?')}")


class Electronico(Producto):
    """Producto electrónico con garantía en meses."""

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock: int,
        garantia_meses: int,
        **kwargs,
    ) -> None:
        super().__init__(nombre=nombre, precio_base=precio_base, stock=stock, **kwargs)
        self.garantia_meses = garantia_meses

    @property
    def garantia_meses(self) -> int:
        """Garantía en meses (0 a 60). Atributo protegido _garantia_meses."""
        return self._garantia_meses

    @garantia_meses.setter
    def garantia_meses(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValidationError("La garantía debe ser un número entero de meses")
        if not 0 <= valor <= 60:
            raise ValidationError("La garantía debe estar entre 0 y 60 meses")
        self._garantia_meses = valor

    @override
    def calcular_precio_final(self) -> float:
        """Precio base + IGV (18 %) y 5 % de descuento si stock > 50."""
        precio = self.precio_base * (1 + IGV)
        if self.stock > UMBRAL_STOCK:
            precio *= 1 - DESCUENTO_VOLUMEN
        return round(precio, 2)

    @override
    def detalle_extra(self) -> str:
        return f"Garantía: {self.garantia_meses} meses"


class Libro(Producto):
    """Libro con autor (atributo privado) e indicador de libro de texto."""

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock: int,
        autor: str,
        es_texto: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(nombre=nombre, precio_base=precio_base, stock=stock, **kwargs)
        self.autor = autor
        self.es_texto = es_texto

    @property
    def autor(self) -> str:
        """Autor del libro. Se guarda en __autor (name-mangling)."""
        return self.__autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValidationError("El autor debe ser texto")
        limpio = " ".join(valor.split())
        if len(limpio) < 3 or any(c.isdigit() for c in limpio):
            raise ValidationError("Autor inválido: mínimo 3 letras y sin números")
        self.__autor = limpio.title()

    @property
    def es_texto(self) -> bool:
        """True si es un libro de texto (aplica descuento)."""
        return self._es_texto

    @es_texto.setter
    def es_texto(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValidationError("es_texto debe ser True o False")
        self._es_texto = valor

    @override
    def calcular_precio_final(self) -> float:
        """Precio base - 10 % si es libro de texto (libros exonerados de IGV)."""
        precio = self.precio_base
        if self.es_texto:
            precio *= 1 - DESCUENTO_LIBRO_TEXTO
        return round(precio, 2)

    @override
    def detalle_extra(self) -> str:
        tipo = "Texto" if self.es_texto else "General"
        return f"Autor: {self.autor} | Tipo: {tipo}"


class DescuentoMixin:
    """Mixin que aplica un descuento promocional sobre el precio final.

    Debe ir a la IZQUIERDA en la herencia para que su
    ``calcular_precio_final`` se resuelva primero en el MRO y llame,
    vía ``super()``, a la implementación de la clase concreta.
    """

    def __init__(self, *, descuento_pct: float = 0.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.descuento_pct = descuento_pct

    @property
    def descuento_pct(self) -> float:
        """Porcentaje de descuento promocional (0 a 50)."""
        return self._descuento_pct

    @descuento_pct.setter
    def descuento_pct(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            raise ValidationError("El descuento debe ser numérico")
        if not 0 <= valor <= 50:
            raise ValidationError("El descuento debe estar entre 0 y 50 %")
        self._descuento_pct = float(valor)

    def calcular_precio_final(self) -> float:
        """Aplica el descuento sobre el precio que calcule la clase siguiente."""
        precio = super().calcular_precio_final()  # type: ignore[misc]
        return round(precio * (1 - self.descuento_pct / 100), 2)

    def detalle_extra(self) -> str:
        """Agrega el porcentaje de oferta al detalle de la clase concreta."""
        base = super().detalle_extra()  # type: ignore[misc]
        return f"{base} | Oferta: -{self.descuento_pct:g}%"


class ElectronicoOferta(DescuentoMixin, Electronico):
    """Electrónico en oferta. MRO: ElectronicoOferta → DescuentoMixin →
    Electronico → Producto → object."""


class LibroOferta(DescuentoMixin, Libro):
    """Libro en oferta. MRO: LibroOferta → DescuentoMixin → Libro →
    Producto → object."""
