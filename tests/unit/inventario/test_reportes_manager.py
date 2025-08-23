# -*- coding: utf-8 -*-
"""
Tests unitarios para ReportesManager de Inventario - Rexus.app

Prueba todas las funcionalidades de generación de reportes, análisis ABC,
valoración de inventario, exportación y KPIs del sistema de reportes.

Fecha: 23/08/2025
Estado: Implementación completa de tests faltantes identificados en auditoría
"""

import pytest
import sys
import os
import tempfile
import json
import csv
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Configuración de encoding UTF-8 para compatibilidad
sys.stdout.reconfigure(encoding='utf-8')

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Imports del sistema
try:
    from rexus.modules.inventario.submodules.reportes_manager import ReportesManager
    from rexus.utils.sql_query_manager import SQLQueryManager
    from rexus.utils.app_logger import get_logger
except ImportError as e:
    pytest.skip(f, allow_module_level=True)

# Configurar logger
import logging
logger = logging.getLogger(__name__)


class TestReportesManager:
    """Tests para el gestor de reportes de inventario."""

    def setup_method(self):
        """Configuración para cada test."""
        self.mock_db = Mock()
        self.mock_cursor = Mock()
        self.mock_db.cursor.return_value = self.mock_cursor
        
        # Mock SQLQueryManager
        self.mock_sql_manager = Mock()
        
        # Datos de muestra
        self.sample_productos = [
            {
                'id': 1, 'codigo': 'PROD001', 'descripcion': 'Producto A',
                'categoria': 'Categoria1', 'stock': 100, 'precio_unitario': 25.50,
                'stock_minimo': 20, 'stock_maximo': 200, 'activo': True
            },
            {
                'id': 2, 'codigo': 'PROD002', 'descripcion': 'Producto B', 
                'categoria': 'Categoria2', 'stock': 50, 'precio_unitario': 45.00,
                'stock_minimo': 10, 'stock_maximo': 100, 'activo': True
            },
            {
                'id': 3, 'codigo': 'PROD003', 'descripcion': 'Producto C',
                'categoria': 'Categoria1', 'stock': 0, 'precio_unitario': 15.75,
                'stock_minimo': 5, 'stock_maximo': 50, 'activo': True
            }
        ]
        
        self.sample_movimientos = [
            {
                'id': 1, 'producto_id': 1, 'tipo': 'ENTRADA', 'cantidad': 50,
                'fecha': datetime.now() - timedelta(days=5), 'costo_unitario': 20.00
            },
            {
                'id': 2, 'producto_id': 1, 'tipo': 'SALIDA', 'cantidad': 25,
                'fecha': datetime.now() - timedelta(days=3), 'costo_unitario': None
            },
            {
                'id': 3, 'producto_id': 2, 'tipo': 'ENTRADA', 'cantidad': 30,
                'fecha': datetime.now() - timedelta(days=2), 'costo_unitario': 40.00
            }
        ]

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_generar_reporte_stock_basico(self, mock_sql_class):
        """Test generación básica de reporte de stock."""
        # Configurar mock
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_productos
        
        # Crear manager
        manager = ReportesManager(self.mock_db)
        
        # Generar reporte
        resultado = manager.generar_reporte_stock()
        
        # Verificaciones
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert 'productos' in resultado
        assert 'resumen' in resultado
        assert len(resultado['productos']) > 0
        
        # Verificar que se ejecutó la query
        self.mock_sql_manager.execute_query.assert_called()

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_generar_reporte_stock_con_filtros(self, mock_sql_class):
        """Test reporte de stock con filtros específicos."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = [self.sample_productos[0]]
        
        manager = ReportesManager(self.mock_db)
        
        filtros = {
            'categoria': 'Categoria1',
            'stock_minimo': 50,
            'solo_activos': True
        }
        
        resultado = manager.generar_reporte_stock(filtros=filtros)
        
        assert resultado is not None
        assert len(resultado['productos']) == 1
        assert resultado['productos'][0]['categoria'] == 'Categoria1'
        
        # Verificar que los filtros se pasaron correctamente
        call_args = self.mock_sql_manager.execute_query.call_args
        assert call_args is not None

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_generar_reporte_movimientos(self, mock_sql_class):
        """Test generación de reporte de movimientos."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_movimientos
        
        manager = ReportesManager(self.mock_db)
        
        fecha_inicio = datetime.now() - timedelta(days=7)
        fecha_fin = datetime.now()
        
        resultado = manager.generar_reporte_movimientos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        assert resultado is not None
        assert 'movimientos' in resultado
        assert 'estadisticas' in resultado
        assert len(resultado['movimientos']) == len(self.sample_movimientos)
        
        # Verificar estadísticas calculadas
        assert 'total_entradas' in resultado['estadisticas']
        assert 'total_salidas' in resultado['estadisticas']

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_analisis_abc_inventario(self, mock_sql_class):
        """Test análisis ABC de clasificación de inventario."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        # Mock datos para análisis ABC
        productos_abc = [
            {'codigo': 'PROD001', 'valor_total': 2550.0, 'demanda_anual': 1000},
            {'codigo': 'PROD002', 'valor_total': 2250.0, 'demanda_anual': 500}, 
            {'codigo': 'PROD003', 'valor_total': 78.75, 'demanda_anual': 50}
        ]
        
        self.mock_sql_manager.execute_query.return_value = productos_abc
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.generar_analisis_abc()
        
        assert resultado is not None
        assert 'clasificacion' in resultado
        assert 'productos_a' in resultado['clasificacion']
        assert 'productos_b' in resultado['clasificacion'] 
        assert 'productos_c' in resultado['clasificacion']
        
        # Verificar que los productos se clasificaron
        total_productos = (
            len(resultado['clasificacion']['productos_a']) +
            len(resultado['clasificacion']['productos_b']) + 
            len(resultado['clasificacion']['productos_c'])
        )
        assert total_productos == len(productos_abc)

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_valoracion_inventario(self, mock_sql_class):
        """Test valoración total del inventario."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_productos
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.calcular_valoracion_inventario()
        
        assert resultado is not None
        assert 'valor_total' in resultado
        assert 'valor_por_categoria' in resultado
        assert 'productos_sin_stock' in resultado
        
        # Verificar cálculos
        assert isinstance(resultado['valor_total'], (int, float, Decimal))
        assert resultado['valor_total'] > 0

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_generar_dashboard_kpis(self, mock_sql_class):
        """Test generación de KPIs para dashboard."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        # Mock diferentes queries para KPIs
        self.mock_sql_manager.execute_query.side_effect = [
            [{'total': 150}],  # Total productos
            [{'total': 5}],    # Productos bajo stock mínimo
            [{'valor': 12500.50}],  # Valor total inventario
            [{'movimientos': 25}]   # Movimientos del mes
        ]
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.generar_kpis_dashboard()
        
        assert resultado is not None
        assert 'total_productos' in resultado
        assert 'productos_bajo_minimo' in resultado
        assert 'valor_total_inventario' in resultado
        assert 'movimientos_mes_actual' in resultado
        
        # Verificar tipos de datos
        assert isinstance(resultado['total_productos'], int)
        assert isinstance(resultado['valor_total_inventario'], (int, float))

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_exportar_reporte_csv(self, mock_sql_class):
        """Test exportación de reporte a formato CSV."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_productos
        
        manager = ReportesManager(self.mock_db)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            resultado = manager.exportar_reporte_csv(
                datos=self.sample_productos,
                archivo_destino=temp_path
            )
            
            assert resultado['success'] is True
            assert os.path.exists(temp_path)
            
            # Verificar contenido del archivo
            with open(temp_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == len(self.sample_productos)
                assert 'codigo' in rows[0]
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_exportar_reporte_json(self, mock_sql_class):
        """Test exportación de reporte a formato JSON."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_productos
        
        manager = ReportesManager(self.mock_db)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            resultado = manager.exportar_reporte_json(
                datos={'productos': self.sample_productos, 'timestamp': datetime.now().isoformat()},
                archivo_destino=temp_path
            )
            
            assert resultado['success'] is True
            assert os.path.exists(temp_path)
            
            # Verificar contenido JSON válido
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert 'productos' in data
                assert len(data['productos']) == len(self.sample_productos)
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_reporte_productos_sin_movimientos(self, mock_sql_class):
        """Test reporte de productos sin movimientos en período."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        productos_sin_movimientos = [
            {'id': 4, 'codigo': 'PROD004', 'descripcion': 'Producto Sin Movimiento',
             'stock': 10, 'ultimo_movimiento': None}
        ]
        
        self.mock_sql_manager.execute_query.return_value = productos_sin_movimientos
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.generar_reporte_productos_sin_movimientos(dias=30)
        
        assert resultado is not None
        assert 'productos' in resultado
        assert len(resultado['productos']) == 1
        assert resultado['productos'][0]['codigo'] == 'PROD004'

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_error_conexion_base_datos(self, mock_sql_class):
        """Test manejo de errores de conexión a base de datos."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.side_effect = ConnectionError("Error de conexión")
        
        manager = ReportesManager(None)  # Sin conexión
        resultado = manager.generar_reporte_stock()
        
        assert resultado is not None
        assert resultado.get('success') is False
        assert 'error' in resultado

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_filtros_fecha_invalidos(self, mock_sql_class):
        """Test manejo de filtros de fecha inválidos."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        manager = ReportesManager(self.mock_db)
        
        # Fechas inválidas (inicio posterior al fin)
        fecha_inicio = datetime.now()
        fecha_fin = datetime.now() - timedelta(days=5)
        
        resultado = manager.generar_reporte_movimientos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        assert resultado is not None
        assert resultado.get('success') is False
        assert 'error' in resultado

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_exportacion_archivo_sin_permisos(self, mock_sql_class):
        """Test manejo de errores de permisos en exportación."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = self.sample_productos
        
        manager = ReportesManager(self.mock_db)
        
        # Intentar escribir en directorio sin permisos (simulado)
        archivo_invalido = "/root/archivo_sin_permisos.csv"  # En Windows esto fallará
        
        with patch('builtins.open', side_effect=PermissionError("Sin permisos")):
            resultado = manager.exportar_reporte_csv(
                datos=self.sample_productos,
                archivo_destino=archivo_invalido
            )
            
            assert resultado['success'] is False
            assert 'error' in resultado

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_reporte_con_datos_vacios(self, mock_sql_class):
        """Test generación de reportes con datos vacíos."""
        mock_sql_class.return_value = self.mock_sql_manager
        self.mock_sql_manager.execute_query.return_value = []  # Sin datos
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.generar_reporte_stock()
        
        assert resultado is not None
        assert 'productos' in resultado
        assert len(resultado['productos']) == 0
        assert 'resumen' in resultado
        assert resultado['resumen']['total_productos'] == 0

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_calculo_tendencias_stock(self, mock_sql_class):
        """Test cálculo de tendencias de stock."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        # Mock datos históricos para tendencias
        datos_historicos = [
            {'fecha': '2025-08-01', 'stock_promedio': 120},
            {'fecha': '2025-08-15', 'stock_promedio': 110},
            {'fecha': '2025-08-23', 'stock_promedio': 100}
        ]
        
        self.mock_sql_manager.execute_query.return_value = datos_historicos
        
        manager = ReportesManager(self.mock_db)
        resultado = manager.calcular_tendencias_stock(producto_id=1)
        
        assert resultado is not None
        assert 'tendencia' in resultado
        assert 'proyeccion' in resultado
        # La tendencia debería ser negativa (stock disminuyendo)
        assert resultado['tendencia'] < 0

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')  
    def test_reporte_integracion_con_operaciones(self, mock_sql_class):
        """Test integración de reportes con operaciones de inventario."""
        mock_sql_class.return_value = self.mock_sql_manager
        
        # Simular que se registra un movimiento
        manager = ReportesManager(self.mock_db)
        
        # Mock: después de un movimiento, el reporte debe reflejar el cambio
        movimiento_data = {
            'producto_id': 1,
            'tipo': 'ENTRADA', 
            'cantidad': 25
        }
        
        # Simular datos actualizados después del movimiento
        productos_actualizados = self.sample_productos.copy()
        productos_actualizados[0]['stock'] += 25  # Stock aumentado
        
        self.mock_sql_manager.execute_query.return_value = productos_actualizados
        
        resultado = manager.generar_reporte_stock()
        
        # Verificar que el reporte refleja el cambio
        assert resultado['productos'][0]['stock'] == 125  # 100 + 25
        
        # Verificar que se actualiza el valor total
        assert resultado['resumen']['valor_total'] > 0


