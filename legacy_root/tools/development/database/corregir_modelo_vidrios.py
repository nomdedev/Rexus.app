"""
Script para corregir todas las consultas SQL del modelo de vidrios.
Actualiza las columnas para que coincidan con la estructura real de la base de datos.
"""

# Añadir el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import os
import sys


def corregir_modelo_vidrios():
    """
    Corrige el modelo de vidrios para usar las columnas correctas de la base de datos.
    """
    ruta_modelo = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "modules",
        "vidrios",
        "model.py",
    )

    try:
        with open(ruta_modelo, "r", encoding="utf-8") as f:
            contenido = f.read()

        print("🔧 Corrigiendo modelo de vidrios...")

        # Correcciones necesarias:
        correcciones = [
            # Cambiar id_obra por obra_id
            ("id_obra", "obra_id"),
            # Eliminar referencias a fecha_pedido que no existe
            ("fecha_pedido", "id"),
            # Eliminar referencias a usuario que no existe en estas consultas
            (", usuario, fecha_pedido", ""),
            ("usuario, fecha_pedido", ""),
            (", usuario", ""),
            # Corregir ORDER BY fecha_pedido DESC por ORDER BY id DESC
            ("ORDER BY fecha_pedido DESC", "ORDER BY id DESC"),
            # Corregir las consultas de SELECT que usan columnas inexistentes
            (
                "SELECT vpo.id_obra, o.nombre, o.cliente, vpo.tipo, vpo.ancho, vpo.alto, vpo.color, vpo.cantidad_reservada, vpo.estado, vpo.fecha_pedido",
                "SELECT vpo.obra_id, o.nombre, o.cliente, vpo.tipo, vpo.ancho, vpo.alto, vpo.color, vpo.cantidad_reservada, vpo.estado, vpo.id",
            ),
            # Corregir SELECT en obtener_detalle_pedido
            (
                "SELECT tipo, ancho, alto, color, cantidad_reservada, estado, fecha_pedido, proveedor, fecha_entrega, observaciones",
                "SELECT tipo, ancho, alto, color, cantidad_reservada, estado, id, proveedor, fecha_entrega, observaciones",
            ),
            # Corregir consultas de INSERT que incluyen columnas inexistentes
            (
                "INSERT INTO vidrios_por_obra (id_obra, tipo, ancho, alto, color, proveedor, fecha_entrega, observaciones, cantidad_reservada, estado, usuario, fecha_pedido)",
                "INSERT INTO vidrios_por_obra (obra_id, tipo, ancho, alto, color, proveedor, fecha_entrega, observaciones, cantidad_reservada, estado)",
            ),
            # Reducir parámetros VALUES para que coincidan
            (
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ),
        ]

        contenido_corregido = contenido

        for buscar, reemplazar in correcciones:
            if buscar in contenido_corregido:
                contenido_corregido = contenido_corregido.replace(buscar, reemplazar)
                print(f"   [CHECK] Corregido: {buscar[:50]}...")

        # Guardar el archivo corregido
        with open(ruta_modelo, "w", encoding="utf-8") as f:
            f.write(contenido_corregido)

        print(f"[CHECK] Modelo de vidrios corregido exitosamente")
        return True

    except Exception as e:
        print(f"[ERROR] Error corrigiendo modelo de vidrios: {e}")
        return False


def main():
    corregir_modelo_vidrios()


if __name__ == "__main__":
    main()
