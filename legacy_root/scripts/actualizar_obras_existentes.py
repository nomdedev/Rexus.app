"""
Script para actualizar obras existentes con códigos automáticos y fechas por defecto.
"""

import datetime
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar rutas para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "rexus"))


def generar_codigo_obra() -> str:
    """Genera un código único para la obra."""
    fecha_actual = datetime.datetime.now()
    codigo_fecha = fecha_actual.strftime("%Y%m")
    codigo_unico = str(uuid.uuid4())[:8].upper()
    return f"OBR-{codigo_fecha}-{codigo_unico}"


def actualizar_obras_existentes():
    """Actualiza obras existentes sin código con valores por defecto."""
    try:
        # Importar directamente desde el directorio correcto
        import os
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        from rexus.core.database import InventarioDatabaseConnection

        print("🔄 Iniciando actualización de obras existentes...")

        # Conectar a base de datos
        db = InventarioDatabaseConnection()
        db.connect()
        cursor = db.cursor()

        # Obtener obras sin código
        cursor.execute("""
            SELECT id, nombre, cliente, fecha_inicio, fecha_fin_estimada
            FROM obras
            WHERE codigo IS NULL OR codigo = '' OR codigo = 'Sin código'
        """)

        obras_sin_codigo = cursor.fetchall()
        print(f"📋 Encontradas {len(obras_sin_codigo)} obras sin código")

        fecha_actual = datetime.date.today()

        for obra in obras_sin_codigo:
            obra_id, nombre, cliente, fecha_inicio, fecha_fin_est = obra

            # Generar código único
            codigo = generar_codigo_obra()

            # Establecer fecha de medición por defecto (hoy si no tiene fecha_inicio)
            fecha_medicion = fecha_inicio if fecha_inicio else fecha_actual

            # Calcular fecha de colocación (90 días después de medición)
            if isinstance(fecha_medicion, str):
                fecha_medicion = datetime.datetime.strptime(
                    fecha_medicion, "%Y-%m-%d"
                ).date()

            fecha_colocacion = fecha_medicion + datetime.timedelta(days=90)

            # Actualizar obra
            cursor.execute(
                """
                UPDATE obras
                SET codigo = ?,
                    fecha_medicion = ?,
                    fecha_colocacion = ?,
                    observaciones = COALESCE(observaciones, '') || ?
                WHERE id = ?
            """,
                (
                    codigo,
                    fecha_medicion.strftime("%Y-%m-%d"),
                    fecha_colocacion.strftime("%Y-%m-%d"),
                    f"\n[AUTO] Código generado automáticamente el {fecha_actual}. Fecha de medición establecida por defecto.",
                    obra_id,
                ),
            )

            print(f"  [CHECK] Obra '{nombre}' - Código: {codigo}")
            print(f"     📅 Fecha medición: {fecha_medicion}")
            print(f"     📅 Fecha colocación: {fecha_colocacion}")

        # Confirmar cambios
        db.commit()
        print(
            f"\n🎉 Actualización completada: {len(obras_sin_codigo)} obras actualizadas"
        )

        # Mostrar obras actualizadas
        cursor.execute("""
            SELECT codigo, nombre, cliente, fecha_medicion, fecha_colocacion
            FROM obras
            ORDER BY fecha_medicion DESC
        """)

        todas_obras = cursor.fetchall()
        print(f"\n[CHART] Resumen de todas las obras ({len(todas_obras)}):")
        for obra in todas_obras:
            codigo, nombre, cliente, f_medicion, f_colocacion = obra
            print(f"  • {codigo} - {nombre} ({cliente})")
            print(f"    Medición: {f_medicion} | Colocación: {f_colocacion}")

        db.close()
        return True

    except Exception as e:
        print(f"[ERROR] Error actualizando obras: {e}")
        import traceback

        traceback.print_exc()
        return False


