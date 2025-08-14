#!/usr/bin/env python3
"""
Optimizador de Rendimiento de Base de Datos para Rexus.app

Analiza las consultas y tablas para crear índices óptimos que mejoren el rendimiento.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class IndexRecommendation:
    """Recomendación de índice."""
    table: str
    columns: List[str]
    index_type: str  # 'btree', 'hash', 'composite'
    reason: str
    priority: str  # 'high', 'medium', 'low'
    estimated_impact: str


class DatabasePerformanceOptimizer:
    """Optimizador de rendimiento de base de datos."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.models_dir = root_dir / "rexus" / "modules"
        self.recommendations = []

        # Patrones comunes de consultas que se benefician de índices
        self.query_patterns = [
            # WHERE clauses
            r'WHERE\s+(\w+)\s*=',
            r'WHERE\s+(\w+)\s+IN',
            r'WHERE\s+(\w+)\s+LIKE',
            r'WHERE\s+(\w+)\s+BETWEEN',
            r'WHERE\s+(\w+)\s*<',
            r'WHERE\s+(\w+)\s*>',

            # JOIN conditions
            r'JOIN\s+\w+\s+ON\s+\w+\.(\w+)\s*=',
            r'LEFT\s+JOIN\s+\w+\s+ON\s+\w+\.(\w+)\s*=',
            r'INNER\s+JOIN\s+\w+\s+ON\s+\w+\.(\w+)\s*=',

            # ORDER BY
            r'ORDER\s+BY\s+(\w+)',

            # GROUP BY
            r'GROUP\s+BY\s+(\w+)',
        ]

        # Tablas principales identificadas
        self.main_tables = {
            'usuarios': ['username', 'email', 'estado', 'fecha_creacion'],
            'inventario': ['codigo', 'categoria', 'proveedor', 'estado', 'fecha_creacion'],
            'compras': ['numero_orden', 'proveedor', 'estado', 'fecha_pedido'],
            'mantenimientos': ['equipo_id', 'tipo', 'estado', 'fecha_programada'],
            'equipos': ['codigo', 'tipo', 'estado', 'ubicacion'],
            'obras': ['codigo', 'cliente', 'estado', 'fecha_inicio'],
            'pedidos': ['numero', 'cliente', 'estado', 'fecha_pedido'],
            'vidrios': ['codigo', 'tipo', 'color', 'proveedor'],
            'herrajes': ['codigo', 'categoria', 'proveedor'],
            'logistica': ['codigo_envio', 'destino', 'estado', 'fecha_envio']
        }

    def analyze_model_files(self) -> Dict[str, List[str]]:
        """Analiza archivos de modelo para encontrar patrones de consulta."""
        query_analysis = {}

        for module_dir in self.models_dir.iterdir():
            if module_dir.is_dir():
                model_file = module_dir / "model.py"
                if model_file.exists():
                    queries = self.extract_queries_from_file(model_file)
                    if queries:
                        query_analysis[module_dir.name] = queries

        return query_analysis

    def extract_queries_from_file(self, file_path: Path) -> List[str]:
        """Extrae consultas SQL de un archivo."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Buscar consultas SQL
            sql_patterns = [
                r'SELECT[^;]+',
                r'UPDATE[^;]+',
                r'DELETE[^;]+',
                r'INSERT[^;]+',
            ]

            queries = []
            for pattern in sql_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                queries.extend(matches)

            return queries

        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return []

    def analyze_query_patterns(self, queries: List[str]) -> Set[Tuple[str, str]]:
        """Analiza patrones en las consultas para identificar campos que necesitan índices."""
        indexed_fields = set()

        for query in queries:
            for pattern in self.query_patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                for match in matches:
                    # Intentar identificar la tabla
                    table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
                    if table_match:
                        table = table_match.group(1)
                        indexed_fields.add((table, match))

        return indexed_fields

    def generate_basic_recommendations(self):
        """Genera recomendaciones básicas de índices para tablas principales."""

        # Índices primarios y únicos esenciales
        for table, columns in self.main_tables.items():
            # Índice en campo de identificación principal
            if 'codigo' in columns:
                self.recommendations.append(IndexRecommendation(
                    table=table,
                    columns=['codigo'],
                    index_type='btree',
                    reason='Campo de identificación único usado frecuentemente en búsquedas',
                    priority='high',
                    estimated_impact='Alto - Mejora significativa en consultas por código'
                ))

            # Índice en estado para filtros
            if 'estado' in columns:
                self.recommendations.append(IndexRecommendation(
                    table=table,
                    columns=['estado'],
                    index_type='btree',
                    reason='Campo estado usado frecuentemente para filtrar registros activos/inactivos',
                    priority='high',
                    estimated_impact='Alto - Mejora filtros por estado'
                ))

            # Índice en fecha de creación para ordenamiento temporal
            if 'fecha_creacion' in columns:
                self.recommendations.append(IndexRecommendation(
                    table=table,
                    columns=['fecha_creacion'],
                    index_type='btree',
                    reason='Campo fecha usado para ordenamiento cronológico y filtros temporales',
                    priority='medium',
                    estimated_impact='Medio - Mejora consultas temporales y paginación'
                ))

            # Índices compuestos para consultas combinadas comunes
            if 'estado' in columns and 'fecha_creacion' in columns:
                self.recommendations.append(IndexRecommendation(
                    table=table,
                    columns=['estado', 'fecha_creacion'],
                    index_type='composite',
                    reason='Combinación común en filtros por estado con ordenamiento temporal',
                    priority='medium',
                    estimated_impact='Medio - Optimiza consultas combinadas estado-fecha'
                ))

    def generate_specific_recommendations(self):
        """Genera recomendaciones específicas por módulo."""

        # Usuarios - Índices para autenticación y búsqueda
        self.recommendations.extend([
            IndexRecommendation(
                table='usuarios',
                columns=['username'],
                index_type='btree',
                reason='Campo username usado en autenticación (búsquedas frecuentes)',
                priority='high',
                estimated_impact='Crítico - Mejora tiempo de login significativamente'
            ),
            IndexRecommendation(
                table='usuarios',
                columns=['email'],
                index_type='btree',
                reason='Campo email usado para recuperación de contraseñas y validación',
                priority='high',
                estimated_impact='Alto - Mejora validaciones y recuperación de cuenta'
            )
        ])

        # Inventario - Índices para gestión de stock
        self.recommendations.extend([
            IndexRecommendation(
                table='inventario',
                columns=['categoria', 'estado'],
                index_type='composite',
                reason='Consultas frecuentes por categoría y estado para reportes de stock',
                priority='high',
                estimated_impact='Alto - Optimiza reportes de inventario por categoría'
            ),
            IndexRecommendation(
                table='inventario',
                columns=['proveedor'],
                index_type='btree',
                reason='Búsquedas por proveedor para gestión de compras',
                priority='medium',
                estimated_impact='Medio - Mejora búsquedas por proveedor'
            )
        ])

        # Compras - Índices para gestión de órdenes
        self.recommendations.extend([
            IndexRecommendation(
                table='compras',
                columns=['numero_orden'],
                index_type='btree',
                reason='Búsquedas por número de orden para seguimiento',
                priority='high',
                estimated_impact='Alto - Mejora búsquedas de órdenes específicas'
            ),
            IndexRecommendation(
                table='compras',
                columns=['proveedor', 'estado'],
                index_type='composite',
                reason='Reportes por proveedor filtrados por estado',
                priority='medium',
                estimated_impact='Medio - Optimiza reportes de compras por proveedor'
            )
        ])

        # Mantenimiento - Índices para programación
        self.recommendations.extend([
            IndexRecommendation(
                table='mantenimientos',
                columns=['equipo_id'],
                index_type='btree',
                reason='Consultas por equipo para historial de mantenimiento',
                priority='high',
                estimated_impact='Alto - Mejora consultas de historial por equipo'
            ),
            IndexRecommendation(
                table='mantenimientos',
                columns=['fecha_programada', 'estado'],
                index_type='composite',
                reason='Consultas para calendario de mantenimientos pendientes',
                priority='high',
                estimated_impact='Alto - Optimiza calendario de mantenimientos'
            )
        ])

        # Auditoria - Índices para trazabilidad
        self.recommendations.extend([
            IndexRecommendation(
                table='auditoria',
                columns=['usuario', 'fecha'],
                index_type='composite',
                reason='Consultas de auditoría por usuario en rangos de tiempo',
                priority='medium',
                estimated_impact='Medio - Mejora consultas de auditoría'
            ),
            IndexRecommendation(
                table='auditoria',
                columns=['accion'],
                index_type='btree',
                reason='Filtros por tipo de acción en reportes de auditoría',
                priority='low',
                estimated_impact='Bajo - Mejora filtros por tipo de acción'
            )
        ])

    def generate_sql_scripts(self) -> List[str]:
        """Genera scripts SQL para crear los índices."""
        sql_scripts = []

        # Header del script
        sql_scripts.append("""
