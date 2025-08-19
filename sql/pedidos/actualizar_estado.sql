-- Script para actualizar el estado de un pedido
-- Parámetros: :id, :nuevo_estado, :observaciones, :usuario_id
-- Retorna: Filas afectadas

UPDATE pedidos 
SET 
    estado = :nuevo_estado,
    observaciones = CASE 
        WHEN :observaciones IS NOT NULL THEN :observaciones
        ELSE observaciones
    END,
    fecha_actualizacion = GETDATE()
WHERE id = :id AND activo = 1;

-- Insertar en historial de cambios
INSERT INTO pedidos_historial (
    pedido_id,
    estado_anterior,
    estado_nuevo,
    fecha_cambio,
    usuario_id,
    observaciones
)
SELECT 
    :id,
    LAG(estado) OVER (ORDER BY fecha_creacion) as estado_anterior,
    :nuevo_estado,
    GETDATE(),
    :usuario_id,
    :observaciones
FROM pedidos 
WHERE id = :id;

SELECT @@ROWCOUNT as filas_afectadas;