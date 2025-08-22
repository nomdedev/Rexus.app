-- Crear tabla pedidos_detalle (SQL Server)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_detalle')
CREATE TABLE pedidos_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT,
    codigo_producto NVARCHAR(50),
    descripcion NVARCHAR(255) NOT NULL,
    categoria NVARCHAR(100),
    cantidad DECIMAL(10,3) NOT NULL,
    unidad_medida NVARCHAR(10) NOT NULL DEFAULT 'UND',
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_item DECIMAL(10,2) NOT NULL DEFAULT 0,
    subtotal_item DECIMAL(10,2) NOT NULL,
    observaciones_item NVARCHAR(MAX),
    cantidad_entregada DECIMAL(10,3) NOT NULL DEFAULT 0,
    fecha_creacion DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);