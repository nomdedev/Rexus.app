-- 🔒 Obtener último ID insertado de forma segura
-- Reemplaza la vulnerabilidad @@IDENTITY con SCOPE_IDENTITY() que es más segura
-- SCOPE_IDENTITY() devuelve el último valor de identidad insertado en el mismo scope y sesión
SELECT SCOPE_IDENTITY() AS last_id;
