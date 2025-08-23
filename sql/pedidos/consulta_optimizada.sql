-- consulta_optimizada.sql
-- Módulo: pedidos
-- Generado automáticamente el: 2025-08-22 23:18:58
-- Archivo original: D:\martin\Rexus.app\rexus\modules\pedidos\view_complete.py
-- Línea original: 309

-- CONSULTA ORIGINAL (PROBLEMÁTICA):
-- SELECT id, nombre FROM obras WHERE activo = 1 ORDER BY nombre

-- QUERY OPTIMIZADA - Generada automáticamente
-- Problemas identificados:
-- - ORDER BY sin LIMIT - Puede consumir mucha memoria
-- Índices sugeridos se encuentran al final del archivo

SELECT id, nombre FROM obras WHERE activo = 1 ORDER BY nombre

-- ÍNDICES SUGERIDOS PARA OPTIMIZACIÓN:
-- Ejecutar estos comandos para mejorar el rendimiento:

CREATE INDEX IF NOT EXISTS idx_pedidos_tabla_principal_nombre ON tabla_principal(nombre);
CREATE INDEX IF NOT EXISTS idx_pedidos_tabla_principal_activo ON tabla_principal(activo);

-- PARÁMETROS DE EJEMPLO:
-- :param1 - Descripción del parámetro
-- :param2 - Descripción del parámetro

-- USO DESDE PYTHON:
-- from rexus.utils.sql_query_manager import SQLQueryManager
-- sql_manager = SQLQueryManager()
-- resultado = sql_manager.ejecutar_consulta_archivo('sql/pedidos/consulta_optimizada.sql', parametros)