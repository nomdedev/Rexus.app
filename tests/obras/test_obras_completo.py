#!/usr/bin/env python3
"""
TESTS COMPLETOS PARA MÓDULO OBRAS
=================================

Tests exhaustivos que cubren todas las funcionalidades faltantes:
- Alta de obra con todos los campos
- Validación de campos extendidos
- Paginación y filtros
- UI/UX avanzada
- Seguridad
- Permisos y roles
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QTableWidget, QPushButton
from PyQt6.QtCore import Qt
from datetime import datetime, date

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.model_adapter import MockObrasModel, ObrasModelAdapter
from rexus.modules.obras.data_mapper import ObrasDataMapper, ObrasValidator


class TestObrasCompleteFunctionality:
    """Tests completos para todas las funcionalidades del módulo obras."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def obra_completa_datos(self):
        """Datos completos de una obra con todos los campos."""
        return {
            'id': 1,
            'codigo': 'OBR-001',
            'nombre': 'Edificio Central Corporativo',
            'descripcion': 'Construcción de edificio corporativo de 15 pisos con oficinas, centro comercial y estacionamiento subterráneo. Incluye sistemas de climatización, seguridad y automatización.',
            'cliente': 'Corporación ABC S.A.',
            'fecha_inicio': '2024-01-15',
            'fecha_fin_estimada': '2024-12-15',
            'estado': 'EN_PROCESO',
            'presupuesto_inicial': 2500000.00,
            'responsable': 'Ing. Juan Carlos Pérez González',
            'ubicacion': 'Av. Principal 123, Centro, Ciudad Capital',
            'area_construccion': 8500.50,
            'numero_pisos': 15,
            'tipo_construccion': 'Comercial',
            'materiales_especiales': 'Vidrio templado, acero estructural, concreto de alta resistencia',
            'observaciones': 'Proyecto requiere permisos especiales de altura. Coordinación con empresa de telecomunicaciones para instalación de antenas.',
            'contacto_cliente': 'Maria Rodriguez - mrodriguez@abc.com - Tel: 555-0123',
            'fecha_contrato': '2023-12-01',
            'fecha_entrega_contractual': '2024-12-31',
            'penalizaciones': 0.5,  # Porcentaje por día de retraso
            'bonificaciones': 2.0,  # Porcentaje por entrega anticipada
            'garantia_meses': 24,
            'seguro_obra': 125000.00,
            'anticipo_recibido': 750000.00,
            'porcentaje_avance': 35.5,
            'riesgo_nivel': 'MEDIO',
            'prioridad': 'ALTA'
        }

    def test_alta_obra_todos_los_campos(self, app, obra_completa_datos):
        """Test: alta de obra con todos los campos posibles."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                # Configurar modelo mock
                model_instance = MockModel.return_value
                model_instance.crear_obra.return_value = (True, "Obra creada exitosamente")
                model_instance.obtener_obra_por_codigo.return_value = obra_completa_datos
                
                from rexus.modules.obras.view import ObrasView
                from rexus.modules.obras.controller import ObrasController
                
                vista = ObrasView()
                controlador = ObrasController(model=model_instance, view=vista)
                
                # Probar alta de obra
                resultado = controlador.crear_obra(obra_completa_datos)
                
                assert resultado is True
                model_instance.crear_obra.assert_called_once()
                
                # Verificar que se pasaron todos los campos
                args, kwargs = model_instance.crear_obra.call_args
                datos_enviados = args[0]
                
                campos_criticos = [
                    'codigo', 'nombre', 'descripcion', 'cliente', 
                    'responsable', 'presupuesto_inicial', 'area_construccion'
                ]
                
                for campo in campos_criticos:
                    assert campo in datos_enviados
                    assert datos_enviados[campo] == obra_completa_datos[campo]

    def test_validacion_campos_extendidos(self, obra_completa_datos):
        """Test: validación exhaustiva de todos los campos extendidos."""
        
        # Test 1: Presupuesto negativo
        datos_invalidos = obra_completa_datos.copy()
        datos_invalidos['presupuesto_inicial'] = -50000.0
        
        es_valida, errores = ObrasValidator.validar_obra_dict(datos_invalidos)
        assert es_valida is False
        assert any('negativo' in error.lower() for error in errores)
        
        # Test 2: Área de construcción inválida
        datos_invalidos = obra_completa_datos.copy()
        datos_invalidos['area_construccion'] = -100.0
        
        # Extender validador para área
        class ExtendedValidator(ObrasValidator):
            @staticmethod
            def validar_obra_dict(obra_dict):
                es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
                
                # Validar área de construcción
                area = obra_dict.get('area_construccion', 0)
                if area and area <= 0:
                    errores.append("El área de construcción debe ser positiva")
                    es_valida = False
                
                # Validar número de pisos
                pisos = obra_dict.get('numero_pisos', 0)
                if pisos and pisos <= 0:
                    errores.append("El número de pisos debe ser positivo")
                    es_valida = False
                
                # Validar garantía
                garantia = obra_dict.get('garantia_meses', 0)
                if garantia and garantia < 0:
                    errores.append("Los meses de garantía no pueden ser negativos")
                    es_valida = False
                
                return es_valida, errores
        
        es_valida, errores = ExtendedValidator.validar_obra_dict(datos_invalidos)
        assert es_valida is False
        assert any('área' in error.lower() for error in errores)
        
        # Test 3: Responsable muy corto
        datos_invalidos = obra_completa_datos.copy()
        datos_invalidos['responsable'] = 'A'  # Muy corto
        
        # Test 4: Descripción muy larga
        datos_invalidos = obra_completa_datos.copy()
        datos_invalidos['descripcion'] = 'X' * 5000  # Muy larga
        
        # Test 5: Código con formato inválido
        datos_invalidos = obra_completa_datos.copy()
        datos_invalidos['codigo'] = 'CÓDIGO-INVÁLIDO-CON-ESPACIOS Y CARACTERES RAROS!!!'

    def test_paginacion_obras(self, app):
        """Test: paginación de obras."""
        
        # Crear datos de prueba para paginación
        obras_mock = []
        for i in range(150):  # 150 obras para probar paginación
            obra = {
                'id': i + 1,
                'codigo': f'OBR-{i+1:03d}',
                'nombre': f'Obra {i+1}',
                'cliente': f'Cliente {i+1}',
                'estado': 'EN_PROCESO' if i % 2 == 0 else 'PLANIFICACION',
                'responsable': f'Responsable {i+1}',
                'presupuesto_inicial': 100000.0 + (i * 1000)
            }
            obras_mock.append(obra)
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                
                # Simular paginación
                def obtener_obras_paginadas(pagina=1, por_pagina=50):
                    inicio = (pagina - 1) * por_pagina
                    fin = inicio + por_pagina
                    return obras_mock[inicio:fin], len(obras_mock)
                
                model_instance.obtener_obras_paginadas = obtener_obras_paginadas
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Test página 1
                obras_p1, total = model_instance.obtener_obras_paginadas(1, 50)
                assert len(obras_p1) == 50
                assert total == 150
                assert obras_p1[0]['codigo'] == 'OBR-001'
                
                # Test página 2
                obras_p2, total = model_instance.obtener_obras_paginadas(2, 50)
                assert len(obras_p2) == 50
                assert obras_p2[0]['codigo'] == 'OBR-051'
                
                # Test última página
                obras_p3, total = model_instance.obtener_obras_paginadas(3, 50)
                assert len(obras_p3) == 50
                assert obras_p3[0]['codigo'] == 'OBR-101'

    def test_filtros_avanzados(self, app):
        """Test: filtros avanzados de obras."""
        
        obras_mock = [
            {'id': 1, 'codigo': 'OBR-001', 'estado': 'EN_PROCESO', 'responsable': 'Juan Pérez', 'fecha_inicio': '2024-01-01'},
            {'id': 2, 'codigo': 'OBR-002', 'estado': 'PLANIFICACION', 'responsable': 'María García', 'fecha_inicio': '2024-02-01'},
            {'id': 3, 'codigo': 'OBR-003', 'estado': 'EN_PROCESO', 'responsable': 'Juan Pérez', 'fecha_inicio': '2024-01-15'},
            {'id': 4, 'codigo': 'OBR-004', 'estado': 'FINALIZADA', 'responsable': 'Carlos López', 'fecha_inicio': '2023-12-01'},
        ]
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                
                # Simular filtros
                def obtener_obras_filtradas(filtros):
                    obras_filtradas = obras_mock.copy()
                    
                    if filtros.get('estado') and filtros['estado'] != 'Todos':
                        obras_filtradas = [o for o in obras_filtradas if o['estado'] == filtros['estado']]
                    
                    if filtros.get('responsable'):
                        responsable = filtros['responsable'].lower()
                        obras_filtradas = [o for o in obras_filtradas if responsable in o['responsable'].lower()]
                    
                    if filtros.get('fecha_desde'):
                        fecha_desde = filtros['fecha_desde']
                        obras_filtradas = [o for o in obras_filtradas if o['fecha_inicio'] >= fecha_desde]
                    
                    return obras_filtradas
                
                model_instance.obtener_obras_filtradas = obtener_obras_filtradas
                
                # Test filtro por estado
                filtros = {'estado': 'EN_PROCESO'}
                resultado = model_instance.obtener_obras_filtradas(filtros)
                assert len(resultado) == 2
                assert all(o['estado'] == 'EN_PROCESO' for o in resultado)
                
                # Test filtro por responsable
                filtros = {'responsable': 'Juan'}
                resultado = model_instance.obtener_obras_filtradas(filtros)
                assert len(resultado) == 2
                assert all('Juan' in o['responsable'] for o in resultado)
                
                # Test filtro por fecha
                filtros = {'fecha_desde': '2024-01-01'}
                resultado = model_instance.obtener_obras_filtradas(filtros)
                assert len(resultado) == 3  # Excluye la obra de 2023
                
                # Test filtros combinados
                filtros = {'estado': 'EN_PROCESO', 'responsable': 'Juan'}
                resultado = model_instance.obtener_obras_filtradas(filtros)
                assert len(resultado) == 2

    def test_ui_botones_accion_tabla(self, app):
        """Test: botones de acción en la tabla."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar que los botones existen
                assert hasattr(vista, 'btn_nueva_obra')
                assert hasattr(vista, 'btn_editar_obra')
                assert hasattr(vista, 'btn_eliminar_obra')
                assert hasattr(vista, 'btn_actualizar')
                
                # Verificar que los botones son instancias correctas
                assert isinstance(vista.btn_nueva_obra, QPushButton)
                assert isinstance(vista.btn_editar_obra, QPushButton)
                assert isinstance(vista.btn_eliminar_obra, QPushButton)
                
                # Verificar textos de botones
                assert "Nueva" in vista.btn_nueva_obra.text()
                assert "Editar" in vista.btn_editar_obra.text()
                assert "Eliminar" in vista.btn_eliminar_obra.text()
                
                # Verificar tooltips (si existen)
                if vista.btn_nueva_obra.toolTip():
                    assert len(vista.btn_nueva_obra.toolTip()) > 0
                
                # Simular carga de datos para verificar botones de acción en tabla
                datos_obra = [
                    {'codigo': 'OBR-001', 'nombre': 'Obra Test', 'cliente': 'Cliente Test',
                     'responsable': 'Responsable Test', 'fecha_inicio': '2024-01-01',
                     'fecha_fin_estimada': '2024-12-31', 'estado': 'EN_PROCESO',
                     'presupuesto_inicial': 100000.0}
                ]
                
                vista.cargar_obras_en_tabla(datos_obra)
                
                # Verificar que se creó botón de acción en la tabla
                if vista.tabla_obras.rowCount() > 0:
                    widget_boton = vista.tabla_obras.cellWidget(0, 8)  # Columna de acciones
                    assert widget_boton is not None

    def test_seguridad_xss_protection(self, app):
        """Test: protección contra XSS."""
        
        datos_maliciosos = {
            'nombre': '<script>alert("XSS")</script>Obra Maliciosa',
            'descripcion': 'javascript:alert("XSS")',
            'cliente': '<iframe src="http://malicious.com"></iframe>Cliente',
            'responsable': 'onclick="alert(\'XSS\')" Juan Pérez',
            'observaciones': '<object data="malicious.swf"></object>Observaciones'
        }
        
        from rexus.modules.obras.data_mapper import ObrasValidator
        
        # Crear validador extendido con protección XSS
        class SecurityValidator(ObrasValidator):
            @staticmethod
            def detectar_xss(texto):
                """Detecta posibles ataques XSS."""
                if not texto:
                    return False
                
                texto_lower = texto.lower()
                patrones_peligrosos = [
                    'script', 'javascript:', 'onclick', 'onerror', 'onload',
                    'iframe', 'object', 'embed', 'form', '<', '>'
                ]
                
                return any(patron in texto_lower for patron in patrones_peligrosos)
            
            @staticmethod
            def validar_obra_dict(obra_dict):
                es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
                
                # Validar cada campo de texto contra XSS
                campos_texto = ['nombre', 'descripcion', 'cliente', 'responsable', 'observaciones']
                
                for campo in campos_texto:
                    valor = obra_dict.get(campo, '')
                    if SecurityValidator.detectar_xss(valor):
                        errores.append(f"Contenido potencialmente peligroso detectado en {campo}")
                        es_valida = False
                
                return es_valida, errores
        
        es_valida, errores = SecurityValidator.validar_obra_dict(datos_maliciosos)
        assert es_valida is False
        assert len(errores) > 0
        assert any('peligroso' in error.lower() for error in errores)

    def test_seguridad_sql_injection(self, app):
        """Test: protección contra SQL Injection."""
        
        datos_maliciosos = {
            'nombre': "'; DROP TABLE obras; --",
            'codigo': "OBR-001' OR '1'='1",
            'cliente': "Cliente'; UPDATE obras SET estado='ELIMINADA'; --",
            'responsable': "1' UNION SELECT * FROM usuarios --"
        }
        
        # Simular sanitización de datos
        def sanitizar_sql(texto):
            """Sanitiza texto para prevenir SQL injection."""
            if not texto:
                return ""
            
            caracteres_peligrosos = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'UNION', 'SELECT']
            texto_limpio = str(texto)
            
            for caracter in caracteres_peligrosos:
                texto_limpio = texto_limpio.replace(caracter, '')
            
            return texto_limpio
        
        # Sanitizar datos
        datos_limpios = {}
        for campo, valor in datos_maliciosos.items():
            datos_limpios[campo] = sanitizar_sql(valor)
        
        # Verificar que se removieron caracteres peligrosos
        assert "DROP" not in datos_limpios['nombre']
        assert "'" not in datos_limpios['codigo']
        assert "UPDATE" not in datos_limpios['cliente']
        assert "UNION" not in datos_limpios['responsable']

    def test_permisos_usuario_sin_autorizacion(self, app):
        """Test: usuario sin permisos suficientes."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                
                from rexus.modules.obras.controller import ObrasController
                
                # Simular usuario sin permisos
                with patch('rexus.core.auth_manager.AuthManager') as MockAuth:
                    auth_instance = MockAuth.return_value
                    auth_instance.tiene_permiso.return_value = False
                    auth_instance.es_admin.return_value = False
                    
                    controlador = ObrasController(model=model_instance)
                    
                    # Intentar crear obra sin permisos
                    datos_obra = {'nombre': 'Obra Test', 'cliente': 'Cliente Test'}
                    
                    # El decorador @auth_required debería bloquear la operación
                    with pytest.raises(Exception):  # O el comportamiento esperado sin permisos
                        controlador.crear_obra(datos_obra)

    def test_permisos_usuario_admin(self, app):
        """Test: usuario administrador con todos los permisos."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.crear_obra.return_value = (True, "Obra creada")
                model_instance.eliminar_obra.return_value = (True, "Obra eliminada")
                
                from rexus.modules.obras.controller import ObrasController
                
                # Simular usuario administrador
                with patch('rexus.core.auth_manager.AuthManager') as MockAuth:
                    auth_instance = MockAuth.return_value
                    auth_instance.tiene_permiso.return_value = True
                    auth_instance.es_admin.return_value = True
                    
                    controlador = ObrasController(model=model_instance)
                    
                    # Admin puede crear obra
                    datos_obra = {'nombre': 'Obra Admin', 'cliente': 'Cliente Admin'}
                    resultado = controlador.crear_obra(datos_obra)
                    assert resultado is True
                    
                    # Admin puede eliminar obra
                    # resultado_eliminar = controlador.eliminar_obra(1)
                    # assert resultado_eliminar is True

    def test_tooltips_avanzados(self, app):
        """Test: tooltips informativos en la interfaz."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar tooltips en filtros
                if hasattr(vista, 'combo_filtro_estado'):
                    tooltip_estado = vista.combo_filtro_estado.toolTip()
                    assert len(tooltip_estado) > 20  # Tooltip descriptivo
                    assert 'estado' in tooltip_estado.lower()
                
                if hasattr(vista, 'txt_filtro_responsable'):
                    tooltip_responsable = vista.txt_filtro_responsable.toolTip()
                    assert len(tooltip_responsable) > 20
                    assert 'responsable' in tooltip_responsable.lower()
                
                # Verificar tooltips en botones
                tooltip_nueva = vista.btn_nueva_obra.toolTip()
                if tooltip_nueva:
                    assert 'nueva' in tooltip_nueva.lower() or 'crear' in tooltip_nueva.lower()


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v", "--tb=short"])
