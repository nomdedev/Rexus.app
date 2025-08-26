-- ALTER TABLE statements para agregar columnas faltantes en vidrios
-- Ejecutar en SQL Server para compatibilidad con queries de productos

-- 1. Agregar campos básicos de producto
ALTER TABLE vidrios 
ADD codigo nvarchar(50) NOT NULL DEFAULT 'AUTO_' + CAST(id as nvarchar(10));

ALTER TABLE vidrios 
ADD descripcion nvarchar(255) NOT NULL DEFAULT '';

ALTER TABLE vidrios 
ADD categoria nvarchar(50) NOT NULL DEFAULT 'VIDRIO';

ALTER TABLE vidrios 
ADD subcategoria nvarchar(50) NULL;

-- 2. Agregar campos de stock
ALTER TABLE vidrios 
ADD stock_actual decimal(10,2) NULL DEFAULT 0;

ALTER TABLE vidrios 
ADD stock_minimo decimal(10,2) NULL DEFAULT 0;

ALTER TABLE vidrios 
ADD stock_maximo decimal(10,2) NULL DEFAULT 1000;

ALTER TABLE vidrios 
ADD stock_reservado decimal(10,2) NULL DEFAULT 0;

ALTER TABLE vidrios 
ADD stock_disponible decimal(10,2) NULL;

-- 3. Agregar campos de precios
ALTER TABLE vidrios 
ADD precio_unitario decimal(10,2) NULL DEFAULT 0;

ALTER TABLE vidrios 
ADD precio_promedio decimal(10,2) NULL DEFAULT 0;

ALTER TABLE vidrios 
ADD costo_unitario decimal(10,2) NULL DEFAULT 0;

-- 4. Agregar campos técnicos
ALTER TABLE vidrios 
ADD unidad_medida nvarchar(20) NULL DEFAULT 'M2';

ALTER TABLE vidrios 
ADD ubicacion nvarchar(100) NULL;

ALTER TABLE vidrios 
ADD material nvarchar(50) NULL;

ALTER TABLE vidrios 
ADD marca nvarchar(50) NULL;

ALTER TABLE vidrios 
ADD modelo nvarchar(50) NULL;

ALTER TABLE vidrios 
ADD acabado nvarchar(50) NULL;

-- 5. Agregar campos de proveedor
ALTER TABLE vidrios 
ADD codigo_proveedor nvarchar(50) NULL;

ALTER TABLE vidrios 
ADD tiempo_entrega_dias int NULL DEFAULT 0;

-- 6. Agregar campos de metadatos
ALTER TABLE vidrios 
ADD propiedades_especiales nvarchar(max) NULL;

ALTER TABLE vidrios 
ADD observaciones nvarchar(max) NULL;

ALTER TABLE vidrios 
ADD codigo_qr nvarchar(255) NULL;

ALTER TABLE vidrios 
ADD imagen_url nvarchar(255) NULL;

-- 7. Agregar campos de auditoría
ALTER TABLE vidrios 
ADD usuario_creacion nvarchar(50) NULL;

ALTER TABLE vidrios 
ADD usuario_modificacion nvarchar(50) NULL;

-- 8. Copiar datos existentes donde corresponda
UPDATE vidrios 
SET 
    stock_actual = ISNULL(stock, 0),
    precio_unitario = ISNULL(precio_m2, 0),
    material = 'VIDRIO'
WHERE stock IS NOT NULL OR precio_m2 IS NOT NULL;

-- 9. Crear trigger para calcular stock_disponible automáticamente
GO
CREATE OR ALTER TRIGGER tr_vidrios_stock_disponible
ON vidrios
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE vidrios 
    SET stock_disponible = stock_actual - ISNULL(stock_reservado, 0)
    WHERE id IN (SELECT id FROM inserted);
END;
GO

PRINT 'Columnas agregadas exitosamente a la tabla vidrios';
