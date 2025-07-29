#!/usr/bin/env python3
"""
Generador de Checklists Completados por Módulo
==============================================

Este script genera checklists de verificación completados automáticamente
para cada módulo basándose en el análisis estructural previo.

Funcionalidades:
- Analiza la estructura real de cada módulo
- Completa automáticamente los checks que pueden verificarse por código
- Identifica áreas que requieren verificación manual
- Genera informes de checklist en formato markdown
- Sugiere mejoras específicas basadas en hallazgos

Autor: Sistema de Análisis Automático
Fecha: 2025-06-25
"""

class GeneradorChecklist:
    """Generador automático de checklists de verificación por módulo."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

    def __init__(self, proyecto_root: str):
        self.proyecto_root = Path(proyecto_root)
        self.modulos_dir = self.proyecto_root / "modules"
        self.tests_dir = self.proyecto_root / "tests"
        self.informes_dir = self.proyecto_root / "informes_modulos"
        self.checklists_dir = self.proyecto_root / "docs" / "checklists_completados"

        # Crear directorio de checklists si no existe
        self.checklists_dir.mkdir(parents=True, exist_ok=True)

        # Patrones para detectar características específicas
        self.patrones = {
            'feedback_loading': [
                r'loading.*=.*True',
                r'spinner.*show',
                r'setCursor.*Qt\.WaitCursor',
                r'progress.*setValue',
                r'setEnabled.*False.*#.*loading'
            ],
            'feedback_error': [
                r'QMessageBox.*critical',
                r'show_error',
                r'error_message',
                r'raise.*Exception',
                r'except.*Exception'
            ],
            'feedback_success': [
                r'QMessageBox.*information',
                r'show_success',
                r'success_message',
                r'operacion.*exitosa'
            ],
            'sql_seguro': [
                r'execute.*\?',
                r'executemany',
                r'prepared.*statement',
                r'parametrized.*query'
            ],
            'validacion': [
                r'validate.*',
                r'if.*not.*\w+:',
                r'isinstance.*\(',
                r'len.*\w+.*>.*0'
            ],
            'transacciones': [
                r'BEGIN.*TRANSACTION',
                r'COMMIT',
                r'ROLLBACK',
                r'transaction.*\('
            ]
        }

    def analizar_modulo(self, nombre_modulo: str) -> Dict[str, Any]:
        """Analiza un módulo específico y extrae información para el checklist."""
        modulo_path = self.modulos_dir / nombre_modulo
        analisis = {
            'nombre': nombre_modulo,
            'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estructura': {},
            'carga_datos': {},
            'feedback_visual': {},
            'almacenamiento_bd': {},
            'tests': {},
            'edge_cases': {},
            'sugerencias': []
        }

        if not modulo_path.exists():
            analisis['error'] = f"Módulo {nombre_modulo} no encontrado"
            return analisis

        # Analizar estructura del módulo
        analisis['estructura'] = self._analizar_estructura(modulo_path)

        # Analizar carga de datos
        analisis['carga_datos'] = self._analizar_carga_datos(modulo_path)

        # Analizar feedback visual
        analisis['feedback_visual'] = self._analizar_feedback_visual(modulo_path)

        # Analizar almacenamiento en BD
        analisis['almacenamiento_bd'] = self._analizar_almacenamiento_bd(modulo_path)

        # Analizar tests
        analisis['tests'] = self._analizar_tests(nombre_modulo)

        # Analizar edge cases
        analisis['edge_cases'] = self._analizar_edge_cases(nombre_modulo)

        # Generar sugerencias
        analisis['sugerencias'] = self._generar_sugerencias(analisis)

        return analisis

    def _analizar_estructura(self, modulo_path: Path) -> Dict[str, Any]:
        """Analiza la estructura del módulo."""
        estructura = {
            'archivos_core': {},
            'archivos_adicionales': [],
            'lineas_totales': 0,
            'tamaño_total': 0
        }

        archivos_core = ['controller.py', 'model.py', 'view.py', '__init__.py']

        for archivo in archivos_core:
            archivo_path = modulo_path / archivo
            if archivo_path.exists():
                stats = archivo_path.stat()
                with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lineas = len(f.readlines())

                estructura['archivos_core'][archivo] = {
                    'existe': True,
                    'lineas': lineas,
                    'tamaño': stats.st_size
                }
                estructura['lineas_totales'] += lineas
                estructura['tamaño_total'] += stats.st_size
            else:
                estructura['archivos_core'][archivo] = {
                    'existe': False,
                    'lineas': 0,
                    'tamaño': 0
                }

        # Buscar archivos adicionales
        for archivo in modulo_path.rglob('*.py'):
            if archivo.name not in archivos_core:
                estructura['archivos_adicionales'].append(archivo.name)

        return estructura

    def _analizar_carga_datos(self, modulo_path: Path) -> Dict[str, Any]:
        """Analiza las operaciones de carga de datos del módulo."""
        carga = {
            'conexion_bd': {'detectada': False, 'detalles': []},
            'operaciones_crud': {'create': 0, 'read': 0, 'update': 0, 'delete': 0},
            'validaciones': {'detectadas': 0, 'tipos': []},
            'transacciones': {'detectadas': 0, 'rollback': False}
        }

        # Analizar archivos del módulo
        for archivo in modulo_path.rglob('*.py'):
            try:
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()

                # Detectar conexiones a BD
                if any(term in contenido.lower() for term in ['connect', 'database', 'cursor', 'execute']):
                    carga['conexion_bd']['detectada'] = True
                    carga['conexion_bd']['detalles'].append(f"Detectada en {archivo.name}")

                # Detectar operaciones CRUD
                if any(term in contenido.upper() for term in ['INSERT', 'CREATE']):
                    carga['operaciones_crud']['create'] += 1
                if any(term in contenido.upper() for term in ['SELECT', 'FETCH']):
                    carga['operaciones_crud']['read'] += 1
                if any(term in contenido.upper() for term in ['UPDATE', 'SET']):
                    carga['operaciones_crud']['update'] += 1
                if any(term in contenido.upper() for term in ['DELETE', 'DROP']):
                    carga['operaciones_crud']['delete'] += 1

                # Detectar validaciones
                for patron in self.patrones['validacion']:
                    matches = re.findall(patron, contenido, re.IGNORECASE)
                    if matches:
                        carga['validaciones']['detectadas'] += len(matches)
                        carga['validaciones']['tipos'].extend([f"Validación en {archivo.name}" for _ in matches])

                # Detectar transacciones
                for patron in self.patrones['transacciones']:
                    if re.search(patron, contenido, re.IGNORECASE):
                        carga['transacciones']['detectadas'] += 1
                        if 'rollback' in patron.lower():
                            carga['transacciones']['rollback'] = True

            except Exception as e:
                print(f"Error analizando {archivo}: {e}")

        return carga

    def _analizar_feedback_visual(self, modulo_path: Path) -> Dict[str, Any]:
        """Analiza el feedback visual del módulo."""
        feedback = {
            'indicadores_carga': {'count': 0, 'ejemplos': []},
            'mensajes_error': {'count': 0, 'ejemplos': []},
            'mensajes_exito': {'count': 0, 'ejemplos': []},
            'actualizaciones_ui': {'count': 0, 'ejemplos': []}
        }

        for archivo in modulo_path.rglob('*.py'):
            try:
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()

                # Analizar indicadores de carga
                for patron in self.patrones['feedback_loading']:
                    matches = re.findall(patron, contenido, re.IGNORECASE)
                    if matches:
                        feedback['indicadores_carga']['count'] += len(matches)
                        feedback['indicadores_carga']['ejemplos'].extend(matches[:3])  # Solo los primeros 3

                # Analizar mensajes de error
                for patron in self.patrones['feedback_error']:
                    matches = re.findall(patron, contenido, re.IGNORECASE)
                    if matches:
                        feedback['mensajes_error']['count'] += len(matches)
                        feedback['mensajes_error']['ejemplos'].extend(matches[:3])

                # Analizar mensajes de éxito
                for patron in self.patrones['feedback_success']:
                    matches = re.findall(patron, contenido, re.IGNORECASE)
                    if matches:
                        feedback['mensajes_exito']['count'] += len(matches)
                        feedback['mensajes_exito']['ejemplos'].extend(matches[:3])

                # Analizar actualizaciones de UI
                ui_patterns = [r'update.*', r'refresh.*', r'reload.*', r'setText.*', r'setModel.*']
                for patron in ui_patterns:
                    matches = re.findall(patron, contenido, re.IGNORECASE)
                    if matches:
                        feedback['actualizaciones_ui']['count'] += len(matches)
                        feedback['actualizaciones_ui']['ejemplos'].extend(matches[:5])

            except Exception as e:
                print(f"Error analizando feedback en {archivo}: {e}")

        return feedback

    def _analizar_almacenamiento_bd(self, modulo_path: Path) -> Dict[str, Any]:
        """Analiza las características de almacenamiento en BD."""
        almacenamiento = {
            'sql_seguro': {'detectado': False, 'count': 0},
            'optimizaciones': {'indices': 0, 'joins': 0, 'limit': 0},
            'seguridad': {'parametrizadas': 0, 'validacion_input': 0},
            'rendimiento': {'transacciones': 0, 'pool_conexiones': False}
        }

        for archivo in modulo_path.rglob('*.py'):
            try:
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()

                # Analizar SQL seguro
                for patron in self.patrones['sql_seguro']:
                    if re.search(patron, contenido, re.IGNORECASE):
                        almacenamiento['sql_seguro']['detectado'] = True
                        almacenamiento['sql_seguro']['count'] += 1

                # Analizar optimizaciones
                if re.search(r'CREATE.*INDEX', contenido, re.IGNORECASE):
                    almacenamiento['optimizaciones']['indices'] += 1
                if re.search(r'JOIN', contenido, re.IGNORECASE):
                    almacenamiento['optimizaciones']['joins'] += 1
                if re.search(r'LIMIT|TOP', contenido, re.IGNORECASE):
                    almacenamiento['optimizaciones']['limit'] += 1

                # Analizar seguridad
                if re.search(r'execute.*\?|executemany', contenido, re.IGNORECASE):
                    almacenamiento['seguridad']['parametrizadas'] += 1

                # Analizar rendimiento
                if re.search(r'pool|transaction', contenido, re.IGNORECASE):
                    almacenamiento['rendimiento']['transacciones'] += 1
                if re.search(r'connection.*pool', contenido, re.IGNORECASE):
                    almacenamiento['rendimiento']['pool_conexiones'] = True

            except Exception as e:
                print(f"Error analizando almacenamiento en {archivo}: {e}")

        return almacenamiento

    def _analizar_tests(self, nombre_modulo: str) -> Dict[str, Any]:
        """Analiza los tests del módulo."""
        tests = {
            'archivos_test': [],
            'cobertura_estimada': 0,
            'tipos_test': {'unitarios': 0, 'integracion': 0, 'edge_cases': 0},
            'metodos_probados': []
        }

        tests_modulo_dir = self.tests_dir / nombre_modulo
        if tests_modulo_dir.exists():
            for archivo_test in tests_modulo_dir.rglob('test_*.py'):
                tests['archivos_test'].append(archivo_test.name)

                try:
                    with open(archivo_test, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()

                    # Contar tipos de tests
                    if 'edge' in archivo_test.name.lower() or 'edge_case' in contenido.lower():
                        tests['tipos_test']['edge_cases'] += 1
                    elif 'integration' in archivo_test.name.lower() or 'integracion' in archivo_test.name.lower():
                        tests['tipos_test']['integracion'] += 1
                    else:
                        tests['tipos_test']['unitarios'] += 1

                    # Buscar métodos de test
                    test_methods = re.findall(r'def (test_\w+)', contenido)
                    tests['metodos_probados'].extend(test_methods)

                except Exception as e:
                    print(f"Error analizando test {archivo_test}: {e}")

        # Calcular cobertura estimada
        total_tests = len(tests['archivos_test'])
        if total_tests > 0:
            # Estimación basada en cantidad y tipos de tests
            base_coverage = min(total_tests * 15, 100)  # 15% por archivo de test, máximo 100%
            if tests['tipos_test']['edge_cases'] > 0:
                base_coverage = min(base_coverage + 20, 100)
            if tests['tipos_test']['integracion'] > 0:
                base_coverage = min(base_coverage + 15, 100)
            tests['cobertura_estimada'] = base_coverage

        return tests

    def _analizar_edge_cases(self, nombre_modulo: str) -> Dict[str, Any]:
        """Analiza los edge cases implementados y sugiere adicionales."""
        edge_cases = {
            'implementados': [],
            'sugeridos': [],
            'categorias_cubiertas': set(),
            'prioridad_implementacion': []
        }

        tests_modulo_dir = self.tests_dir / nombre_modulo
        if tests_modulo_dir.exists():
            # Buscar edge cases implementados
            for archivo_test in tests_modulo_dir.rglob('*edge*.py'):
                try:
                    with open(archivo_test, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()

                    # Extraer nombres de tests de edge cases
                    test_methods = re.findall(r'def (test_\w+)', contenido)
                    edge_cases['implementados'].extend(test_methods)

                    # Categorizar edge cases
                    if 'null' in contenido.lower() or 'vacio' in contenido.lower():
                        edge_cases['categorias_cubiertas'].add('datos_vacios')
                    if 'limite' in contenido.lower() or 'boundary' in contenido.lower():
                        edge_cases['categorias_cubiertas'].add('valores_limite')
                    if 'concurren' in contenido.lower():
                        edge_cases['categorias_cubiertas'].add('concurrencia')
                    if 'error' in contenido.lower() or 'exception' in contenido.lower():
                        edge_cases['categorias_cubiertas'].add('manejo_errores')

                except Exception as e:
                    print(f"Error analizando edge cases en {archivo_test}: {e}")

        # Sugerir edge cases adicionales basados en el módulo
        edge_cases_sugeridos = {
            'inventario': [
                'Stock negativo',
                'Cantidades muy grandes',
                'Códigos duplicados',
                'Productos sin categoría',
                'Movimientos sin fecha',
                'Reservas expiradas'
            ],
            'obras': [
                'Fechas de entrega pasadas',
                'Presupuestos negativos',
                'Estados inválidos',
                'Materiales sin asignar',
                'Múltiples modificaciones simultáneas'
            ],
            'usuarios': [
                'Contraseñas muy débiles',
                'Emails inválidos',
                'Permisos conflictivos',
                'Sesiones expiradas',
                'Múltiples logins simultáneos'
            ],
            'general': [
                'Conexión BD perdida',
                'Memoria insuficiente',
                'Timeout de operaciones',
                'Caracteres especiales en entrada',
                'JSON malformado'
            ]
        }

        # Agregar edge cases específicos del módulo y generales
        edge_cases['sugeridos'].extend(edge_cases_sugeridos.get(nombre_modulo, []))
        edge_cases['sugeridos'].extend(edge_cases_sugeridos['general'])

        # Priorizar por categorías no cubiertas
        categorias_importantes = ['datos_vacios', 'valores_limite', 'manejo_errores', 'concurrencia']
        for categoria in categorias_importantes:
            if categoria not in edge_cases['categorias_cubiertas']:
                edge_cases['prioridad_implementacion'].append(categoria)

        return edge_cases

    def _generar_sugerencias(self, analisis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera sugerencias de mejora basadas en el análisis."""
        sugerencias = []

        # Sugerencias basadas en estructura
        if not analisis['estructura']['archivos_core']['__init__.py']['existe']:
            sugerencias.append({
                'categoria': 'ESTRUCTURA',
                'prioridad': 'baja',
                'descripcion': 'Agregar archivo __init__.py para hacer el módulo importable'
            })

        # Sugerencias basadas en feedback visual
        if analisis['feedback_visual']['mensajes_error']['count'] == 0:
            sugerencias.append({
                'categoria': 'UX',
                'prioridad': 'media',
                'descripcion': 'Implementar mensajes de error para mejorar la experiencia de usuario'
            })

        if analisis['feedback_visual']['indicadores_carga']['count'] == 0:
            sugerencias.append({
                'categoria': 'UX',
                'prioridad': 'media',
                'descripcion': 'Agregar indicadores de carga para operaciones lentas'
            })

        # Sugerencias basadas en seguridad
        if not analisis['almacenamiento_bd']['sql_seguro']['detectado']:
            sugerencias.append({
                'categoria': 'SEGURIDAD',
                'prioridad': 'alta',
                'descripcion': 'Implementar consultas SQL parametrizadas para prevenir inyección SQL'
            })

        # Sugerencias basadas en tests
        if analisis['tests']['cobertura_estimada'] < 60:
            sugerencias.append({
                'categoria': 'CALIDAD',
                'prioridad': 'alta',
                'descripcion': 'Aumentar cobertura de tests - actualmente estimada en {}%'.format(analisis['tests']['cobertura_estimada'])
            })

        if analisis['tests']['tipos_test']['edge_cases'] == 0:
            sugerencias.append({
                'categoria': 'ROBUSTEZ',
                'prioridad': 'media',
                'descripcion': 'Agregar tests para edge cases identificados'
            })

        # Sugerencias basadas en rendimiento
        if analisis['almacenamiento_bd']['optimizaciones']['limit'] == 0:
            sugerencias.append({
                'categoria': 'RENDIMIENTO',
                'prioridad': 'media',
                'descripcion': 'Implementar paginación (LIMIT/TOP) para consultas de grandes datasets'
            })

        return sugerencias

    def generar_checklist_completo(self, nombre_modulo: str) -> str:
        """Genera un checklist completo y marcado para el módulo."""
        analisis = self.analizar_modulo(nombre_modulo)

        if 'error' in analisis:
            return f"Error: {analisis['error']}"

        # Plantilla de checklist con datos completados
        template = f"""# Checklist de Verificación - Módulo {nombre_modulo.title()}

**Información del Módulo**
- **Nombre del módulo:** {nombre_modulo}
- **Responsable:** [A completar manualmente]
- **Fecha de verificación:** {analisis['fecha_analisis']}
- **Versión analizada:** [A completar manualmente]

---

## 1. Verificación de Carga de Datos

### 1.1 Estructura de Datos
- [{'x' if analisis['estructura']['archivos_core']['model.py']['existe'] else ' '}] **Modelo de datos definido correctamente**
  - [{'x' if analisis['estructura']['archivos_core']['model.py']['existe'] else ' '}] Clases/tablas principales identificadas
  - [ ] Relaciones entre entidades documentadas *(Verificación manual requerida)*
  - [ ] Campos obligatorios y opcionales definidos *(Verificación manual requerida)*
  - [ ] Tipos de datos apropiados *(Verificación manual requerida)*
  - [ ] Restricciones de integridad implementadas *(Verificación manual requerida)*

- [{'x' if analisis['carga_datos']['conexion_bd']['detectada'] else ' '}] **Conexión a base de datos**
  - [{'x' if analisis['carga_datos']['conexion_bd']['detectada'] else ' '}] Conexión se establece correctamente
  - [{'x' if analisis['almacenamiento_bd']['rendimiento']['pool_conexiones'] else ' '}] Pool de conexiones configurado (si aplica)
  - [ ] Timeouts apropiados configurados *(Verificación manual requerida)*
  - [ ] Reconexión automática implementada *(Verificación manual requerida)*
  - [ ] Cierre adecuado de conexiones *(Verificación manual requerida)*

### 1.2 Operaciones CRUD
- [{'x' if analisis['carga_datos']['operaciones_crud']['create'] > 0 else ' '}] **Create (Crear)** - {analisis['carga_datos']['operaciones_crud']['create']} operaciones detectadas
  - [ ] Datos se insertan correctamente *(Verificación manual requerida)*
  - [{'x' if analisis['carga_datos']['validaciones']['detectadas'] > 0 else ' '}] Validaciones aplicadas antes de insertar
  - [ ] Manejo de IDs autogenerados *(Verificación manual requerida)*
  - [{'x' if analisis['carga_datos']['transacciones']['detectadas'] > 0 else ' '}] Transacciones implementadas apropiadamente
  - [{'x' if analisis['carga_datos']['transacciones']['rollback'] else ' '}] Rollback en caso de error

- [{'x' if analisis['carga_datos']['operaciones_crud']['read'] > 0 else ' '}] **Read (Leer)** - {analisis['carga_datos']['operaciones_crud']['read']} operaciones detectadas
  - [ ] Consultas SELECT funcionan correctamente *(Verificación manual requerida)*
  - [ ] Filtros y búsquedas implementados *(Verificación manual requerida)*
  - [{'x' if analisis['almacenamiento_bd']['optimizaciones']['limit'] > 0 else ' '}] Paginación funciona (si aplica)
  - [ ] Ordenamiento por columnas funciona *(Verificación manual requerida)*
  - [{'x' if analisis['almacenamiento_bd']['optimizaciones']['joins'] > 0 else ' '}] Joins y relaciones cargan correctamente

- [{'x' if analisis['carga_datos']['operaciones_crud']['update'] > 0 else ' '}] **Update (Actualizar)** - {analisis['carga_datos']['operaciones_crud']['update']} operaciones detectadas
  - [ ] Actualizaciones se aplican correctamente *(Verificación manual requerida)*
  - [ ] Solo se actualizan campos modificados *(Verificación manual requerida)*
  - [ ] Versionado/concurrencia manejada *(Verificación manual requerida)*
  - [ ] Auditoría de cambios implementada *(Verificación manual requerida)*
  - [{'x' if analisis['carga_datos']['validaciones']['detectadas'] > 0 else ' '}] Validaciones aplicadas antes de actualizar

- [{'x' if analisis['carga_datos']['operaciones_crud']['delete'] > 0 else ' '}] **Delete (Eliminar)** - {analisis['carga_datos']['operaciones_crud']['delete']} operaciones detectadas
  - [ ] Eliminaciones funcionan correctamente *(Verificación manual requerida)*
  - [ ] Soft delete implementado (si aplica) *(Verificación manual requerida)*
  - [ ] Eliminación en cascada configurada apropiadamente *(Verificación manual requerida)*
  - [ ] Verificación de dependencias antes de eliminar *(Verificación manual requerida)*
  - [ ] Auditoría de eliminaciones *(Verificación manual requerida)*

### 1.3 Validación de Datos
- [{'x' if analisis['carga_datos']['validaciones']['detectadas'] > 0 else ' '}] **Validación de entrada** - {analisis['carga_datos']['validaciones']['detectadas']} validaciones detectadas
  - [ ] Tipos de datos validados *(Verificación manual requerida)*
  - [ ] Rangos y límites verificados *(Verificación manual requerida)*
  - [ ] Formatos específicos validados (email, teléfono, etc.) *(Verificación manual requerida)*
  - [ ] Campos requeridos verificados *(Verificación manual requerida)*
  - [{'x' if analisis['almacenamiento_bd']['seguridad']['validacion_input'] > 0 else ' '}] Sanitización de datos implementada

---

## 2. Verificación de Feedback Visual

### 2.1 Indicadores de Estado
- [{'x' if analisis['feedback_visual']['indicadores_carga']['count'] > 0 else ' '}] **Indicadores de carga** - {analisis['feedback_visual']['indicadores_carga']['count']} implementaciones detectadas
  - [{'x' if any('spinner' in ej.lower() for ej in analisis['feedback_visual']['indicadores_carga']['ejemplos']) else ' '}] Spinner/loading mostrado durante operaciones lentas
  - [{'x' if any('cursor' in ej.lower() for ej in analisis['feedback_visual']['indicadores_carga']['ejemplos']) else ' '}] Cursor cambia a "wait" durante procesamientos
  - [{'x' if any('progress' in ej.lower() for ej in analisis['feedback_visual']['indicadores_carga']['ejemplos']) else ' '}] Barras de progreso para operaciones largas
  - [ ] Textos informativos durante esperas *(Verificación manual requerida)*
  - [{'x' if any('enabled' in ej.lower() for ej in analisis['feedback_visual']['indicadores_carga']['ejemplos']) else ' '}] Deshabilitación de controles durante procesamiento

- [{'x' if analisis['feedback_visual']['actualizaciones_ui']['count'] > 0 else ' '}] **Estados de la interfaz** - {analisis['feedback_visual']['actualizaciones_ui']['count']} actualizaciones detectadas
  - [ ] Botones reflejan el estado actual *(Verificación manual requerida)*
  - [ ] Campos se habilitan/deshabilitan apropiadamente *(Verificación manual requerida)*
  - [ ] Pestañas/secciones muestran estado correcto *(Verificación manual requerida)*
  - [ ] Contadores se actualizan en tiempo real *(Verificación manual requerida)*
  - [ ] Badges/etiquetas reflejan datos actuales *(Verificación manual requerida)*

### 2.2 Mensajes al Usuario
- [{'x' if analisis['feedback_visual']['mensajes_exito']['count'] > 0 else ' '}] **Mensajes de éxito** - {analisis['feedback_visual']['mensajes_exito']['count']} implementaciones detectadas
  - [ ] Confirmación de operaciones exitosas *(Verificación manual requerida)*
  - [ ] Detalles relevantes incluidos *(Verificación manual requerida)*
  - [ ] Duración apropiada de visualización *(Verificación manual requerida)*
  - [ ] Estilo consistente con la aplicación *(Verificación manual requerida)*
  - [ ] Posicionamiento apropiado en la UI *(Verificación manual requerida)*

- [{'x' if analisis['feedback_visual']['mensajes_error']['count'] > 0 else ' '}] **Mensajes de error** - {analisis['feedback_visual']['mensajes_error']['count']} implementaciones detectadas
  - [ ] Errores mostrados de forma clara *(Verificación manual requerida)*
  - [ ] Mensajes específicos y útiles *(Verificación manual requerida)*
  - [ ] Sugerencias de corrección incluidas *(Verificación manual requerida)*
  - [ ] No se expone información sensible *(Verificación manual requerida)*
  - [ ] Logging de errores implementado *(Verificación manual requerida)*

---

## 3. Verificación de Almacenamiento en BD

### 3.1 Integridad de Datos
- [ ] **Consistencia** *(Verificación manual requerida)*
  - [ ] Datos se almacenan en formato correcto
  - [ ] Codificación de caracteres apropiada (UTF-8)
  - [ ] Decimales con precisión correcta
  - [ ] Fechas en formato estándar
  - [ ] Referencias foráneas válidas

- [{'x' if analisis['carga_datos']['transacciones']['detectadas'] > 0 else ' '}] **Transacciones** - {analisis['carga_datos']['transacciones']['detectadas']} detectadas
  - [{'x' if analisis['carga_datos']['transacciones']['detectadas'] > 0 else ' '}] Operaciones complejas usan transacciones
  - [{'x' if analisis['carga_datos']['transacciones']['rollback'] else ' '}] Rollback funciona correctamente en errores
  - [ ] Aislamiento apropiado configurado *(Verificación manual requerida)*
  - [ ] Deadlocks manejados apropiadamente *(Verificación manual requerida)*
  - [ ] Timeouts de transacción configurados *(Verificación manual requerida)*

### 3.2 Rendimiento
- [{'x' if sum(analisis['almacenamiento_bd']['optimizaciones'].values()) > 0 else ' '}] **Consultas optimizadas**
  - [{'x' if analisis['almacenamiento_bd']['optimizaciones']['indices'] > 0 else ' '}] Índices apropiados definidos
  - [ ] Consultas N+1 evitadas *(Verificación manual requerida)*
  - [{'x' if analisis['almacenamiento_bd']['optimizaciones']['joins'] > 0 else ' '}] JOINs optimizados
  - [{'x' if analisis['almacenamiento_bd']['optimizaciones']['limit'] > 0 else ' '}] LIMIT/TOP usados para grandes datasets
  - [ ] Consultas lentas identificadas y optimizadas *(Verificación manual requerida)*

### 3.3 Seguridad
- [{'x' if analisis['almacenamiento_bd']['sql_seguro']['detectado'] else ' '}] **Prevención de inyección SQL** - {analisis['almacenamiento_bd']['sql_seguro']['count']} implementaciones seguras detectadas
  - [{'x' if analisis['almacenamiento_bd']['seguridad']['parametrizadas'] > 0 else ' '}] Consultas parametrizadas usadas
  - [{'x' if analisis['almacenamiento_bd']['seguridad']['validacion_input'] > 0 else ' '}] Input sanitizado antes de uso
  - [ ] Validación de nombres de tabla/columna *(Verificación manual requerida)*
  - [ ] Escapado apropiado de caracteres especiales *(Verificación manual requerida)*
  - [{'x' if analisis['almacenamiento_bd']['sql_seguro']['detectado'] else ' '}] No concatenación directa de SQL

---

## 4. Verificación de Tests

### 4.1 Cobertura de Tests
- [{'x' if analisis['tests']['tipos_test']['unitarios'] > 0 else ' '}] **Tests unitarios** - {analisis['tests']['tipos_test']['unitarios']} archivos detectados
  - [ ] Métodos principales probados *(Verificación manual requerida)*
  - [{'x' if analisis['carga_datos']['validaciones']['detectadas'] > 0 else ' '}] Validaciones probadas
  - [{'x' if analisis['feedback_visual']['mensajes_error']['count'] > 0 else ' '}] Manejo de errores probado
  - [{'x' if analisis['tests']['tipos_test']['edge_cases'] > 0 else ' '}] Edge cases cubiertos
  - [ ] Mocks usados apropiadamente *(Verificación manual requerida)*

- [{'x' if analisis['tests']['tipos_test']['integracion'] > 0 else ' '}] **Tests de integración** - {analisis['tests']['tipos_test']['integracion']} archivos detectados
  - [ ] Operaciones de BD probadas *(Verificación manual requerida)*
  - [ ] Flujos completos probados *(Verificación manual requerida)*
  - [ ] Interacción entre módulos probada *(Verificación manual requerida)*
  - [ ] APIs externas mockeadas *(Verificación manual requerida)*
  - [ ] Configuraciones diferentes probadas *(Verificación manual requerida)*

### 4.2 Edge Cases Identificados
**Edge Cases Implementados:** {len(analisis['edge_cases']['implementados'])}
{chr(10).join('- ' + case for case in analisis['edge_cases']['implementados'][:10])}

**Edge Cases Sugeridos para Implementar:**
{chr(10).join('- [ ] ' + case for case in analisis['edge_cases']['sugeridos'][:15])}

### 4.3 Categorías de Edge Cases Cubiertas
{chr(10).join('- [x] ' + cat.replace('_', ' ').title() for cat in analisis['edge_cases']['categorias_cubiertas'])}

**Categorías Pendientes (Alta Prioridad):**
{chr(10).join('- [ ] ' + cat.replace('_', ' ').title() for cat in analisis['edge_cases']['prioridad_implementacion'])}

---

## 5. Sugerencias y Mejoras Identificadas

### 5.1 Sugerencias Automáticas
{chr(10).join(f"**{sug['categoria']}** - Prioridad: {sug['prioridad']}" + chr(10) + sug['descripcion'] + chr(10) for sug in analisis['sugerencias'])}

### 5.2 Mejoras Identificadas Manualmente
- [ ] **Mejoras de Rendimiento:**
  - [ ] _________________________________
  - [ ] _________________________________

- [ ] **Mejoras de UX:**
  - [ ] _________________________________
  - [ ] _________________________________

- [ ] **Mejoras de Seguridad:**
  - [ ] _________________________________
  - [ ] _________________________________

---

## 6. Resumen de Verificación

### Estadísticas Automáticas
- **Archivos core detectados:** {sum(1 for arch in analisis['estructura']['archivos_core'].values() if arch['existe'])}/4
- **Tests implementados:** {len(analisis['tests']['archivos_test'])}
- **Cobertura estimada:** {analisis['tests']['cobertura_estimada']}%
- **Feedback visual detectado:** {analisis['feedback_visual']['indicadores_carga']['count'] + analisis['feedback_visual']['mensajes_error']['count'] + analisis['feedback_visual']['mensajes_exito']['count']} implementaciones
- **SQL seguro detectado:** {'Sí' if analisis['almacenamiento_bd']['sql_seguro']['detectado'] else 'No'}
- **Sugerencias generadas:** {len(analisis['sugerencias'])}

### Estado General (Estimación Automática)
- [{'x' if analisis['tests']['cobertura_estimada'] >= 80 and analisis['almacenamiento_bd']['sql_seguro']['detectado'] and len(analisis['sugerencias']) <= 2 else ' '}] ✅ Módulo cumple todos los estándares
- [{'x' if 60 <= analisis['tests']['cobertura_estimada'] < 80 or (not analisis['almacenamiento_bd']['sql_seguro']['detectado']) or 3 <= len(analisis['sugerencias']) <= 5 else ' '}] ⚠️ Módulo necesita mejoras menores
- [{'x' if analisis['tests']['cobertura_estimada'] < 60 or len(analisis['sugerencias']) > 5 else ' '}] ❌ Módulo necesita mejoras críticas

### Próximos Pasos Sugeridos
1. **Completar verificación manual** de los elementos marcados como "Verificación manual requerida"
2. **Implementar sugerencias de alta prioridad** listadas arriba
3. **Añadir edge cases faltantes** especialmente en categorías no cubiertas
4. **Revisar y mejorar feedback visual** si la puntuación es baja
5. **Implementar medidas de seguridad** si no se detectó SQL seguro

### Notas Adicionales
- Este checklist fue generado automáticamente el {analisis['fecha_analisis']}
- Los elementos marcados con *(Verificación manual requerida)* necesitan revisión humana
- Las estimaciones son basadas en análisis estático del código
- Se recomienda completar la verificación manual para obtener una evaluación completa

---

**Verificador:** _________________ **Fecha:** _________ **Firma:** _________

"""

        return template

    def procesar_todos_los_modulos(self):
        """Procesa todos los módulos y genera sus checklists."""
        if not self.modulos_dir.exists():
            print(f"Error: Directorio de módulos no encontrado: {self.modulos_dir}")
            return

        modulos_procesados = []
        for modulo_dir in self.modulos_dir.iterdir():
            if modulo_dir.is_dir() and not modulo_dir.name.startswith('.'):
                nombre_modulo = modulo_dir.name
                print(f"Procesando módulo: {nombre_modulo}")

                try:
                    checklist = self.generar_checklist_completo(nombre_modulo)
                    archivo_checklist = self.checklists_dir / f"checklist_completo_{nombre_modulo}.md"

                    with open(archivo_checklist, 'w', encoding='utf-8') as f:
                        f.write(checklist)

                    modulos_procesados.append({
                        'nombre': nombre_modulo,
                        'archivo': archivo_checklist,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    print(f"✅ Checklist generado: {archivo_checklist}")

                except Exception as e:
                    print(f"❌ Error procesando {nombre_modulo}: {e}")

        # Generar índice de checklists
        self._generar_indice_checklists(modulos_procesados)

        print(f"\n✅ Procesamiento completo. {len(modulos_procesados)} checklists generados.")
        print(f"📁 Checklists guardados en: {self.checklists_dir}")

    def _generar_indice_checklists(self, modulos_procesados: List[Dict[str, Any]]):
        """Genera un índice de todos los checklists creados."""
        indice_content = f"""# Índice de Checklists Completados

Checklists de verificación generados automáticamente para todos los módulos del proyecto.

**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total de módulos:** {len(modulos_procesados)}

---

## Checklists por Módulo

| Módulo | Archivo | Fecha de Generación | Estado |
|--------|---------|-------------------|---------|
"""

        for modulo in sorted(modulos_procesados, key=lambda x: x['nombre']):
            indice_content += f"| {modulo['nombre'].title()} | [checklist_completo_{modulo['nombre']}.md](checklist_completo_{modulo['nombre']}.md) | {modulo['timestamp']} | 🔄 Pendiente revisión |\n"

        indice_content += f"""
---

## Instrucciones de Uso

1. **Revisar cada checklist individual** - Los checklists contienen verificaciones automáticas y elementos que requieren revisión manual
2. **Completar elementos marcados como "Verificación manual requerida"** - Estos elementos no pueden verificarse automáticamente
3. **Implementar sugerencias de alta prioridad** - Las sugerencias están categorizadas por prioridad
4. **Actualizar estado en este índice** - Marcar como completado cuando se termine la verificación

## Leyenda de Estados

- 🔄 **Pendiente revisión** - Checklist generado, falta revisión manual
- ⚠️ **En progreso** - Revisión iniciada, pendiente completar
- ✅ **Completado** - Verificación completa terminada
- ❌ **Requiere mejoras** - Verificación completa, identificadas mejoras críticas

## Notas Importantes

- Los checklists se generan automáticamente basándose en análisis estático del código
- Las estimaciones de cobertura y calidad son aproximadas
- Se requiere verificación manual para una evaluación completa
- Los elementos de seguridad SQL son especialmente importantes de verificar

## Enlaces Relacionados

- [Checklist de Implementación de Seguridad](../checklist_implementacion_seguridad.md)
- [Checklist de Uso de SQL Seguro](../checklist_uso_sql_seguro.md)
- [Checklist de Validación de Datos](../checklist_validacion_datos.md)
- [Checklist de Verificación de Módulo (Plantilla)](../checklist_verificacion_modulo.md)

---

**Última actualización:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        archivo_indice = self.checklists_dir / "00_indice_checklists_completados.md"
        with open(archivo_indice, 'w', encoding='utf-8') as f:
            f.write(indice_content)

        print(f"📋 Índice de checklists generado: {archivo_indice}")

def main():
    """Función principal del script."""
    # Obtener la ruta del proyecto (asumiendo que el script está en scripts/verificacion/)
    script_dir = Path(__file__).parent
    proyecto_root = script_dir.parent.parent

    print("🔍 Generador de Checklists Completados por Módulo")
    print(f"📁 Proyecto: {proyecto_root}")
    print("=" * 50)

    generador = GeneradorChecklist(str(proyecto_root))
    generador.procesar_todos_los_modulos()

    print("\n" + "=" * 50)
    print("✅ Generación de checklists completada")
    print(f"📁 Ver resultados en: {generador.checklists_dir}")
    print("🔄 Próximos pasos:")
    print("   1. Revisar cada checklist individual")
    print("   2. Completar verificaciones manuales")
    print("   3. Implementar sugerencias de alta prioridad")
    print("   4. Actualizar estados en el índice")

if __name__ == "__main__":
    main()
