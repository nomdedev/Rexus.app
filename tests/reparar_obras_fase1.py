#!/usr/bin/env python3
"""
REPARADOR MÓDULO OBRAS - FASE 1: TESTING
========================================

Corrige los problemas de testing del módulo obras para permitir
mocking y testing de integración adecuados.
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def reparar_view_para_testing():
    """Repara view.py para permitir testing adecuado."""
    
    print("🔧 REPARANDO VIEW.PY PARA TESTING")
    print("=" * 50)
    
    # Leer archivo actual
    view_path = Path("rexus/modules/obras/view.py")
    
    if not view_path.exists():
        print("[ERROR] Error: view.py no encontrado")
        return False
    
    with open(view_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # 1. Agregar import global de ObrasModel para testing
    print("📝 1. Agregando import global de ObrasModel...")
    
    # Buscar la línea donde se importa ObrasModel dinámicamente
    if "from .model import ObrasModel" not in contenido:
        print("[ERROR] Import dinámico no encontrado")
        return False
    
    # Agregar import global después de los imports existentes
    imports_adicionales = '''
# Import global para testing - permite mocking
try:
    from .model import ObrasModel
except ImportError:
    # Fallback para testing
    ObrasModel = None
'''
    
    # Insertar después de los imports de PyQt6
    linea_insercion = contenido.find("from .cronograma_view import CronogramaObrasView")
    if linea_insercion == -1:
        print("[ERROR] No se encontró punto de inserción")
        return False
    
    contenido_nuevo = (
        contenido[:linea_insercion] + 
        imports_adicionales + 
        "\n" + 
        contenido[linea_insercion:]
    )
    
    # 2. Simplificar init_model para usar import global
    print("📝 2. Simplificando init_model...")
    
    init_model_viejo = '''    def init_model(self):
        """Inicializar el modelo de obras."""
        try:
            from .model import ObrasModel
            from rexus.core.database import get_inventario_connection
            
            print("[OBRAS VIEW] Inicializando modelo...")
            # Obtener conexión a la base de datos
            db_conn = get_inventario_connection(auto_connect=True)
            if db_conn.connection:
                self.model = ObrasModel(db_conn.connection)
                print("[OBRAS VIEW] Modelo inicializado correctamente")
            else:
                print("[OBRAS VIEW] Error: No se pudo conectar a la base de datos")
                self.model = None
        except Exception as e:
            print(f"[OBRAS VIEW] Error inicializando modelo: {e}")
            import traceback
            traceback.print_exc()
            self.model = None'''
    
    init_model_nuevo = '''    def init_model(self):
        """Inicializar el modelo de obras."""
        try:
            from rexus.core.database import get_inventario_connection
            
            print("[OBRAS VIEW] Inicializando modelo...")
            
            # Verificar que ObrasModel esté disponible
            if ObrasModel is None:
                print("[OBRAS VIEW] ObrasModel no disponible")
                self.model = None
                return
            
            # Obtener conexión a la base de datos
            db_conn = get_inventario_connection(auto_connect=True)
            if db_conn and db_conn.connection:
                self.model = ObrasModel(db_conn.connection)
                print("[OBRAS VIEW] Modelo inicializado correctamente")
            else:
                print("[OBRAS VIEW] Error: No se pudo conectar a la base de datos")
                self.model = None
        except Exception as e:
            print(f"[OBRAS VIEW] Error inicializando modelo: {e}")
            import traceback
            traceback.print_exc()
            self.model = None'''
    
    contenido_nuevo = contenido_nuevo.replace(init_model_viejo, init_model_nuevo)
    
    # 3. Crear backup
    backup_path = Path("backups_uiux/obras_view_backup_testing.py")
    backup_path.parent.mkdir(exist_ok=True)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"💾 Backup creado: {backup_path}")
    
    # 4. Escribir archivo reparado
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print("[CHECK] view.py reparado para testing")
    
    return True

def crear_adapter_modelo():
    """Crea un adapter para el modelo que facilite testing."""
    
    print("\n🔧 CREANDO ADAPTER DE MODELO")
    print("=" * 50)
    
    adapter_content = '''"""
