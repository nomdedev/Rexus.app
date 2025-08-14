#!/usr/bin/env python
"""Test script to verify all fixes"""

print("=== Testing Critical Fixes ===")

try:
    print("1. Testing module imports...")
    modules = ['inventario','vidrios','herrajes','obras','usuarios','compras','pedidos','auditoria','configuracion','logistica','mantenimiento']
    for module in modules:
        __import__(f'rexus.modules.{module}.view')
        print(f"  {module}: OK")

    print("\n2. Testing AuditoriaModel data_sanitizer...")
    from rexus.modules.auditoria.model import AuditoriaModel
    # Create with minimal connection
    model = AuditoriaModel()
    has_data_sanitizer = hasattr(model, 'data_sanitizer')
    print(f"  data_sanitizer attribute: {'OK' if has_data_sanitizer else 'MISSING'}")

    print("\n3. Testing AuditoriaView methods...")
    from rexus.modules.auditoria.view import AuditoriaView
    view = AuditoriaView()
    has_normal_method = hasattr(view, 'cargar_registros_auditoria')
    has_accent_method = hasattr(view, 'cargar_registros_auditoría')
    print(f"  cargar_registros_auditoria: {'OK' if has_normal_method else 'MISSING'}")
    print(f"  cargar_registros_auditoría: {'OK' if has_accent_method else 'MISSING'}")

    print("\n4. Testing database tables...")
    from rexus.core.database import get_inventario_connection
    conn = get_inventario_connection()
    if conn:
        cursor = conn.cursor()
        tables_to_check = ['compras', 'detalle_compras']
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table} table: OK ({count} records)")
            except Exception as e:
                print(f"  {table} table: MISSING")
        conn.close()
    else:
        print("  Database connection: FAILED")

    print("\n=== All Tests Completed ===")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
