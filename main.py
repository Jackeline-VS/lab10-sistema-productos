#!/usr/bin/env python3
"""Orquestador CLI del Sistema de Gestión de Productos - IS093A Semana 10."""

from __future__ import annotations

import logging

from models import Electronico, ElectronicoOferta, Libro, LibroOferta, Producto
from utils import (
    NotFoundError,
    ValidationError,
    formatear_moneda,
    linea,
    titulo,
    validar_categoria,
    validar_numero,
    validar_si_no,
    validar_texto,
)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

Inventario = dict[int, Producto]

OPCIONES: dict[str, str] = {
    "1": "Agregar Producto",
    "2": "Listar Productos",
    "3": "Calcular Precio Final",
    "4": "Salir",
}


def menu() -> str:
    """Muestra el menú principal y devuelve la opción elegida."""
    print("\n" + titulo("GESTIÓN DE PRODUCTOS (CLI)"))
    for clave, texto in OPCIONES.items():
        print(f"  {clave}. {texto}")
    return input("Opción > ").strip()


def pedir(mensaje: str) -> str:
    """Lee una entrada del usuario sin espacios en los extremos."""
    return input(f"  {mensaje}: ").strip()


def agregar_producto(inventario: Inventario, nuevo_id: int) -> Producto:
    """Solicita datos, los valida y guarda el producto con el ID indicado."""
    categoria = validar_categoria(pedir("Categoría (electronico/libro)"))
    datos: dict = {
        "nombre": validar_texto(pedir("Nombre"), "nombre"),
        "precio_base": validar_numero(pedir("Precio base S/"), float, 0.01, 100_000),
        "stock": int(validar_numero(pedir("Stock"), int, 0, 10_000)),
    }

    if categoria == "electronico":
        datos["garantia_meses"] = int(
            validar_numero(pedir("Garantía (meses)"), int, 0, 60)
        )
    else:
        datos["autor"] = validar_texto(pedir("Autor"), "autor", 3)
        datos["es_texto"] = validar_si_no(pedir("¿Es libro de texto? (s/n)"))

    en_oferta = validar_si_no(pedir("¿Aplicar oferta? (s/n)"))
    if en_oferta:
        datos["descuento_pct"] = validar_numero(pedir("Descuento %"), float, 0, 50)
        clase = ElectronicoOferta if categoria == "electronico" else LibroOferta
    else:
        clase = Electronico if categoria == "electronico" else Libro

    producto = clase(**datos)
    inventario[nuevo_id] = producto
    return producto


def listar_productos(inventario: Inventario) -> None:
    """Muestra todos los productos o un aviso si el inventario está vacío."""
    if not inventario:
        print("  📭 Inventario vacío. Agregue un producto con la opción 1.")
        return
    print(linea())
    for id_prod, producto in inventario.items():
        print(f"  ID {id_prod:>3} → {producto}")
    print(linea())
    print(f"  Total de productos: {len(inventario)}")


def buscar_producto(inventario: Inventario, id_prod: int) -> Producto:
    """Devuelve el producto con ese ID o lanza NotFoundError."""
    if id_prod not in inventario:
        raise NotFoundError(f"No existe un producto con ID {id_prod}")
    return inventario[id_prod]


def mostrar_precio_final(inventario: Inventario) -> None:
    """Pide un ID y muestra el precio final calculado polimórficamente."""
    if not inventario:
        raise NotFoundError("El inventario está vacío")
    id_prod = int(validar_numero(pedir("ID del producto"), int, 1))
    producto = buscar_producto(inventario, id_prod)
    print(f"  {producto}")
    print(f"  💰 Precio final: {formatear_moneda(producto.calcular_precio_final())}")
    print(f"  🔗 MRO: {' → '.join(c.__name__ for c in type(producto).__mro__)}")


def main() -> None:
    """Bucle principal del sistema."""
    inventario: Inventario = {}  # {id: objeto_producto}
    contador_id = 1
    operaciones = 0

    while True:
        opcion = ""
        try:
            opcion = menu()
            if opcion == "1":
                producto = agregar_producto(inventario, contador_id)
                print(f"  ✅ Producto agregado con ID {contador_id}: {producto}")
                contador_id += 1
            elif opcion == "2":
                listar_productos(inventario)
            elif opcion == "3":
                mostrar_precio_final(inventario)
            elif opcion == "4":
                print("Cerrando sistema...")
                break
            else:
                raise ValidationError(f"Opción inválida: '{opcion}'")
        except ValidationError as e:
            print(f"⚠️  Error de validación: {e}")
            logger.warning("ValidationError: %s", e)
        except NotFoundError as e:
            print(f"🔍 No encontrado: {e}")
            logger.warning("NotFoundError: %s", e)
        except (KeyboardInterrupt, EOFError):
            print("\nInterrupción detectada. Cerrando sistema...")
            break
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Se registra con traceback completo, nunca se silencia.
            print(f"❌ Error inesperado: {e}")
            logger.exception("Error inesperado")
        else:
            logger.info("Opción %s ejecutada correctamente", opcion)
        finally:
            operaciones += 1
            logger.info("Operación #%d finalizada (opción '%s')", operaciones, opcion)

    print(f"Productos registrados en la sesión: {len(inventario)}")
    logger.info("Sistema cerrado. Productos: %d", len(inventario))


if __name__ == "__main__":
    main()