Adapter para el modelo de obras que facilita testing y desacoplamiento.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class ObrasModelInterface(ABC):
    """Interface para el modelo de obras."""
    
    @abstractmethod
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras."""
        pass
    
    @abstractmethod
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        pass
    
    @abstractmethod
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra."""
        pass
    
    @abstractmethod
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra existente."""
        pass
    
    @abstractmethod
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra."""
        pass
    
    @abstractmethod
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras con filtros aplicados."""
        pass


class ObrasModelAdapter(ObrasModelInterface):
    """Adapter que envuelve el modelo real de obras."""
    
    def __init__(self, modelo_real):
        """Inicializa el adapter con el modelo real."""
        self._modelo = modelo_real
    
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras."""
        if not self._modelo:
            return []
        return self._modelo.obtener_todas_obras()
    
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        if not self._modelo:
            return None
        return self._modelo.obtener_obra_por_id(obra_id)
    
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra."""
        if not self._modelo:
            return False
        return self._modelo.crear_obra(datos_obra)
    
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra existente."""
        if not self._modelo:
            return False
        return self._modelo.actualizar_obra(obra_id, datos)
    
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra."""
        if not self._modelo:
            return False
        return self._modelo.eliminar_obra(obra_id)
    
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras con filtros aplicados."""
        if not self._modelo:
            return []
        return self._modelo.obtener_obras_filtradas(filtros)


