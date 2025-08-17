-- Creación de tabla de detalle de pedidos
-- Archivo: create_pedidos_detalle_table.sql
-- Módulo: Pedidos
-- Descripción: Crea la tabla de detalle de items por pedido

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_detalle' AND xtype='U')
CREATE TABLE pedidos_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT,
    codigo_producto NVARCHAR(50),
    descripcion NVARCHAR(255) NOT NULL,
    categoria NVARCHAR(100),
    cantidad DECIMAL(10,3) NOT NULL,
    unidad_medida NVARCHAR(20) NOT NULL DEFAULT 'UND',
    precio_unitario DECIMAL(12,2) NOT NULL,
    descuento_item DECIMAL(12,2) NOT NULL DEFAULT 0,
    subtotal_item DECIMAL(12,2) NOT NULL,
    observaciones_item NTEXT,
    cantidad_entregada DECIMAL(10,3) NOT NULL DEFAULT 0,
    cantidad_pendiente AS (cantidad - cantidad_entregada) PERSISTED,
    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);
