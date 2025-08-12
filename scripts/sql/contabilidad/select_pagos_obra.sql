-- Obtiene pagos por obra con filtros opcionales
-- Parámetros: obra_id, categoria (pueden ser NULL)
SELECT 
    id, obra_id, concepto, categoria, monto, fecha_pago,
    metodo_pago, estado, usuario_creacion, fecha_creacion,
    observaciones
FROM pagos_obra
WHERE 
    (? IS NULL OR obra_id = ?)
    AND (? IS NULL OR ? = 'Todas' OR categoria = ?)
ORDER BY fecha_pago DESC