-- consulta_optimizada.sql
-- Módulo: logistica
-- Generado automáticamente el: 2025-08-22 23:18:58
-- Archivo original: D:\martin\Rexus.app\rexus\modules\logistica\model.py
-- Línea original: 81

-- CONSULTA ORIGINAL (PROBLEMÁTICA):
-- SELECT * FROM sysobjects WHERE name=? AND xtype='U

-- QUERY OPTIMIZADA - Generada automáticamente
-- Problemas identificados:
-- - SELECT * - Evitar seleccionar todas las columnas
-- - SELECT * - Selecciona columnas específicas
-- Índices sugeridos se encuentran al final del archivo

SELECT
    -- Especificar columnas necesarias
    columna1,
    columna2,
    columna3 FROM sysobjects WHERE name=? AND xtype='U

-- ÍNDICES SUGERIDOS PARA OPTIMIZACIÓN:
-- Ejecutar estos comandos para mejorar el rendimiento:

CREATE INDEX IF NOT EXISTS idx_logistica_tabla_principal_xtype ON tabla_principal(xtype);
CREATE INDEX IF NOT EXISTS idx_logistica_tabla_principal_name ON tabla_principal(name);

-- PARÁMETROS DE EJEMPLO:
-- :param1 - Descripción del parámetro
-- :param2 - Descripción del parámetro

-- USO DESDE PYTHON:
-- from rexus.utils.sql_query_manager import SQLQueryManager
-- sql_manager = SQLQueryManager()
-- resultado = sql_manager.ejecutar_consulta_archivo('sql/logistica/consulta_optimizada.sql', parametros)