-- Script seguro para actualizar cantidad pedida de herraje en obra
-- Uso: Ejecutar desde backend con parámetros seguros

UPDATE herrajes_obra 
SET cantidad_pedida = cantidad_pedida + ?
WHERE herraje_id = ? AND obra_id = ?;