class MockObrasModel(ObrasModelInterface):
    """Mock del modelo de obras para testing."""
    
    def __init__(self):
        """Inicializa el mock con datos de prueba."""
        self._obras = [
            (1, "Edificio Central", "DESC001", "Construcción principal", 1, 
             "2024-01-15", "2024-12-15", None, "EN_PROCESO", "Activo", 
             25.5, 150000.0, 45000.0, 15.5, "Centro", "Juan Pérez", 
             "En proceso", 1, "2024-01-10", "2024-02-15", "OBR-001", 
             "Juan Pérez", "2024-01-15", "2024-12-15", 150000.0, None, 
             "Construcción de edificio principal"),
            (2, "Plaza Comercial", "DESC002", "Centro comercial", 2, 
             "2024-02-01", "2025-01-30", None, "PLANIFICACION", "Activo", 
             60.0, 250000.0, 120000.0, 12.0, "Norte", "María García", 
             "Sin observaciones", 1, "2024-01-20", "2024-03-01", "OBR-002", 
             "María García", "2024-02-01", "2025-01-30", 250000.0, None, 
             "Centro comercial fase 1")
        ]
    
    def obtener_todas_obras(self) -> List[Tuple]:
        """Obtiene todas las obras mock."""
        return self._obras.copy()
    
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID."""
        for obra in self._obras:
            if obra[0] == obra_id:
                return {
                    'id': obra[0],
                    'nombre': obra[1],
                    'codigo': obra[20] if len(obra) > 20 else f"OBR-{obra[0]:03d}",
                    'cliente': obra[5] if len(obra) > 5 else "Cliente Test",
                    'estado': obra[8] if len(obra) > 8 else "EN_PROCESO"
                }
        return None
    
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra mock."""
        nuevo_id = max(obra[0] for obra in self._obras) + 1 if self._obras else 1
        nueva_obra = (nuevo_id, datos_obra.get('nombre', 'Nueva Obra'), 
                     f"DESC{nuevo_id:03d}", "Descripción test", nuevo_id,
                     "2024-01-01", "2024-12-31", None, "PLANIFICACION", "Activo",
                     0.0, 100000.0, 0.0, 0.0, "Ubicación Test", "Responsable Test",
                     "Nueva obra", 1, "2024-01-01", "2024-01-01", f"OBR-{nuevo_id:03d}",
                     "Responsable Test", "2024-01-01", "2024-12-31", 100000.0, None,
                     datos_obra.get('descripcion', 'Descripción test'))
        self._obras.append(nueva_obra)
        return True
    
    def actualizar_obra(self, obra_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza una obra mock."""
        for i, obra in enumerate(self._obras):
            if obra[0] == obra_id:
                # Actualizar obra (simplificado para mock)
                obra_actualizada = list(obra)
                obra_actualizada[1] = datos.get('nombre', obra[1])
                self._obras[i] = tuple(obra_actualizada)
                return True
        return False
    
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra mock."""
        for i, obra in enumerate(self._obras):
            if obra[0] == obra_id:
                del self._obras[i]
                return True
        return False
    
    def obtener_obras_filtradas(self, filtros: Dict[str, Any]) -> List[Tuple]:
        """Obtiene obras filtradas mock."""
        obras_filtradas = self._obras.copy()
        
        if filtros.get('estado') and filtros['estado'] != 'Todos':
            obras_filtradas = [obra for obra in obras_filtradas 
                             if obra[8] == filtros['estado']]
        
        return obras_filtradas
'''
    
    adapter_path = Path("rexus/modules/obras/model_adapter.py")
    with open(adapter_path, 'w', encoding='utf-8') as f:
        f.write(adapter_content)
    
    print(f"[CHECK] Adapter creado: {adapter_path}")
    
    return True

def reparar_tests_integracion():
    """Repara los tests de integración para que funcionen."""
    
    print("\n🔧 REPARANDO TESTS DE INTEGRACIÓN")
    print("=" * 50)
    
    test_path = Path("tests/obras/test_obras_view_integration_fixed.py")
    
    test_content = '''"""
Tests de integración REPARADOS para la vista de obras.
Utilizan el nuevo adapter y mocking mejorado.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QTableWidget
from PyQt6.QtCore import Qt

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Imports reparados
from rexus.modules.obras.model_adapter import MockObrasModel, ObrasModelAdapter


class TestObrasViewDataLoadingFixed:
    """Tests REPARADOS para verificar la carga de datos en la vista de obras."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def mock_obras_model(self):
        """Mock del modelo de obras con datos de prueba."""
        return MockObrasModel()

    @pytest.fixture
    def obras_test_data(self):
        """Datos de prueba consistentes con el modelo real."""
        return [
            {
                'id': 1,
                'codigo': 'OBR-001',
                'nombre': 'Edificio Central',
                'descripcion': 'Construcción de edificio principal',
                'cliente': 'Cliente A',
                'fecha_inicio': '2024-01-15',
                'fecha_fin_estimada': '2024-12-15',
                'estado': 'EN_PROCESO',
                'presupuesto_inicial': 150000.0,
                'responsable': 'Juan Pérez'
            },
            {
                'id': 2,
                'codigo': 'OBR-002',
                'nombre': 'Plaza Comercial',
                'descripcion': 'Centro comercial fase 1',
                'cliente': 'Cliente B',
                'fecha_inicio': '2024-02-01',
                'fecha_fin_estimada': '2025-01-30',
                'estado': 'PLANIFICACION',
                'presupuesto_inicial': 250000.0,
                'responsable': 'María García'
            }
        ]

    def test_cargar_datos_iniciales_en_tabla_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: cargar datos iniciales en la tabla."""
        
        # Mock del modelo a nivel global
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            # Mock de la conexión de BD
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                # Importar y crear vista después del mock
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar que la tabla existe
                assert hasattr(vista, 'tabla_obras')
                assert isinstance(vista.tabla_obras, QTableWidget)
                
                # Cargar datos en formato de diccionario
                vista.cargar_obras_en_tabla(obras_test_data)
                
                # Verificar que los datos se cargaron
                assert vista.tabla_obras.rowCount() == len(obras_test_data)
                
                # Verificar contenido de la primera fila
                if vista.tabla_obras.rowCount() > 0:
                    codigo_item = vista.tabla_obras.item(0, 0)  # Columna código
                    nombre_item = vista.tabla_obras.item(0, 1)  # Columna nombre
                    
                    assert codigo_item is not None
                    assert nombre_item is not None
                    assert codigo_item.text() == "OBR-001"
                    assert nombre_item.text() == "Edificio Central"

    def test_actualizar_tabla_con_nuevos_datos_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: actualizar tabla cuando cambian los datos."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Cargar datos iniciales
                vista.cargar_obras_en_tabla(obras_test_data)
                assert vista.tabla_obras.rowCount() == 2
                
                # Agregar nueva obra
                nueva_obra = {
                    'id': 3,
                    'codigo': 'OBR-003',
                    'nombre': 'Residencial Los Pinos',
                    'descripcion': 'Conjunto residencial',
                    'cliente': 'Cliente C',
                    'fecha_inicio': '2024-03-01',
                    'fecha_fin_estimada': '2025-06-30',
                    'estado': 'PLANIFICACION',
                    'presupuesto_inicial': 180000.0,
                    'responsable': 'Carlos López'
                }
                
                obras_actualizadas = obras_test_data + [nueva_obra]
                vista.cargar_obras_en_tabla(obras_actualizadas)
                
                # Verificar actualización
                assert vista.tabla_obras.rowCount() == 3

    def test_tabla_vacia_cuando_no_hay_datos_fixed(self, app, mock_obras_model):
        """Test REPARADO: tabla vacía cuando no hay datos."""
        
        # Configurar mock para devolver lista vacía
        mock_obras_model._obras = []
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Cargar datos vacíos
                vista.cargar_obras_en_tabla([])
                
                # Verificar tabla vacía
                assert vista.tabla_obras.rowCount() == 0

    def test_manejo_errores_carga_datos_fixed(self, app):
        """Test REPARADO: manejo de errores al cargar datos."""
        
        # Mock que simula error en el modelo
        mock_model_error = Mock()
        mock_model_error.obtener_todas_obras.side_effect = Exception("Error de BD")
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_model_error):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar que no se produce crash
                assert vista.tabla_obras.rowCount() == 0
                assert vista.model is not None  # Modelo se inicializó aunque falló la carga

    def test_formato_fechas_en_tabla_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: verificar formato correcto de fechas."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                vista.cargar_obras_en_tabla(obras_test_data)
                
                # Verificar formato de fecha
                if vista.tabla_obras.rowCount() > 0:
                    fecha_item = vista.tabla_obras.item(0, 4)  # Columna fecha inicio
                    assert fecha_item is not None
                    
                    fecha_text = fecha_item.text()
                    # Verificar que la fecha está en formato correcto (sin hora)
                    assert len(fecha_text) == 10  # YYYY-MM-DD
                    assert fecha_text.count('-') == 2

    def test_columnas_tabla_configuradas_correctamente_fixed(self, app, mock_obras_model):
        """Test REPARADO: verificar configuración de columnas."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar número de columnas
                assert vista.tabla_obras.columnCount() == 9
                
                # Verificar headers
                headers_esperados = [
                    "Código", "Nombre", "Cliente", "Responsable",
                    "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
                ]
                
                for i, header_esperado in enumerate(headers_esperados):
                    header_actual = vista.tabla_obras.horizontalHeaderItem(i)
                    assert header_actual is not None
                    assert header_actual.text() == header_esperado


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
'''
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"[CHECK] Tests reparados creados: {test_path}")
    
    return True

def main():
    """Función principal de reparación."""
    
    print("[ROCKET] INICIANDO REPARACIÓN MÓDULO OBRAS - FASE 1")
    print("=" * 60)
    
    try:
        # 1. Reparar view.py para testing
        if not reparar_view_para_testing():
            print("[ERROR] Error reparando view.py")
            return False
        
        # 2. Crear adapter de modelo
        if not crear_adapter_modelo():
            print("[ERROR] Error creando adapter")
            return False
        
        # 3. Reparar tests de integración
        if not reparar_tests_integracion():
            print("[ERROR] Error reparando tests")
            return False
        
        print("\n🎉 FASE 1 COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("[CHECK] view.py reparado para testing")
        print("[CHECK] Adapter de modelo creado")
        print("[CHECK] Tests de integración reparados")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Ejecutar tests reparados")
        print("   2. Proceder con FASE 2: Refactorización de Vista")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error durante reparación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
