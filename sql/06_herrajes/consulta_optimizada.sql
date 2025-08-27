-- consulta_optimizada.sql
-- Módulo: herrajes
-- Generado automáticamente el: 2025-08-22 23:18:58
-- Archivo original: D:\martin\Rexus.app\rexus\modules\herrajes\model.py
-- Línea original: 129

-- CONSULTA ORIGINAL (PROBLEMÁTICA):
-- SELECT * FROM herrajes WHERE activo = 1

-- QUERY OPTIMIZADA - Generada automáticamente
-- Problemas identificados:
-- - SELECT * - Evitar seleccionar todas las columnas
-- - SELECT * - Selecciona columnas específicas
-- Índices sugeridos se encuentran al final del archivo

SELECT
    -- Especificar columnas necesarias
    columna1,
    columna2,
    columna3 FROM herrajes WHERE activo = 1

-- ÍNDICES SUGERIDOS PARA OPTIMIZACIÓN:
-- Ejecutar estos comandos para mejorar el rendimiento:

CREATE INDEX IF NOT EXISTS idx_herrajes_tabla_principal_activo ON tabla_principal(activo);

-- PARÁMETROS DE EJEMPLO:
-- :param1 - Descripción del parámetro
-- :param2 - Descripción del parámetro

-- USO DESDE PYTHON:
-- from rexus.utils.sql_query_manager import SQLQueryManager
-- sql_manager = SQLQueryManager()
-- resultado = sql_manager.ejecutar_consulta_archivo('sql/herrajes/consulta_optimizada.sql', parametros)