#!/usr/bin/env python3
"""
REPARADOR MÓDULO OBRAS - FASE 2: REFACTORIZACIÓN DE VISTA
==========================================================

Simplifica los métodos complejos de la vista, crea mapeo centralizado
de datos y mejora la legibilidad del código.
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def crear_mapeo_datos_centralizado():
    """Crea un módulo centralizado para mapeo de datos de obras."""
    
    print("🔧 CREANDO MAPEO DE DATOS CENTRALIZADO")
    print("=" * 50)
    
    mapeo_content = '''"""
Mapeo centralizado de datos para obras.
Evita índices hardcodeados y facilita mantenimiento.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime


class ObrasDataMapper:
    """Mapea datos de obras entre diferentes formatos."""
    
    # Índices de la estructura real de la base de datos
    INDICES_BD = {
        'id': 0,
        'nombre': 1,
        'descripcion': 26,
        'codigo': 20,
        'cliente': 5,
        'fecha_inicio': 22,
        'fecha_fin_estimada': 23,
        'estado': 6,
        'presupuesto_inicial': 24,
        'responsable': 21
    }
    
    # Índices de las columnas de la tabla UI
    INDICES_TABLA = {
        'codigo': 0,
        'nombre': 1,
        'cliente': 2,
        'responsable': 3,
        'fecha_inicio': 4,
        'fecha_fin': 5,
        'estado': 6,
        'presupuesto': 7,
        'acciones': 8
    }
    
    @classmethod
    def tupla_a_dict(cls, tupla_obra: Tuple) -> Dict[str, Any]:
        """Convierte una tupla de la BD a diccionario estructurado."""
        if not tupla_obra:
            return {}
        
        try:
            return {
                'id': cls._extraer_campo(tupla_obra, 'id'),
                'codigo': cls._extraer_campo(tupla_obra, 'codigo'),
                'nombre': cls._extraer_campo(tupla_obra, 'nombre'),
                'descripcion': cls._extraer_campo(tupla_obra, 'descripcion'),
                'cliente': cls._extraer_campo(tupla_obra, 'cliente'),
                'fecha_inicio': cls._formatear_fecha(cls._extraer_campo(tupla_obra, 'fecha_inicio')),
                'fecha_fin_estimada': cls._formatear_fecha(cls._extraer_campo(tupla_obra, 'fecha_fin_estimada')),
                'estado': cls._extraer_campo(tupla_obra, 'estado'),
                'presupuesto_inicial': cls._formatear_presupuesto(cls._extraer_campo(tupla_obra, 'presupuesto_inicial')),
                'responsable': cls._extraer_campo(tupla_obra, 'responsable')
            }
        except Exception as e:
            print(f"[MAPPER] Error mapeando tupla: {e}")
            return cls._dict_vacio()
    
    @classmethod
    def lista_tuplas_a_dicts(cls, tuplas_obras: List[Tuple]) -> List[Dict[str, Any]]:
        """Convierte una lista de tuplas a lista de diccionarios."""
        if not tuplas_obras:
            return []
        
        return [cls.tupla_a_dict(tupla) for tupla in tuplas_obras]
    
    @classmethod
    def dict_a_fila_tabla(cls, obra_dict: Dict[str, Any]) -> List[str]:
        """Convierte un diccionario de obra a lista para mostrar en tabla."""
        try:
            return [
                str(obra_dict.get('codigo', '')),
                str(obra_dict.get('nombre', '')),
                str(obra_dict.get('cliente', '')),
                str(obra_dict.get('responsable', '')),
                cls._formatear_fecha_tabla(obra_dict.get('fecha_inicio', '')),
                cls._formatear_fecha_tabla(obra_dict.get('fecha_fin_estimada', '')),
                str(obra_dict.get('estado', '')),
                cls._formatear_presupuesto_tabla(obra_dict.get('presupuesto_inicial', 0))
            ]
        except Exception as e:
            print(f"[MAPPER] Error convirtiendo a fila: {e}")
            return [''] * 8
    
    @classmethod
    def _extraer_campo(cls, tupla: Tuple, campo: str) -> Any:
        """Extrae un campo de la tupla usando el índice correcto."""
        indice = cls.INDICES_BD.get(campo)
        if indice is None:
            return ''
        
        if len(tupla) > indice:
            valor = tupla[indice]
            return valor if valor is not None else ''
        return ''
    
    @classmethod
    def _formatear_fecha(cls, fecha) -> str:
        """Formatea una fecha para almacenamiento."""
        if not fecha:
            return ''
        
        if isinstance(fecha, str):
            # Ya es string, verificar formato
            return fecha[:10] if len(fecha) >= 10 else fecha
        
        if hasattr(fecha, 'strftime'):
            return fecha.strftime('%Y-%m-%d')
        
        return str(fecha)
    
    @classmethod
    def _formatear_fecha_tabla(cls, fecha) -> str:
        """Formatea una fecha para mostrar en tabla."""
        fecha_formateada = cls._formatear_fecha(fecha)
        if not fecha_formateada:
            return ''
        
        try:
            # Convertir a formato más legible si es necesario
            if '-' in fecha_formateada and len(fecha_formateada) == 10:
                return fecha_formateada  # Ya está en formato YYYY-MM-DD
            return fecha_formateada
        except Exception:
            return str(fecha)
    
    @classmethod
    def _formatear_presupuesto(cls, presupuesto) -> float:
        """Formatea un presupuesto para almacenamiento."""
        if not presupuesto:
            return 0.0
        
        try:
            return float(presupuesto)
        except (ValueError, TypeError):
            return 0.0
    
    @classmethod
    def _formatear_presupuesto_tabla(cls, presupuesto) -> str:
        """Formatea un presupuesto para mostrar en tabla."""
        presupuesto_num = cls._formatear_presupuesto(presupuesto)
        if presupuesto_num == 0:
            return ''
        
        try:
            return f"${presupuesto_num:,.2f}"
        except Exception:
            return str(presupuesto)
    
    @classmethod
    def _dict_vacio(cls) -> Dict[str, Any]:
        """Retorna un diccionario vacío con la estructura correcta."""
        return {
            'id': '',
            'codigo': '',
            'nombre': '',
            'descripcion': '',
            'cliente': '',
            'fecha_inicio': '',
            'fecha_fin_estimada': '',
            'estado': '',
            'presupuesto_inicial': 0.0,
            'responsable': ''
        }
    
    @classmethod
    def validar_estructura_dict(cls, obra_dict: Dict[str, Any]) -> bool:
        """Valida que un diccionario tenga la estructura correcta."""
        campos_requeridos = [
            'id', 'codigo', 'nombre', 'cliente', 
            'estado', 'responsable'
        ]
        
        return all(campo in obra_dict for campo in campos_requeridos)