-- ====================================================
-- SCRIPT DE OPTIMIZACIÓN DE RENDIMIENTO - REXUS.APP
-- Índices para mejorar rendimiento de consultas
-- ====================================================

-- Verificar si un índice existe antes de crearlo
-- (Compatible con SQL Server)

""")

        for rec in self.recommendations:
            # Generar nombre del índice
            if len(rec.columns) == 1:
                index_name = f"IX_{rec.table}_{rec.columns[0]}"
            else:
                index_name = f"IX_{rec.table}_{'_'.join(rec.columns)}"

            # Generar script SQL
            columns_str = ', '.join(rec.columns)

            sql_script = f"""
-- {rec.reason}
-- Impacto: {rec.estimated_impact}
-- Prioridad: {rec.priority.upper()}
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = '{index_name}' AND object_id = OBJECT_ID('{rec.table}'))
BEGIN
    CREATE INDEX {index_name} ON {rec.table} ({columns_str});
    PRINT 'Índice {index_name} creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice {index_name} ya existe';
END
GO

"""
            sql_scripts.append(sql_script)

        return sql_scripts

    def save_optimization_script(self, output_path: Path):
        """Guarda el script de optimización."""
        sql_scripts = self.generate_sql_scripts()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(sql_scripts)

        print(f"Script de optimización guardado en: {output_path}")

    def generate_performance_report(self) -> str:
        """Genera reporte de recomendaciones de rendimiento."""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE OPTIMIZACIÓN DE RENDIMIENTO - REXUS.APP")
        report.append("=" * 60)
        report.append("")

        # Resumen
        high_priority = [r for r in self.recommendations if r.priority == 'high']
        medium_priority = [r for r in self.recommendations if r.priority == 'medium']
        low_priority = [r for r in self.recommendations if r.priority == 'low']

        report.append("RESUMEN DE RECOMENDACIONES:")
        report.append(f"- Total de índices recomendados: {len(self.recommendations)}")
        report.append(f"- Prioridad ALTA: {len(high_priority)} índices")
        report.append(f"- Prioridad MEDIA: {len(medium_priority)} índices")
        report.append(f"- Prioridad BAJA: {len(low_priority)} índices")
        report.append("")

        # Recomendaciones por prioridad
        for priority,
recs in [("ALTA",
            high_priority),
            ("MEDIA",
            medium_priority),
            ("BAJA",
            low_priority)]:
            if recs:
                report.append(f"RECOMENDACIONES DE PRIORIDAD {priority}:")
                report.append("-" * 40)

                for i, rec in enumerate(recs, 1):
                    report.append(f"{i}. Tabla: {rec.table}")
                    report.append(f"   Columnas: {', '.join(rec.columns)}")
                    report.append(f"   Tipo: {rec.index_type}")
                    report.append(f"   Razón: {rec.reason}")
                    report.append(f"   Impacto: {rec.estimated_impact}")
                    report.append("")

        # Beneficios esperados
        report.append("BENEFICIOS ESPERADOS:")
        report.append("-" * 20)
        report.append("• Mejora significativa en tiempo de respuesta de consultas")
        report.append("• Reducción en uso de CPU para búsquedas")
        report.append("• Mejor rendimiento en reportes y listados")
        report.append("• Optimización de consultas de autenticación")
        report.append("• Aceleración de filtros y ordenamientos")
        report.append("")

        # Implementación
        report.append("IMPLEMENTACIÓN:")
        report.append("-" * 15)
        report.append("1. Ejecutar script SQL de optimización")
        report.append("2. Monitorear rendimiento después de aplicar índices")
        report.append("3. Ajustar índices según patrones de uso reales")
        report.append("4. Considerar mantenimiento periódico de índices")
        report.append("")

        return '\n'.join(report)

    def run_optimization_analysis(self):
        """Ejecuta el análisis completo de optimización."""
        print("=== ANÁLISIS DE OPTIMIZACIÓN DE RENDIMIENTO ===")
        print()

        # Generar recomendaciones
        print("Generando recomendaciones básicas...")
        self.generate_basic_recommendations()

        print("Generando recomendaciones específicas...")
        self.generate_specific_recommendations()

        # Generar archivos de salida
        scripts_dir = self.root_dir / "scripts" / "database"
        scripts_dir.mkdir(exist_ok=True)

        # Script SQL
        sql_script_path = scripts_dir / "performance_optimization.sql"
        self.save_optimization_script(sql_script_path)

        # Reporte
        report_content = self.generate_performance_report()
        report_path = scripts_dir / "performance_optimization_report.txt"
        report_path.write_text(report_content, encoding='utf-8')

        print(f"Reporte guardado en: {report_path}")
        print()

        # Mostrar resumen
        print("RESUMEN:")
        print(f"- {len(self.recommendations)} índices recomendados")
        high_priority = [r for r in self.recommendations if r.priority == 'high']
        print(f"- {len(high_priority)} de prioridad ALTA")
        print()

        return len(self.recommendations)


def main():
    """Función principal."""
    # Obtener directorio raíz del proyecto
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    print(f"Directorio del proyecto: {root_dir}")
    print()

    # Crear optimizador y ejecutar análisis
    optimizer = DatabasePerformanceOptimizer(root_dir)
    total_recommendations = optimizer.run_optimization_analysis()

    print(f"[OK] Analisis completado: {total_recommendations} recomendaciones generadas")
    print()
    print("Para aplicar las optimizaciones:")
    print("1. Revisar el archivo: scripts/database/performance_optimization.sql")
    print("2. Ejecutar el script en la base de datos")
    print("3. Monitorear el rendimiento después de la implementación")


if __name__ == "__main__":
    main()
