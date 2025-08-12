-- Obtener todas las categorías disponibles
-- Archivo: obtener_categorias.sql
-- Módulo: Inventario/Productos
-- Descripción: Lista categorías únicas ordenadas

SELECT DISTINCT categoria
FROM [inventario]
WHERE activo = 1
    AND categoria IS NOT NULL
    AND categoria != ''
ORDER BY categoria ASC;

-- Ejemplo de uso en Python:
-- cursor.execute(query)
-- categorias = [row[0] for row in cursor.fetchall()]
