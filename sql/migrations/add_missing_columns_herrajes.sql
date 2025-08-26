-- ALTER TABLE statements para agregar columnas faltantes en herrajes
-- Ejecutar en SQL Server para compatibilidad con queries de productos

-- 1. Agregar campos de categorización
ALTER TABLE herrajes 
ADD subcategoria nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD tipo nvarchar(100) NULL;

-- 2. Agregar campos de stock avanzado
ALTER TABLE herrajes 
ADD stock_maximo decimal(10,2) NULL DEFAULT 1000;

ALTER TABLE herrajes 
ADD stock_reservado decimal(10,2) NULL DEFAULT 0;

ALTER TABLE herrajes 
ADD stock_disponible decimal(10,2) NULL;

-- 3. Agregar campos de precios y costos
ALTER TABLE herrajes 
ADD precio_promedio decimal(10,2) NULL DEFAULT 0;

ALTER TABLE herrajes 
ADD costo_unitario decimal(10,2) NULL DEFAULT 0;

-- 4. Agregar campos de ubicación y características físicas
ALTER TABLE herrajes 
ADD ubicacion nvarchar(100) NULL;

ALTER TABLE herrajes 
ADD color nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD material nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD marca nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD modelo nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD acabado nvarchar(50) NULL;

-- 5. Agregar campos de proveedor
ALTER TABLE herrajes 
ADD codigo_proveedor nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD tiempo_entrega_dias int NULL DEFAULT 0;

-- 6. Agregar campos técnicos y metadatos
ALTER TABLE herrajes 
ADD propiedades_especiales nvarchar(max) NULL;

ALTER TABLE herrajes 
ADD codigo_qr nvarchar(255) NULL;

-- 7. Agregar campos de auditoría
ALTER TABLE herrajes 
ADD usuario_creacion nvarchar(50) NULL;

ALTER TABLE herrajes 
ADD usuario_modificacion nvarchar(50) NULL;

-- 8. Crear trigger para calcular stock_disponible automáticamente
GO
CREATE OR ALTER TRIGGER tr_herrajes_stock_disponible
ON herrajes
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE herrajes 
    SET stock_disponible = stock_actual - ISNULL(stock_reservado, 0)
    WHERE id IN (SELECT id FROM inserted);
END;
GO

PRINT 'Columnas agregadas exitosamente a la tabla herrajes';