class ObrasTableHelper:
    """Helper para operaciones específicas de la tabla de obras."""
    
    @staticmethod
    def configurar_headers_tabla(tabla):
        """Configura los headers de la tabla de obras."""
        headers = [
            "Código", "Nombre", "Cliente", "Responsable",
            "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
        ]
        tabla.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos de columna
        if tabla.horizontalHeader():
            header = tabla.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 120)  # Código
            header.resizeSection(1, 200)  # Nombre
            header.resizeSection(2, 150)  # Cliente
            header.resizeSection(3, 150)  # Responsable
            header.resizeSection(4, 100)  # Fecha Inicio
            header.resizeSection(5, 100)  # Fecha Fin
            header.resizeSection(6, 100)  # Estado
            header.resizeSection(7, 120)  # Presupuesto
    
    @staticmethod
    def crear_boton_accion(texto: str, callback, fila: int):
        """Crea un botón de acción para una fila específica."""
        from PyQt6.QtWidgets import QPushButton
        
        btn = QPushButton(texto)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn.clicked.connect(lambda: callback(fila))
        return btn


class ObrasValidator:
    """Validador de datos de obras."""
    
    @staticmethod
    def validar_obra_dict(obra_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida un diccionario de obra y retorna errores si los hay."""
        errores = []
        
        # Validar campos requeridos
        if not obra_dict.get('nombre', '').strip():
            errores.append("El nombre es requerido")
        
        if not obra_dict.get('codigo', '').strip():
            errores.append("El código es requerido")
        
        if not obra_dict.get('cliente', '').strip():
            errores.append("El cliente es requerido")
        
        if not obra_dict.get('responsable', '').strip():
            errores.append("El responsable es requerido")
        
        # Validar formato de fechas
        fecha_inicio = obra_dict.get('fecha_inicio', '')
        if fecha_inicio and not ObrasValidator._validar_formato_fecha(fecha_inicio):
            errores.append("Formato de fecha de inicio inválido")
        
        fecha_fin = obra_dict.get('fecha_fin_estimada', '')
        if fecha_fin and not ObrasValidator._validar_formato_fecha(fecha_fin):
            errores.append("Formato de fecha de fin inválido")
        
        # Validar presupuesto
        presupuesto = obra_dict.get('presupuesto_inicial', 0)
        if presupuesto and presupuesto < 0:
            errores.append("El presupuesto no puede ser negativo")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def _validar_formato_fecha(fecha_str: str) -> bool:
        """Valida que una fecha tenga formato correcto."""
        if not fecha_str:
            return True  # Fecha vacía es válida
        
        try:
            if len(fecha_str) >= 10:
                datetime.strptime(fecha_str[:10], '%Y-%m-%d')
                return True
        except ValueError:
            pass
        
        return False
'''
    
    mapeo_path = Path("rexus/modules/obras/data_mapper.py")
    with open(mapeo_path, 'w', encoding='utf-8') as f:
        f.write(mapeo_content)
    
    print(f"✅ Mapeo de datos creado: {mapeo_path}")
    return True

def refactorizar_metodo_cargar_obras():
    """Refactoriza el método cargar_obras_en_tabla para reducir complejidad."""
    
    print("\n🔧 REFACTORIZANDO MÉTODO cargar_obras_en_tabla")
    print("=" * 50)
    
    # Leer el archivo view.py actual
    view_path = Path("rexus/modules/obras/view.py")
    
    with open(view_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Crear versión simplificada del método
    metodo_simplificado = '''    def cargar_obras_en_tabla(self, obras):
        """Carga las obras en la tabla usando el mapper centralizado."""
        try:
            from .data_mapper import ObrasDataMapper, ObrasTableHelper
            
            # Limpiar tabla
            self.tabla_obras.setRowCount(0)
            
            if not obras:
                print("[OBRAS VIEW] No hay obras para mostrar")
                return
            
            # Configurar número de filas
            self.tabla_obras.setRowCount(len(obras))
            
            for fila, obra in enumerate(obras):
                self._cargar_fila_obra(fila, obra)
                
            print(f"[OBRAS VIEW] {len(obras)} obras cargadas en tabla")
            
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando obras en tabla: {e}")
            import traceback
            traceback.print_exc()
    
    def _cargar_fila_obra(self, fila: int, obra):
        """Carga una fila individual de obra en la tabla."""
        try:
            from .data_mapper import ObrasDataMapper, ObrasTableHelper
            from PyQt6.QtWidgets import QTableWidgetItem
            
            # Convertir obra a diccionario si es necesario
            if isinstance(obra, dict):
                obra_dict = obra
            else:
                # Es tupla de la BD
                obra_dict = ObrasDataMapper.tupla_a_dict(obra)
            
            # Obtener datos formateados para la tabla
            datos_fila = ObrasDataMapper.dict_a_fila_tabla(obra_dict)
            
            # Cargar datos en las columnas
            for columna, dato in enumerate(datos_fila):
                item = QTableWidgetItem(str(dato))
                self.tabla_obras.setItem(fila, columna, item)
            
            # Agregar botón de acción en la última columna
            btn_editar = ObrasTableHelper.crear_boton_accion(
                "Editar", 
                self.editar_obra_desde_tabla, 
                fila
            )
            self.tabla_obras.setCellWidget(fila, ObrasDataMapper.INDICES_TABLA['acciones'], btn_editar)
            
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando fila {fila}: {e}")
            # Llenar con datos vacíos en caso de error
            for columna in range(8):  # 8 columnas de datos
                self.tabla_obras.setItem(fila, columna, QTableWidgetItem(""))'''
    
    # Buscar y reemplazar el método original
    inicio_metodo = contenido.find("def cargar_obras_en_tabla(self, obras):")
    if inicio_metodo == -1:
        print("❌ No se encontró el método cargar_obras_en_tabla")
        return False
    
    # Buscar el final del método
    lineas = contenido[inicio_metodo:].split('\n')
    fin_metodo = 1
    indentacion_base = None
    
    for i, linea in enumerate(lineas[1:], 1):
        if linea.strip() == '':
            continue
        
        # Detectar indentación base del primer contenido
        if indentacion_base is None and linea.strip():
            indentacion_base = len(linea) - len(linea.lstrip())
        
        # Si encontramos una línea con menor indentación, es el final del método
        if linea.strip() and len(linea) - len(linea.lstrip()) <= 4:  # Nivel de clase
            fin_metodo = i
            break
    
    # Crear backup
    backup_path = Path("backups_uiux/obras_view_backup_fase2.py")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"💾 Backup creado: {backup_path}")
    
    # Reemplazar método
    metodo_original = '\n'.join(lineas[:fin_metodo])
    contenido_nuevo = contenido.replace(metodo_original, metodo_simplificado)
    
    # Escribir archivo actualizado
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print("✅ Método cargar_obras_en_tabla refactorizado")
    return True

def agregar_validaciones_robustas():
    """Agrega validaciones robustas a la vista."""
    
    print("\n🔧 AGREGANDO VALIDACIONES ROBUSTAS")
    print("=" * 50)
    
    # Leer archivo view.py
    view_path = Path("rexus/modules/obras/view.py")
    
    with open(view_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Agregar método de validación al final de la clase ObrasView
    metodo_validacion = '''
    def validar_datos_obra(self, datos_obra: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida los datos de una obra antes de procesarlos."""
        try:
            from .data_mapper import ObrasValidator
            return ObrasValidator.validar_obra_dict(datos_obra)
        except Exception as e:
            print(f"[OBRAS VIEW] Error en validación: {e}")
            return False, [f"Error en validación: {str(e)}"]
    
    def mostrar_errores_validacion(self, errores: List[str]):
        """Muestra errores de validación al usuario."""
        try:
            from rexus.utils.message_system import show_error
            mensaje = "Errores encontrados:\\n\\n" + "\\n".join(f"• {error}" for error in errores)
            show_error(self, "⚠️ Datos inválidos", mensaje)
        except Exception as e:
            print(f"[OBRAS VIEW] Error mostrando errores: {e}")
    
    def cargar_datos_iniciales_seguro(self):
        """Versión segura de cargar_datos_iniciales con mejor manejo de errores."""
        try:
            if self.model is None:
                print("[OBRAS VIEW] No hay modelo disponible para cargar datos")
                self.cargar_obras_en_tabla([])
                return
            
            print("[OBRAS VIEW] Cargando datos iniciales...")
            obras = self.model.obtener_todas_obras()
            
            if obras:
                # Usar el mapper para convertir datos
                from .data_mapper import ObrasDataMapper
                obras_dict = ObrasDataMapper.lista_tuplas_a_dicts(obras)
                
                # Validar datos antes de cargar
                obras_validas = []
                for obra in obras_dict:
                    es_valida, errores = self.validar_datos_obra(obra)
                    if es_valida:
                        obras_validas.append(obra)
                    else:
                        print(f"[OBRAS VIEW] Obra inválida ignorada: {obra.get('codigo', 'Sin código')} - {errores}")
                
                self.cargar_obras_en_tabla(obras_validas)
                print(f"[OBRAS VIEW] {len(obras_validas)} obras válidas cargadas de {len(obras)} totales")
            else:
                print("[OBRAS VIEW] No hay obras para mostrar")
                self.cargar_obras_en_tabla([])
                
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando datos iniciales: {e}")
            import traceback
            traceback.print_exc()
            self.cargar_obras_en_tabla([])'''
    
    # Buscar el final de la clase ObrasView
    fin_clase = contenido.rfind("class DialogoObra(QDialog):")
    if fin_clase == -1:
        print("❌ No se encontró el final de la clase ObrasView")
        return False
    
    # Insertar métodos antes del DialogoObra
    contenido_nuevo = (
        contenido[:fin_clase] + 
        metodo_validacion + 
        "\n\n\n" + 
        contenido[fin_clase:]
    )
    
    # Reemplazar llamada a cargar_datos_iniciales con la versión segura
    contenido_nuevo = contenido_nuevo.replace(
        "self.cargar_datos_iniciales()",
        "self.cargar_datos_iniciales_seguro()"
    )
    
    # Escribir archivo actualizado
    with open(view_path, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print("✅ Validaciones robustas agregadas")
    return True

def crear_tests_unitarios():
    """Crea tests unitarios específicos para los métodos refactorizados."""
    
    print("\n🔧 CREANDO TESTS UNITARIOS")
    print("=" * 50)
    
    test_content = '''"""
Tests unitarios para los métodos refactorizados del módulo obras.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.data_mapper import ObrasDataMapper, ObrasValidator, ObrasTableHelper


class TestObrasDataMapper:
    """Tests para el mapper de datos de obras."""

    def test_tupla_a_dict_obra_completa(self):
        """Test: conversión de tupla completa a diccionario."""
        # Tupla simulando estructura real de BD (27 campos)
        tupla_obra = tuple([
            1,                          # 0: id
            "Edificio Central",         # 1: nombre
            None, None, None,           # 2-4: campos intermedios
            "Cliente A",                # 5: cliente
            "EN_PROCESO",               # 6: estado
            None, None, None, None,     # 7-10: campos intermedios
            None, None, None, None,     # 11-14: campos intermedios
            None, None, None, None,     # 15-18: campos intermedios
            None,                       # 19: campo intermedio
            "OBR-001",                  # 20: codigo
            "Juan Pérez",               # 21: responsable
            "2024-01-15",               # 22: fecha_inicio
            "2024-12-15",               # 23: fecha_fin_estimada
            150000.0,                   # 24: presupuesto_inicial
            None,                       # 25: campo intermedio
            "Construcción principal"    # 26: descripcion
        ])
        
        resultado = ObrasDataMapper.tupla_a_dict(tupla_obra)
        
        assert resultado['id'] == 1
        assert resultado['codigo'] == "OBR-001"
        assert resultado['nombre'] == "Edificio Central"
        assert resultado['cliente'] == "Cliente A"
        assert resultado['estado'] == "EN_PROCESO"
        assert resultado['responsable'] == "Juan Pérez"
        assert resultado['presupuesto_inicial'] == 150000.0

    def test_tupla_a_dict_obra_incompleta(self):
        """Test: conversión de tupla incompleta a diccionario."""
        tupla_obra = (1, "Obra Simple", "DESC", "Descripción")
        
        resultado = ObrasDataMapper.tupla_a_dict(tupla_obra)
        
        assert resultado['id'] == 1
        assert resultado['nombre'] == "Obra Simple"
        assert resultado['codigo'] == ''  # Campo faltante
        assert resultado['cliente'] == ''  # Campo faltante

    def test_tupla_vacia(self):
        """Test: manejo de tupla vacía."""
        resultado = ObrasDataMapper.tupla_a_dict(())
        
        assert resultado == {}

    def test_lista_tuplas_a_dicts(self):
        """Test: conversión de lista de tuplas."""
        tuplas = [
            (1, "Obra 1", None, None, None, "Cliente 1"),
            (2, "Obra 2", None, None, None, "Cliente 2")
        ]
        
        resultado = ObrasDataMapper.lista_tuplas_a_dicts(tuplas)
        
        assert len(resultado) == 2
        assert resultado[0]['id'] == 1
        assert resultado[1]['id'] == 2

    def test_dict_a_fila_tabla(self):
        """Test: conversión de diccionario a fila de tabla."""
        obra_dict = {
            'codigo': 'OBR-001',
            'nombre': 'Edificio Central',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': '2024-01-15',
            'fecha_fin_estimada': '2024-12-15',
            'estado': 'EN_PROCESO',
            'presupuesto_inicial': 150000.0
        }
        
        resultado = ObrasDataMapper.dict_a_fila_tabla(obra_dict)
        
        assert len(resultado) == 8
        assert resultado[0] == 'OBR-001'
        assert resultado[1] == 'Edificio Central'
        assert resultado[7] == '$150,000.00'

    def test_formatear_presupuesto_tabla(self):
        """Test: formateo de presupuesto para tabla."""
        assert ObrasDataMapper._formatear_presupuesto_tabla(150000) == '$150,000.00'
        assert ObrasDataMapper._formatear_presupuesto_tabla(0) == ''
        assert ObrasDataMapper._formatear_presupuesto_tabla(None) == ''

    def test_formatear_fecha_tabla(self):
        """Test: formateo de fecha para tabla."""
        assert ObrasDataMapper._formatear_fecha_tabla('2024-01-15 10:30:00') == '2024-01-15'
        assert ObrasDataMapper._formatear_fecha_tabla('2024-01-15') == '2024-01-15'
        assert ObrasDataMapper._formatear_fecha_tabla('') == ''


class TestObrasValidator:
    """Tests para el validador de obras."""

    def test_validar_obra_completa_valida(self):
        """Test: validación de obra completa y válida."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': '2024-01-15',
            'fecha_fin_estimada': '2024-12-15',
            'presupuesto_inicial': 150000.0
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is True
        assert len(errores) == 0

    def test_validar_obra_campos_faltantes(self):
        """Test: validación con campos requeridos faltantes."""
        obra_dict = {
            'nombre': '',  # Vacío
            'codigo': 'OBR-001',
            'cliente': '',  # Vacío
            'responsable': 'Juan Pérez'
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert 'El nombre es requerido' in errores
        assert 'El cliente es requerido' in errores

    def test_validar_fechas_invalidas(self):
        """Test: validación con fechas inválidas."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': 'fecha-invalida',
            'fecha_fin_estimada': '2024-13-45'  # Fecha imposible
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert any('fecha' in error.lower() for error in errores)

    def test_validar_presupuesto_negativo(self):
        """Test: validación con presupuesto negativo."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'presupuesto_inicial': -50000.0
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert 'negativo' in str(errores).lower()


class TestObrasTableHelper:
    """Tests para el helper de tabla."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    def test_crear_boton_accion(self, app):
        """Test: creación de botón de acción."""
        callback_llamado = False
        
        def callback_test(fila):
            nonlocal callback_llamado
            callback_llamado = True
            assert fila == 5
        
        boton = ObrasTableHelper.crear_boton_accion("Test", callback_test, 5)
        
        assert boton is not None
        assert boton.text() == "Test"
        
        # Simular click
        boton.click()
        assert callback_llamado is True


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
'''
    
    test_path = Path("tests/obras/test_obras_unitarios.py")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Tests unitarios creados: {test_path}")
    return True

def main():
    """Función principal de la Fase 2."""
    
    print("🚀 INICIANDO FASE 2: REFACTORIZACIÓN DE VISTA")
    print("=" * 60)
    
    try:
        # 1. Crear mapeo centralizado
        if not crear_mapeo_datos_centralizado():
            print("❌ Error creando mapeo centralizado")
            return False
        
        # 2. Refactorizar método complejo
        if not refactorizar_metodo_cargar_obras():
            print("❌ Error refactorizando método")
            return False
        
        # 3. Agregar validaciones
        if not agregar_validaciones_robustas():
            print("❌ Error agregando validaciones")
            return False
        
        # 4. Crear tests unitarios
        if not crear_tests_unitarios():
            print("❌ Error creando tests unitarios")
            return False
        
        print("\n🎉 FASE 2 COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ Mapeo de datos centralizado creado")
        print("✅ Método cargar_obras_en_tabla simplificado")
        print("✅ Validaciones robustas agregadas")
        print("✅ Tests unitarios creados")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Ejecutar tests unitarios")
        print("   2. Proceder con FASE 3: Mejoras de Seguridad")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante Fase 2: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
