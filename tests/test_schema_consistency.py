# Mapeo de tablas a las columnas que deberían existir según la estructura REAL de la BD
EXPECTED_SCHEMA = {
    # Tabla de obras (BD: inventario)
import pytest

from core.database import MODULO_BASE_DATOS, DatabaseConnection

    'obras': [
        'id', 'nombre', 'direccion', 'telefono', 'fecha_creacion', 'cliente',
        'estado', 'fecha', 'fecha_entrega', 'cantidad_aberturas', 'fecha_compra',
        'pago_completo', 'pago_porcentaje', 'monto_usd', 'monto_ars', 'tipo_obra',
        'usuario_creador', 'fecha_medicion', 'dias_entrega', 'rowversion'
    ],
    # Tabla de inventario de items (BD: inventario)
    'inventario_items': [
        'id', 'codigo', 'nombre', 'tipo', 'stock_actual', 'stock_minimo',
        'ubicacion', 'descripcion', 'qr', 'imagen_referencia', 'rowversion'
    ],
    # Tabla de materiales (BD: inventario)
    'materiales': [
        'id', 'codigo', 'descripcion', 'tipo', 'unidad', 'stock', 'stock_minimo',
        'precio_unitario', 'cantidad', 'ubicacion'
    ],
    # Tabla de pedidos de herrajes (BD: inventario)
    'pedidos_herrajes': [
        'id', 'obra_id', 'tipo_herraje', 'descripcion', 'cantidad', 'estado',
        'fecha_pedido', 'fecha_entrega_estimada', 'usuario_id', 'proveedor',
        'costo', 'observaciones'
    ],
    # Tabla de pedidos de material (BD: inventario)
    'pedidos_material': [
        'id', 'obra_id', 'material_id', 'cantidad', 'estado', 'fecha_pedido',
        'fecha_entrega_estimada', 'usuario_id', 'proveedor', 'costo', 'observaciones'
    ],
    # Tabla de pedidos por obra (BD: inventario)
    'pedidos_obra': [
        'id', 'id_obra', 'id_material', 'tipo_item', 'cantidad_pedida',
        'cantidad_entregada', 'estado', 'precio_unitario', 'precio_total',
        'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega_real',
        'proveedor', 'observaciones', 'usuario'
    ],
    # Tabla de cronograma de obras (BD: inventario)
    'cronograma_obras': [
        'id', 'id_obra', 'etapa', 'fecha_programada', 'fecha_realizada',
        'observaciones', 'responsable', 'estado', 'fecha_inicio', 'fecha_fin'
    ],
    # Tabla de pagos por obra (BD: inventario)
    'pagos_obra': [
        'id', 'id_obra', 'concepto', 'tipo_pago', 'monto', 'fecha_pago',
        'fecha_vencimiento', 'estado', 'metodo_pago', 'comprobante',
        'observaciones', 'usuario', 'fecha_registro'
    ],
    # Tabla de logística por obra (BD: inventario)
    'logistica_por_obra': [
        'id', 'obra_id', 'estado_envio', 'fecha_envio', 'transportista', 'observaciones'
    ],
    # Tabla de usuarios en BD inventario (BD: inventario)
    'users': [
        'id', 'nombre', 'apellido', 'usuario', 'password', 'rol', 'email',
        'telefono', 'fecha_alta', 'ultimo_login', 'activo', 'ip_ultima'
    ],
    # Tabla de usuarios principal (BD: users)
    'usuarios': [
        'id', 'nombre', 'apellido', 'email', 'usuario', 'password_hash', 'rol',
        'estado', 'fecha_creacion', 'ultima_conexion', 'rowversion',
        'ip_ultimo_login', 'ultimo_login'
    ],
    # Tabla de auditoría (BD: auditoria)
    'auditoria': [
        'id', 'usuario_id', 'accion', 'tabla_afectada', 'fecha', 'estado',
        'justificativo', 'admin_id', 'razon'
    ]
}

# Mapeo específico de tabla a base de datos
TABLA_BASE_DATOS = {
    # Tablas en BD inventario
    'obras': 'inventario',
    'inventario_items': 'inventario',
    'materiales': 'inventario',
    'pedidos_herrajes': 'inventario',
    'pedidos_material': 'inventario',
    'pedidos_obra': 'inventario',
    'cronograma_obras': 'inventario',
    'pagos_obra': 'inventario',
    'logistica_por_obra': 'inventario',
    'users': 'inventario',

    # Tablas en BD users
    'usuarios': 'users',

    # Tablas en BD auditoria
    'auditoria': 'auditoria'
}

@pytest.mark.parametrize('table, expected_cols', EXPECTED_SCHEMA.items())
def test_table_columns_exist(table, expected_cols):
    """
    Verifica que cada tabla tenga exactamente las columnas esperadas.
    """
    db = DatabaseConnection()
    # Usar el mapeo específico de tabla a BD
    db_name = TABLA_BASE_DATOS.get(table, 'inventario')
    db.conectar_a_base(db_name)

    # Obtener columnas reales desde INFORMATION_SCHEMA
    rows = db.ejecutar_query(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION",
        (table,)
    )
    assert rows is not None, f"No se pudo obtener columnas para tabla {table} en BD {db_name}"
    actual_cols = [row[0] for row in rows]
    missing = set(expected_cols) - set(actual_cols)
    extra = set(actual_cols) - set(expected_cols)

    # Mensaje más informativo
    if missing or extra:
        print(f"\n🔍 Tabla: {table} (BD: {db_name})")
        print(f"📋 Columnas esperadas ({len(expected_cols)}): {expected_cols}")
        print(f"📋 Columnas reales ({len(actual_cols)}): {actual_cols}")
        if missing:
            print(f"❌ Faltan: {sorted(missing)}")
        if extra:
            print(f"➕ Extras: {sorted(extra)}")

    assert not missing, f"Faltan columnas en tabla '{table}': {sorted(missing)}"
    assert not extra, f"Columnas inesperadas en tabla '{table}': {sorted(extra)}"
