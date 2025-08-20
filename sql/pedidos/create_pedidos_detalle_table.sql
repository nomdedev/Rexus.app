-- Crear tabla pedidos_detalle (SQLite)
CREATE TABLE IF NOT EXISTS pedidos_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    producto_id INTEGER,
    codigo_producto TEXT,
    descripcion TEXT NOT NULL,
    categoria TEXT,
    cantidad REAL NOT NULL,
    unidad_medida TEXT NOT NULL DEFAULT 'UND',
    precio_unitario REAL NOT NULL,
    descuento_item REAL NOT NULL DEFAULT 0,
    subtotal_item REAL NOT NULL,
    observaciones_item TEXT,
    cantidad_entregada REAL NOT NULL DEFAULT 0,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);