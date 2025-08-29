-- sql/02_inventario/consultas/count_inventario_activo.sql
-- Descripción: Cuenta productos activos en inventario
-- Parámetros: :categoria (opcional)
-- Retorna: COUNT(*) de productos activos

SELECT COUNT(*) 
FROM inventario 
WHERE activo = 1
  AND (:categoria IS NULL OR categoria = :categoria);