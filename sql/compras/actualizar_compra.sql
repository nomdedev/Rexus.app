-- Script para actualizar una compra existente
-- Parámetros: :id, :estado, :fecha_entrega, :total, :descuento, :impuestos, :observaciones
-- Retorna: Filas afectadas

UPDATE compras 
SET 
    estado = ISNULL(:estado, estado),
    fecha_entrega = ISNULL(:fecha_entrega, fecha_entrega),
    total = ISNULL(:total, total),
    descuento = ISNULL(:descuento, descuento),
    impuestos = ISNULL(:impuestos, impuestos),
    total_final = ISNULL(:total, total) - ISNULL(:descuento, descuento) + ISNULL(:impuestos, impuestos),
    observaciones = ISNULL(:observaciones, observaciones),
    fecha_actualizacion = GETDATE()
WHERE id = :id AND activo = 1;

SELECT @@ROWCOUNT as filas_afectadas;