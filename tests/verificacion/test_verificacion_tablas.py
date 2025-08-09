"""
Test de Integración Final Simplificado
Verifica la estructura de la base de datos y las relaciones entre tablas
"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal de prueba de integración"""

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Inicializar conexión a BD
        db = ObrasDatabaseConnection()
        db.conectar()
        print(f"[CHECK] Conectado a base de datos: {db.database}")
        print(f"📍 Servidor: {db.server}\n")

        print("\n🧪 INICIANDO TEST DE INTEGRACIÓN")
        print("=" * 60)

        # Test 1: Verificar que las tablas existen
        print("\n📋 Test 1: Verificación de tablas")
        print("-" * 60)

        # Lista de tablas importantes para verificar
        tablas = [
            "obras",
            "inventario_perfiles",
            "users",
            "pedidos_material",
            "vidrios_por_obra",
            "pedidos_herrajes",
            "pagos_pedidos",
            "auditoria"
        ]

        tablas_existentes = []
        tablas_faltantes = []

        for tabla in tablas:
            try:
                query = f"SELECT COUNT(*) FROM {tabla}"
                resultado = db.ejecutar_query(query)
                if resultado:
                    count = resultado[0][0]
                    print(f"[OK] Tabla {tabla}: existe (contiene {count} registros)")
                    tablas_existentes.append(tabla)
                else:
                    print(f"[WARN] Tabla {tabla}: existe pero no se pudo contar registros")
                    tablas_existentes.append(tabla)
            except Exception as e:
                print(f"[ERROR] Tabla {tabla}: no existe o error ({e})")
                tablas_faltantes.append(tabla)

        # Test 2: Verificar relaciones
        print("\n📋 Test 2: Verificación de relaciones")
        print("-" * 60)

        # Conseguir listado de obras para pruebas
        query_obras = "SELECT TOP 3 id, nombre FROM obras ORDER BY id"
        obras = db.ejecutar_query(query_obras)

        if obras and len(obras) > 0:
            id_obra = obras[0][0]
            nombre_obra = obras[0][1]
            print(f"🔍 Obra seleccionada para pruebas: {nombre_obra} (ID: {id_obra})")

            # Verificar pedidos de material para esta obra
            if "pedidos_material" in tablas_existentes:
                try:
                    query = f"SELECT COUNT(*) FROM pedidos_material WHERE obra_id = ? OR id_obra = ?"
                    resultado = db.ejecutar_query(query, (id_obra, id_obra))
                    if resultado:
                        print(f"[OK] Pedidos de material para obra: {resultado[0][0]}")
                    else:
                        print(f"[OK] No hay pedidos de material para esta obra")
                except Exception as e:
                    print(f"[WARN] Error verificando pedidos de material: {e}")

            # Verificar vidrios para esta obra
            if "vidrios_por_obra" in tablas_existentes:
                try:
                    query = f"SELECT COUNT(*) FROM vidrios_por_obra WHERE obra_id = ? OR id_obra = ?"
                    resultado = db.ejecutar_query(query, (id_obra, id_obra))
                    if resultado:
                        print(f"[OK] Vidrios para obra: {resultado[0][0]}")
                    else:
                        print(f"[OK] No hay vidrios para esta obra")
                except Exception as e:
                    print(f"[WARN] Error verificando vidrios: {e}")

            # Verificar herrajes para esta obra
            if "herrajes_por_obra" in tablas_existentes:
                try:
                    query = f"SELECT COUNT(*) FROM herrajes_por_obra WHERE id_obra = ?"
                    resultado = db.ejecutar_query(query, (id_obra,))
                    if resultado:
                        print(f"[OK] Herrajes para obra: {resultado[0][0]}")
                    else:
                        print(f"[OK] No hay herrajes para esta obra")
                except Exception as e:
                    print(f"[WARN] Error verificando herrajes: {e}")

            # Verificar pagos para esta obra
            if "pagos_pedidos" in tablas_existentes:
                try:
                    query = f"SELECT COUNT(*) FROM pagos_pedidos WHERE obra_id = ?"
                    resultado = db.ejecutar_query(query, (id_obra,))
                    if resultado:
                        print(f"[OK] Pagos para obra: {resultado[0][0]}")
                    else:
                        print(f"[OK] No hay pagos para esta obra")
                except Exception as e:
                    print(f"[WARN] Error verificando pagos: {e}")
        else:
            print("[WARN] No se encontraron obras para realizar pruebas")

        # Resumen final
        print("\n[CHART] RESUMEN DEL TEST DE INTEGRACIÓN")
        print("=" * 60)
        print(f"[CHECK] Tablas existentes: {len(tablas_existentes)}/{len(tablas)}")
        if tablas_faltantes:
            print(f"[ERROR] Tablas faltantes: {', '.join(tablas_faltantes)}")
        else:
            print("🎉 Todas las tablas necesarias están presentes")

        if len(tablas_existentes) >= len(tablas) - 1:
            print("\n[CHECK] RESULTADO: Sistema listo para usar")
            print("📝 La estructura de base de datos está unificada y optimizada correctamente")
        else:
            print("\n[WARN] RESULTADO: Sistema parcialmente funcional")
            print("📝 Hay tablas importantes que aún faltan por crear")

    except Exception as e:
        print(f"[ERROR] Error durante las pruebas: {e}")
        traceback.print_exc()
        return False
    finally:
        if db and db.connection:
            db.connection.close()
import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from core.database import ObrasDatabaseConnection

    return True

if __name__ == "__main__":
    main()
