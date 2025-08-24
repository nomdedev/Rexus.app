#!/usr/bin/env python3
"""
Script para corregir completamente el controller de administración
"""

def fix_administracion_controller():
    """Corrige todos los problemas del controller de administración"""
    
    content = '''"""
Controlador de Administración

Controlador principal para el módulo de administración
Integra los submódulos de contabilidad y recursos humanos
Maneja la comunicación entre modelos y vistas
Integrado con el sistema de seguridad global
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSlot, pyqtSignal

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger()
except ImportError:
    import logging
    
    class DummyLogger:
        """Logger dummy para cuando no está disponible el logger principal."""
        
        def info(self, msg): 
            print(f"[INFO] {msg}")
            
        def warning(self, msg): 
            print(f"[WARNING] {msg}")
            
        def error(self, msg): 
            print(f"[ERROR] {msg}")
            
        def debug(self, msg): 
            print(f"[DEBUG] {msg}")
    
    logger = DummyLogger()

# Importar sistema de seguridad
try:
    from rexus.core.security import get_security_manager
except ImportError:
    logger.warning("Sistema de seguridad no disponible")
    get_security_manager = lambda: None

# Importar submódulos
try:
    from .contabilidad import ContabilidadModel, ContabilidadController
except ImportError:
    logger.warning("Submódulo contabilidad no disponible")
    ContabilidadModel = None
    ContabilidadController = None

try:
    from .recursos_humanos import RecursosHumanosModel, RecursosHumanosController
except ImportError:
    logger.warning("Submódulo recursos humanos no disponible")
    RecursosHumanosModel = None
    RecursosHumanosController = None

# Constantes para mensajes
MENSAJE_MODELO_NO_DISPONIBLE = "Modelo no disponible"
MENSAJE_EXITO = "Éxito"
MENSAJE_ERROR = "Error"


class AdministracionController(QObject):
    """Controlador principal del módulo de administración."""
    
    # Señales
    estadisticas_actualizadas = pyqtSignal(dict)
    reporte_generado = pyqtSignal(str, dict)
    datos_actualizados = pyqtSignal()
    
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        """
        Inicializa el controlador de administración.
        
        Args:
            model: Modelo de administración
            view: Vista de administración
            db_connection: Conexión a base de datos
            usuarios_model: Modelo de usuarios
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        
        # Inicializar sistema de seguridad
        self.security_manager = get_security_manager()
        
        # Obtener usuario y rol actual del sistema de seguridad
        try:
            if self.security_manager:
                self.usuario_actual = getattr(self.security_manager, 'get_current_user', lambda: "SISTEMA")()
                self.rol_actual = getattr(self.security_manager, 'get_current_role', lambda: "ADMIN")()
            else:
                self.usuario_actual = "SISTEMA"
                self.rol_actual = "ADMIN"
        except Exception as e:
            logger.warning(f"Error obteniendo usuario actual: {e}")
            self.usuario_actual = "SISTEMA"
            self.rol_actual = "ADMIN"
        
        # Configurar el modelo con la conexión
        if self.model and self.db_connection:
            self.model.db_connection = self.db_connection
            self.model.usuario_actual = self.usuario_actual
        
        # Inicializar submódulos
        self.contabilidad_model = None
        self.contabilidad_controller = None
        self.recursos_humanos_model = None
        self.recursos_humanos_controller = None
        
        # Timer para actualización automática
        self.timer = None
        
        # Inicializar componentes
        self.inicializar_submodulos()
        self.conectar_senales()
        self.cargar_datos_iniciales()
        
        logger.info("AdministracionController inicializado correctamente")
    
    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if not self.view:
                logger.warning("No hay vista disponible para conectar señales")
                return
            
            # Conectar señales principales
            if hasattr(self.view, 'crear_departamento_signal'):
                self.view.crear_departamento_signal.connect(self.crear_departamento)
            
            if hasattr(self.view, 'crear_empleado_signal'):
                self.view.crear_empleado_signal.connect(self.crear_empleado)
            
            if hasattr(self.view, 'crear_asiento_signal'):
                self.view.crear_asiento_signal.connect(self.crear_asiento_contable)
            
            if hasattr(self.view, 'crear_recibo_signal'):
                self.view.crear_recibo_signal.connect(self.crear_recibo)
            
            if hasattr(self.view, 'imprimir_recibo_signal'):
                self.view.imprimir_recibo_signal.connect(self.imprimir_recibo)
            
            if hasattr(self.view, 'generar_reporte_signal'):
                self.view.generar_reporte_signal.connect(self.generar_reporte)
            
            if hasattr(self.view, 'actualizar_datos_signal'):
                self.view.actualizar_datos_signal.connect(self.actualizar_datos)
            
            # Configurar timer para actualización automática
            self.timer = QTimer()
            self.timer.timeout.connect(self.actualizar_datos)
            self.timer.start(30000)  # Actualizar cada 30 segundos
            
            logger.debug("Señales de administración conectadas")
            
        except Exception as e:
            logger.error(f"Error conectando señales: {e}")
    
    def inicializar_submodulos(self):
        """Inicializa los submódulos de contabilidad y recursos humanos."""
        try:
            self._inicializar_contabilidad()
            self._inicializar_recursos_humanos()
            self.conectar_senales_submodulos()
            logger.info("[ADMINISTRACIÓN] Submódulos inicializados correctamente")
            
        except ImportError as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error importando submódulos: {e}")
        except AttributeError as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error configurando submódulos: {e}")
        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error inesperado inicializando submódulos: {e}")
    
    def _inicializar_contabilidad(self):
        """Inicializa el submódulo de contabilidad."""
        try:
            if ContabilidadModel and ContabilidadController:
                self.contabilidad_model = ContabilidadModel(self.db_connection)
                self.contabilidad_controller = ContabilidadController(
                    model=self.contabilidad_model,
                    view=self.view,
                    db_connection=self.db_connection
                )
                logger.debug("Submódulo de contabilidad inicializado")
            else:
                logger.warning("Clases de contabilidad no disponibles")
                
        except Exception as e:
            logger.error(f"Error inicializando contabilidad: {e}")
    
    def _inicializar_recursos_humanos(self):
        """Inicializa el submódulo de recursos humanos."""
        try:
            if RecursosHumanosModel and RecursosHumanosController:
                self.recursos_humanos_model = RecursosHumanosModel(self.db_connection)
                self.recursos_humanos_controller = RecursosHumanosController(
                    model=self.recursos_humanos_model,
                    view=self.view,
                    db_connection=self.db_connection
                )
                logger.debug("Submódulo de recursos humanos inicializado")
            else:
                logger.warning("Clases de recursos humanos no disponibles")
                
        except Exception as e:
            logger.error(f"Error inicializando recursos humanos: {e}")
    
    def conectar_senales_submodulos(self):
        """Conecta las señales entre los submódulos."""
        try:
            # Conectar señales del submódulo de contabilidad
            if self.contabilidad_controller and hasattr(self.contabilidad_controller, 'estadisticas_actualizadas'):
                self.contabilidad_controller.estadisticas_actualizadas.connect(
                    self.actualizar_estadisticas_generales
                )
            
            if self.contabilidad_controller and hasattr(self.contabilidad_controller, 'reporte_generado'):
                self.contabilidad_controller.reporte_generado.connect(
                    self.manejar_reporte_generado
                )
            
            # Conectar señales del submódulo de recursos humanos
            if self.recursos_humanos_controller and hasattr(self.recursos_humanos_controller, 'nomina_calculada'):
                self.recursos_humanos_controller.nomina_calculada.connect(
                    self.manejar_nomina_calculada
                )
            
            if self.recursos_humanos_controller and hasattr(self.recursos_humanos_controller, 'empleado_agregado'):
                self.recursos_humanos_controller.empleado_agregado.connect(
                    self.manejar_empleado_agregado
                )
            
            logger.debug("Señales de submódulos conectadas")
            
        except Exception as e:
            logger.error(f"Error conectando señales de submódulos: {e}")
    
    # MÉTODOS DE MANEJO DE EVENTOS
    
    def actualizar_estadisticas_generales(self, estadisticas):
        """Actualiza las estadísticas generales del módulo."""
        try:
            if self.view and hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
            
            # Emitir señal de estadísticas actualizadas
            self.estadisticas_actualizadas.emit(estadisticas)
            logger.debug("Estadísticas generales actualizadas")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas generales: {e}")
    
    def manejar_reporte_generado(self, tipo_reporte, datos_reporte):
        """Maneja cuando se genera un reporte."""
        try:
            logger.info(f"Reporte generado: {tipo_reporte}")
            
            # Emitir señal de reporte generado
            self.reporte_generado.emit(tipo_reporte, datos_reporte)
            
            if self.view and hasattr(self.view, 'mostrar_reporte'):
                self.view.mostrar_reporte(tipo_reporte, datos_reporte)
                
        except Exception as e:
            logger.error(f"Error manejando reporte generado: {e}")
    
    def manejar_nomina_calculada(self, datos_nomina):
        """Maneja cuando se calcula una nómina."""
        try:
            logger.info("Nómina calculada exitosamente")
            
            if self.view and hasattr(self.view, 'actualizar_nomina'):
                self.view.actualizar_nomina(datos_nomina)
            
            self.actualizar_datos()
            
        except Exception as e:
            logger.error(f"Error manejando nómina calculada: {e}")
    
    def manejar_empleado_agregado(self, datos_empleado):
        """Maneja cuando se agrega un empleado."""
        try:
            logger.info(f"Empleado agregado: {datos_empleado.get('nombre', 'Sin nombre')}")
            self.actualizar_datos()
            
        except Exception as e:
            logger.error(f"Error manejando empleado agregado: {e}")
    
    # MÉTODOS DE CARGA DE DATOS
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo."""
        try:
            logger.debug("Cargando datos iniciales de administración")
            self.actualizar_datos()
            
        except Exception as e:
            logger.debug(f"Error cargando datos iniciales: {e}")
    
    def actualizar_datos(self):
        """Actualiza todos los datos del módulo."""
        try:
            if not self.view:
                logger.warning("No hay vista disponible para actualizar datos")
                return
            
            # Actualizar dashboard principal
            self.actualizar_dashboard()
            
            # Actualizar libro contable
            self.actualizar_libro_contable()
            
            # Actualizar datos de recursos humanos
            self.actualizar_recursos_humanos()
            
            # Emitir señal de datos actualizados
            self.datos_actualizados.emit()
            
            logger.debug("Datos de administración actualizados")
            
        except Exception as e:
            logger.debug(f"Error actualizando datos: {e}")
    
    def actualizar_dashboard(self):
        """Actualiza el dashboard principal."""
        try:
            if not self.view or not self.model:
                return
            
            # Obtener resumen contable
            if hasattr(self.model, 'obtener_resumen_contable'):
                resumen = self.model.obtener_resumen_contable()
                
                if resumen and hasattr(self.view, 'actualizar_dashboard'):
                    self.view.actualizar_dashboard({"resumen": resumen})
            
        except Exception as e:
            logger.debug(f"Error actualizando dashboard: {e}")
    
    def actualizar_libro_contable(self):
        """Actualiza los datos del libro contable."""
        try:
            if not self.view or not self.model:
                return
            
            if hasattr(self.model, 'obtener_libro_contable'):
                asientos = self.model.obtener_libro_contable()
                
                if asientos and hasattr(self.view, 'actualizar_libro_contable'):
                    self.view.actualizar_libro_contable(asientos)
            
        except Exception as e:
            logger.debug(f"Error actualizando libro contable: {e}")
    
    def actualizar_recursos_humanos(self):
        """Actualiza los datos de recursos humanos."""
        try:
            if not self.view:
                return
            
            # Actualizar empleados
            if self.recursos_humanos_controller and hasattr(self.recursos_humanos_controller, 'obtener_empleados'):
                empleados = self.recursos_humanos_controller.obtener_empleados()
                
                if empleados and hasattr(self.view, 'actualizar_empleados'):
                    self.view.actualizar_empleados(empleados)
            
            # Actualizar departamentos
            if self.model and hasattr(self.model, 'obtener_departamentos'):
                departamentos = self.model.obtener_departamentos()
                
                if departamentos and hasattr(self.view, 'actualizar_departamentos'):
                    self.view.actualizar_departamentos(departamentos)
            
        except Exception as e:
            logger.debug(f"Error actualizando recursos humanos: {e}")
    
    # MÉTODOS DE OPERACIONES PRINCIPALES
    
    @pyqtSlot(dict)
    def crear_departamento(self, datos_departamento):
        """Crea un nuevo departamento."""
        try:
            if not self.model:
                logger.error(MENSAJE_MODELO_NO_DISPONIBLE)
                return False
            
            if hasattr(self.model, 'crear_departamento'):
                resultado = self.model.crear_departamento(
                    datos_departamento.get('codigo', ''),
                    datos_departamento.get('nombre', ''),
                    datos_departamento.get('descripcion', ''),
                    datos_departamento.get('responsable_id'),
                    datos_departamento.get('presupuesto', 0)
                )
                
                if resultado:
                    logger.info(f"Departamento creado: {datos_departamento.get('nombre')}")
                    self.actualizar_datos()
                    return True
                else:
                    logger.error("Error creando departamento")
                    return False
            else:
                logger.error("Método crear_departamento no disponible en modelo")
                return False
                
        except Exception as e:
            logger.error(f"Error creando departamento: {e}")
            return False
    
    @pyqtSlot(dict)
    def crear_empleado(self, datos_empleado):
        """Crea un nuevo empleado."""
        try:
            if self.recursos_humanos_controller:
                return self.recursos_humanos_controller.crear_empleado(datos_empleado)
            else:
                logger.error("Controller de recursos humanos no disponible")
                return False
                
        except Exception as e:
            logger.error(f"Error creando empleado: {e}")
            return False
    
    @pyqtSlot(dict)
    def crear_asiento_contable(self, datos_asiento):
        """Crea un nuevo asiento contable."""
        try:
            if not self.model:
                logger.error(MENSAJE_MODELO_NO_DISPONIBLE)
                return False
            
            if hasattr(self.model, 'crear_asiento_contable'):
                resultado = self.model.crear_asiento_contable(
                    datos_asiento.get('fecha_asiento'),
                    datos_asiento.get('tipo_asiento', 'GENERAL'),
                    datos_asiento.get('concepto', ''),
                    datos_asiento.get('referencia', ''),
                    datos_asiento.get('obra_id'),
                    datos_asiento.get('proveedor_id'),
                    datos_asiento.get('empleado_id'),
                    datos_asiento.get('departamento_id'),
                    datos_asiento.get('cuenta_contable', ''),
                    datos_asiento.get('debe', 0),
                    datos_asiento.get('haber', 0),
                    datos_asiento.get('observaciones', '')
                )
                
                if resultado:
                    logger.info("Asiento contable creado exitosamente")
                    self.actualizar_datos()
                    return True
                else:
                    logger.error("Error creando asiento contable")
                    return False
            else:
                logger.error("Método crear_asiento_contable no disponible en modelo")
                return False
                
        except Exception as e:
            logger.error(f"Error creando asiento contable: {e}")
            return False
    
    @pyqtSlot(dict)
    def crear_recibo(self, datos_recibo):
        """Crea un nuevo recibo."""
        try:
            if not self.model:
                logger.error(MENSAJE_MODELO_NO_DISPONIBLE)
                return False
            
            if hasattr(self.model, 'crear_recibo'):
                resultado = self.model.crear_recibo(
                    datos_recibo.get('fecha_emision'),
                    datos_recibo.get('empleado_emisor', ''),
                    datos_recibo.get('descripcion', ''),
                    datos_recibo.get('monto', 0),
                    datos_recibo.get('destinatario', ''),
                    datos_recibo.get('concepto', '')
                )
                
                if resultado:
                    logger.info("Recibo creado exitosamente")
                    self.actualizar_datos()
                    return True
                else:
                    logger.error("Error creando recibo")
                    return False
            else:
                logger.error("Método crear_recibo no disponible en modelo")
                return False
                
        except Exception as e:
            logger.error(f"Error creando recibo: {e}")
            return False
    
    @pyqtSlot(str)
    def imprimir_recibo(self, numero_recibo):
        """Marca un recibo como impreso."""
        try:
            if not self.model:
                logger.error(MENSAJE_MODELO_NO_DISPONIBLE)
                return False
            
            if hasattr(self.model, 'marcar_recibo_impreso'):
                resultado = self.model.marcar_recibo_impreso(numero_recibo)
                
                if resultado:
                    logger.info(f"Recibo {numero_recibo} marcado como impreso")
                    self.actualizar_datos()
                    return True
                else:
                    logger.error(f"Error marcando recibo {numero_recibo} como impreso")
                    return False
            else:
                logger.error("Método marcar_recibo_impreso no disponible en modelo")
                return False
                
        except Exception as e:
            logger.error(f"Error imprimiendo recibo: {e}")
            return False
    
    @pyqtSlot(str, dict)
    def generar_reporte(self, tipo_reporte, parametros):
        """Genera un reporte específico."""
        try:
            if self.contabilidad_controller:
                return self.contabilidad_controller.generar_reporte(tipo_reporte, parametros)
            else:
                logger.error("Controller de contabilidad no disponible para generar reporte")
                return False
                
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return False
    
    # MÉTODOS PÚBLICOS
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del módulo."""
        try:
            estadisticas = {}
            
            # Estadísticas de contabilidad
            if self.contabilidad_controller and hasattr(self.contabilidad_controller, 'obtener_estadisticas'):
                estadisticas['contabilidad'] = self.contabilidad_controller.obtener_estadisticas()
            
            # Estadísticas de recursos humanos
            if self.recursos_humanos_controller and hasattr(self.recursos_humanos_controller, 'obtener_estadisticas'):
                estadisticas['recursos_humanos'] = self.recursos_humanos_controller.obtener_estadisticas()
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas generales: {e}")
            return {}
    
    def obtener_resumen_financiero(self) -> Dict[str, Any]:
        """Obtiene un resumen financiero completo."""
        try:
            if not self.model:
                return {}
            
            if hasattr(self.model, 'obtener_resumen_contable'):
                return self.model.obtener_resumen_contable()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error obteniendo resumen financiero: {e}")
            return {}
    
    def cleanup(self):
        """Limpia recursos del controller."""
        try:
            # Detener timer
            if self.timer:
                self.timer.stop()
                self.timer = None
            
            # Limpiar submódulos
            if self.contabilidad_controller and hasattr(self.contabilidad_controller, 'cleanup'):
                self.contabilidad_controller.cleanup()
            
            if self.recursos_humanos_controller and hasattr(self.recursos_humanos_controller, 'cleanup'):
                self.recursos_humanos_controller.cleanup()
            
            logger.info("AdministracionController limpiado correctamente")
            
        except Exception as e:
            logger.error(f"Error en cleanup de AdministracionController: {e}")
'''
    
    # Crear backup del archivo original
    import shutil
    import datetime
    
    backup_name = f"rexus/modules/administracion/controller.py.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('rexus/modules/administracion/controller.py', backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir archivo corregido
    with open('rexus/modules/administracion/controller.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Controller de administración completamente reescrito y corregido")

if __name__ == '__main__':
    fix_administracion_controller()
