-- Script principal para el módulo Herrajes
-- Consulta todos los herrajes del sistema

SELECT 
    h.ID_Herraje,
    h.Nombre,
    h.Descripcion,
    h.Tipo,
    h.Material,
    h.Precio_Unitario,
    h.Stock_Actual,
    h.Stock_Minimo,
    h.Proveedor_ID,
    p.Nombre_Proveedor,
    p.Telefono as Telefono_Proveedor,
    p.Email as Email_Proveedor,
    h.Activo,
    h.Fecha_Creacion,
    h.Fecha_Modificacion
FROM Herrajes h
LEFT JOIN Proveedores p ON h.Proveedor_ID = p.ID_Proveedor
WHERE h.Activo = 1
ORDER BY h.Nombre ASC;
