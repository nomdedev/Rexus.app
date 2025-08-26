-- consulta_optimizada.sql
-- Módulo: inventario
-- Generado automáticamente el: 2025-08-22 23:18:58
-- Archivo original: D:\martin\Rexus.app\rexus\modules\inventario\submodules\reservas_manager.py
-- Línea original: 814

-- CONSULTA ORIGINAL (PROBLEMÁTICA):
-- SELECT * FROM ? WHERE id = ?

-- QUERY OPTIMIZADA - Generada automáticamente
-- Problemas identificados:
-- - SELECT * - Selecciona columnas específicas
-- Índices sugeridos se encuentran al final del archivo

SELECT
    -- Especificar columnas necesarias
    columna1,
    columna2,
    columna3 FROM ? WHERE id = ?

-- ÍNDICES SUGERIDOS PARA OPTIMIZACIÓN:
-- Ejecutar estos comandos para mejorar el rendimiento:

CREATE INDEX IF NOT EXISTS idx_inventario_tabla_principal_id ON tabla_principal(id);

-- PARÁMETROS DE EJEMPLO:
-- :param1 - Descripción del parámetro
-- :param2 - Descripción del parámetro

-- USO DESDE PYTHON:
-- from rexus.utils.sql_query_manager import SQLQueryManager
-- sql_manager = SQLQueryManager()
-- resultado = sql_manager.ejecutar_consulta_archivo('sql/inventario/consulta_optimizada.sql', parametros)