class TestReportesManagerIntegration:
    """Tests de integración para ReportesManager."""

    def setup_method(self):
        """Configuración para tests de integración."""
        self.mock_db = Mock()
        self.mock_cursor = Mock() 
        self.mock_db.cursor.return_value = self.mock_cursor

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_flujo_completo_generacion_exportacion(self, mock_sql_class):
        """Test flujo completo: generar reporte y exportar."""
        mock_sql_manager = Mock()
        mock_sql_class.return_value = mock_sql_manager
        
        # Datos de prueba
        productos = [
            {'codigo': 'P001', 'stock': 10, 'precio_unitario': 25.0},
            {'codigo': 'P002', 'stock': 5, 'precio_unitario': 50.0}
        ]
        
        mock_sql_manager.execute_query.return_value = productos
        
        manager = ReportesManager(self.mock_db)
        
        # 1. Generar reporte
        reporte = manager.generar_reporte_stock()
        assert reporte is not None
        assert len(reporte['productos']) == 2
        
        # 2. Exportar a CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            resultado_export = manager.exportar_reporte_csv(
                datos=reporte['productos'],
                archivo_destino=temp_path
            )
            
            assert resultado_export['success'] is True
            assert os.path.exists(temp_path)
            
            # Verificar que el archivo tiene el contenido correcto
            with open(temp_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
                assert 'P001' in contenido
                assert 'P002' in contenido
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch('rexus.modules.inventario.submodules.reportes_manager.SQLQueryManager')
    def test_performance_reportes_grandes(self, mock_sql_class):
        """Test performance con grandes volúmenes de datos."""
        mock_sql_manager = Mock()
        mock_sql_class.return_value = mock_sql_manager
        
        # Simular gran cantidad de productos
        productos_grandes = []
        for i in range(1000):
            productos_grandes.append({
                'id': i+1,
                'codigo': f'PROD{i+1:04d}',
                'stock': i % 100,
                'precio_unitario': (i % 50) + 10.0
            })
        
        mock_sql_manager.execute_query.return_value = productos_grandes
        
        manager = ReportesManager(self.mock_db)
        
        import time
        inicio = time.time()
        resultado = manager.generar_reporte_stock()
        fin = time.time()
        
        # El reporte debería completarse en menos de 2 segundos
        assert (fin - inicio) < 2.0
        assert len(resultado['productos']) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])