def generar_cargas_material_obras():
    """Genera cargas de material para las obras existentes."""
    try:
        from rexus.core.database import InventarioDatabaseConnection

        print("\n🔄 Generando cargas de material para obras...")

        db = InventarioDatabaseConnection()
        db.connect()
        cursor = db.cursor()

        # Obtener todas las obras
        cursor.execute("""
            SELECT id, codigo, nombre, cliente, fecha_medicion, fecha_colocacion, estado
            FROM obras
            ORDER BY fecha_medicion
        """)

        obras = cursor.fetchall()

        # Crear tabla de cargas de material si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cargas_material (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                obra_id INTEGER NOT NULL,
                codigo_carga VARCHAR(50) NOT NULL,
                tipo_material VARCHAR(100) NOT NULL,
                cantidad DECIMAL(10,2) NOT NULL,
                unidad VARCHAR(20) NOT NULL,
                fecha_solicitud DATE NOT NULL,
                fecha_entrega_estimada DATE,
                estado VARCHAR(50) DEFAULT 'PENDIENTE',
                prioridad VARCHAR(20) DEFAULT 'NORMAL',
                observaciones TEXT,
                usuario_creacion VARCHAR(100) DEFAULT 'SISTEMA',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (obra_id) REFERENCES obras(id)
            )
        """)

        materiales_base = [
            ("Vidrio Laminado 6+6", 15.50, "m2", "ALTA"),
            ("Perfil de Aluminio", 8.30, "ml", "NORMAL"),
            ("Herrajes de Ventana", 4.00, "unidad", "NORMAL"),
            ("Silicona Estructural", 2.80, "tubo", "NORMAL"),
            ("Tornillería Inoxidable", 1.00, "kg", "BAJA"),
        ]

        for obra in obras:
            obra_id, codigo, nombre, cliente, fecha_med, fecha_col, estado = obra

            print(f"\n📦 Generando cargas para obra: {codigo} - {nombre}")

            # Generar 3-5 cargas de material por obra
            import random

            num_cargas = random.randint(3, 5)

            for i in range(num_cargas):
                material = random.choice(materiales_base)
                mat_nombre, cantidad_base, unidad, prioridad = material

                # Variar cantidad
                cantidad = round(cantidad_base * random.uniform(0.8, 2.5), 2)

                # Código de carga
                codigo_carga = f"CM-{codigo}-{i + 1:02d}"

                # Fechas
                fecha_solicitud = datetime.datetime.strptime(
                    fecha_med, "%Y-%m-%d"
                ).date()
                fecha_entrega = fecha_solicitud + datetime.timedelta(
                    days=random.randint(5, 15)
                )

                # Estado según fecha
                if fecha_entrega < datetime.date.today():
                    estado_carga = "ENTREGADO"
                elif fecha_solicitud <= datetime.date.today():
                    estado_carga = random.choice(["EN_PROCESO", "PREPARANDO"])
                else:
                    estado_carga = "PENDIENTE"

                cursor.execute(
                    """
                    INSERT INTO cargas_material
                    (obra_id, codigo_carga, tipo_material, cantidad, unidad,
                     fecha_solicitud, fecha_entrega_estimada, estado, prioridad,
                     observaciones, usuario_creacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        obra_id,
                        codigo_carga,
                        mat_nombre,
                        cantidad,
                        unidad,
                        fecha_solicitud,
                        fecha_entrega,
                        estado_carga,
                        prioridad,
                        f"Carga generada automáticamente para obra {codigo}",
                        "SISTEMA",
                    ),
                )

                print(
                    f"  [CHECK] {codigo_carga}: {cantidad} {unidad} de {mat_nombre} - {estado_carga}"
                )

        db.commit()

        # Mostrar resumen
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN estado = 'ENTREGADO' THEN 1 ELSE 0 END) as entregadas,
                   SUM(CASE WHEN estado = 'EN_PROCESO' THEN 1 ELSE 0 END) as en_proceso,
                   SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as pendientes
            FROM cargas_material
        """)

        resumen = cursor.fetchone()
        total, entregadas, en_proceso, pendientes = resumen

        print(f"\n[CHART] Resumen de cargas de material:")
        print(f"  📦 Total generadas: {total}")
        print(f"  [CHECK] Entregadas: {entregadas}")
        print(f"  🔄 En proceso: {en_proceso}")
        print(f"  ⏳ Pendientes: {pendientes}")

        db.close()
        return True

    except Exception as e:
        print(f"[ERROR] Error generando cargas de material: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("[ROCKET] Iniciando actualización completa de obras...")

    # Actualizar obras existentes
    if actualizar_obras_existentes():
        # Generar cargas de material
        generar_cargas_material_obras()

        print("\n🎉 Proceso completado exitosamente!")
        print("\n📋 Próximos pasos:")
        print("  1. Verificar que las obras tienen códigos únicos")
        print("  2. Revisar fechas de medición y colocación")
        print("  3. Ajustar cargas de material según necesidades")
        print("  4. Probar el flujo completo en la aplicación")
    else:
        print("[ERROR] Error en la actualización. Revise los logs.")
