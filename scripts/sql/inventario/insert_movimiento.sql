-- Inserción segura de movimientos de inventario en el historial
-- Utiliza parámetros seguros para prevenir SQL injection
-- Registra todas las operaciones de stock para auditoría

INSERT INTO historial (
    accion,
    descripcion,
    usuario,
    fecha,
    detalles
) VALUES (
    ?,  -- accion (ej: 'INVENTARIO_ENTRADA', 'INVENTARIO_SALIDA', etc.)
    ?,  -- descripcion del movimiento
    ?,  -- usuario que realiza la operación
    ?,  -- fecha del movimiento
    ?   -- detalles adicionales en formato JSON o texto
);