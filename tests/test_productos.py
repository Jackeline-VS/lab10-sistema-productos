"""Pruebas de ruta feliz y ruta de error del Sistema de Gestión de Productos."""

# pylint: disable=missing-function-docstring

import unittest

from main import buscar_producto
from models import Electronico, ElectronicoOferta, Libro, LibroOferta
from utils import NotFoundError, ValidationError, validar_categoria, validar_numero


class TestRutaFeliz(unittest.TestCase):
    """Casos donde todo funciona correctamente."""

    def test_electronico_con_igv(self):
        laptop = Electronico("Laptop", 2000, 12, 12)
        self.assertEqual(laptop.calcular_precio_final(), 2360.0)

    def test_electronico_descuento_por_stock(self):
        laptop = Electronico("Laptop", 2000, 60, 12)
        self.assertEqual(laptop.calcular_precio_final(), 2242.0)

    def test_libro_de_texto_descuento(self):
        libro = Libro("Calculo", 200, 5, "james stewart", True)
        self.assertEqual(libro.calcular_precio_final(), 180.0)
        self.assertEqual(libro.autor, "James Stewart")

    def test_mixin_y_mro(self):
        oferta = LibroOferta(
            nombre="Calculo",
            precio_base=200,
            stock=5,
            autor="James",
            es_texto=True,
            descuento_pct=10,
        )
        self.assertEqual(oferta.calcular_precio_final(), 162.0)
        nombres = [c.__name__ for c in ElectronicoOferta.__mro__]
        self.assertEqual(
            nombres,
            [
                "ElectronicoOferta",
                "DescuentoMixin",
                "Electronico",
                "Producto",
                "object",
            ],
        )

    def test_polimorfismo(self):
        productos = [Electronico("Mouse", 50, 10, 6), Libro("Python", 300, 2, "Ana")]
        precios = [p.calcular_precio_final() for p in productos]
        self.assertEqual(precios, [59.0, 300.0])

    def test_validadores(self):
        self.assertEqual(validar_numero(" 25.5 "), 25.5)
        self.assertEqual(validar_categoria(" Libro "), "libro")


class TestRutaError(unittest.TestCase):
    """Casos donde el sistema debe lanzar excepciones controladas."""

    def test_precio_negativo(self):
        with self.assertRaises(ValidationError):
            Electronico("Laptop", -5, 10, 12)

    def test_garantia_fuera_de_rango(self):
        with self.assertRaises(ValidationError):
            Electronico("Laptop", 2000, 10, 99)

    def test_autor_con_numeros(self):
        with self.assertRaises(ValidationError):
            Libro("Calculo", 100, 5, "J4mes")

    def test_numero_invalido(self):
        with self.assertRaises(ValidationError):
            validar_numero("abc")

    def test_categoria_invalida(self):
        with self.assertRaises(ValidationError):
            validar_categoria("ropa")

    def test_producto_no_encontrado(self):
        with self.assertRaises(NotFoundError):
            buscar_producto({}, 99)

    def test_setter_protege_estado(self):
        libro = Libro("Python", 300, 2, "Ana Perez")
        with self.assertRaises(ValidationError):
            libro.stock = -1
        self.assertEqual(libro.stock, 2)


if __name__ == "__main__":
    unittest.main()
