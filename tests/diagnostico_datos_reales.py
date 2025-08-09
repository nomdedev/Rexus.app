#!/usr/bin/env python3
"""
Test de Diagnóstico de Datos Reales
===================================

Identifica exactamente por qué no se cargan los datos reales de la base de datos.
"""

import os
import sys
import traceback

# Agregar ruta del proyecto
sys.path.insert(0, os.path.abspath("."))


def diagnosticar_carga_datos():
    """Diagnostica paso a paso la carga de datos reales."""

    print("🔍 DIAGNÓSTICO DE CARGA DE DATOS REALES")
    print("=" * 60)

    try:
        # 1. Test de conexión directa
        print("1️⃣ Probando conexión directa a base de datos...")
        from rexus.core.database import InventarioDatabaseConnection

        db_connection = InventarioDatabaseConnection(auto_connect=True)
        if not db_connection.connection:
            print("[ERROR] Error en conexión a base de datos")
            return False
        print("[CHECK] Conexión directa OK")

        # 2. Test de consulta directa
        print("\n2️⃣ Probando consulta SQL directa...")
        cursor = db_connection.connection.cursor()

        # Verificar datos con columnas nuevas
        cursor.execute("""
            SELECT TOP 3 id, codigo, descripcion, stock_actual, categoria, precio_unitario, activo
            FROM inventario_perfiles 
            WHERE activo = 1
            ORDER BY id
        """)
        registros_directos = cursor.fetchall()

        if registros_directos:
            print(f"[CHECK] Consulta directa OK - {len(registros_directos)} registros")
            for reg in registros_directos:
                print(f"   📋 ID: {reg[0]}, Código: {reg[1]}, Activo: {reg[6]}")
        else:
            print("[WARN] Consulta directa no devuelve registros")

            # Verificar si hay registros sin columna activo
            cursor.execute("SELECT COUNT(*) FROM inventario_perfiles")
            total = cursor.fetchone()[0]
            print(f"[CHART] Total registros en tabla: {total}")

            # Verificar cuántos tienen activo = 1
            cursor.execute("SELECT COUNT(*) FROM inventario_perfiles WHERE activo = 1")
            activos = cursor.fetchone()[0]
            print(f"[CHART] Registros activos: {activos}")

            if activos == 0:
                print("[WARN] Ningún registro tiene activo = 1, actualizando...")
                cursor.execute(
                    "UPDATE inventario_perfiles SET activo = 1 WHERE activo IS NULL OR activo = 0"
                )
                db_connection.connection.commit()
                print("[CHECK] Registros actualizados a activo = 1")

        # 3. Test del modelo
        print("\n3️⃣ Probando modelo de inventario...")
        from rexus.modules.inventario.model import InventarioModel

        model = InventarioModel(db_connection=db_connection.connection)
        print("[CHECK] Modelo creado")

        # 4. Test del consultas_manager
        print("\n4️⃣ Probando consultas_manager...")
        if hasattr(model, "consultas_manager"):
            print("[CHECK] ConsultasManager disponible")

            try:
                resultado = model.consultas_manager.obtener_productos_paginados_inicial(
                    0, 5
                )

                print(f"[CHART] Tipo resultado: {type(resultado)}")
                print(
                    f"[CHART] Keys disponibles: {list(resultado.keys()) if isinstance(resultado, dict) else 'No es dict'}"
                )

                items = (
                    resultado.get("items", []) if isinstance(resultado, dict) else []
                )
                total = resultado.get("total", 0) if isinstance(resultado, dict) else 0

                print(f"[CHART] Items encontrados: {len(items)}")
                print(f"[CHART] Total reportado: {total}")

                if items:
                    print("[CHECK] ConsultasManager devuelve datos:")
                    for i, item in enumerate(items[:3]):
                        print(f"   {i + 1}. {item}")
                else:
                    print("[ERROR] ConsultasManager no devuelve items")

                    # Revisar si hay error en el resultado
                    if "error" in resultado:
                        print(f"🚨 Error en consultas_manager: {resultado['error']}")

            except Exception as e:
                print(f"[ERROR] Error en consultas_manager: {e}")
                traceback.print_exc()
        else:
            print("[ERROR] ConsultasManager no disponible")

        # 5. Test del método directo del modelo
        print("\n5️⃣ Probando métodos directos del modelo...")

        # Probar obtener_productos_paginados_inicial
        if hasattr(model, "obtener_productos_paginados_inicial"):
            try:
                resultado_directo = model.obtener_productos_paginados_inicial(0, 5)
                print(
                    f"[CHECK] obtener_productos_paginados_inicial OK: {len(resultado_directo.get('items', []))} items"
                )
            except Exception as e:
                print(f"[ERROR] Error en obtener_productos_paginados_inicial: {e}")
                traceback.print_exc()

        # 6. Test del controlador
        print("\n6️⃣ Probando controlador...")
        from rexus.modules.inventario.controller import InventarioController

        controller = InventarioController(
            model=model, db_connection=db_connection.connection
        )

        # Interceptar la carga
        print("📞 Llamando _cargar_datos_inventario...")
        controller._cargar_datos_inventario()

        print("\n" + "=" * 60)
        print("[CHART] DIAGNÓSTICO COMPLETADO")

        return True

    except Exception as e:
        print(f"\n[ERROR] ERROR EN DIAGNÓSTICO: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    resultado = diagnosticar_carga_datos()
    exit(0 if resultado else 1)
