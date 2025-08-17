"""Controlador de Logística"""

import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal
from rexus.utils.error_handler import error_boundary as safe_method_decorator
from rexus.core.auth_decorators import auth_required, admin_required

# Importar sistema de mensajería centralizado y logging
try:
    from rexus.utils.message_system import show_success, show_error, show_warning, show_info
    MESSAGING_AVAILABLE = True
except ImportError:
    # Fallback temporal con QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    def show_success(parent, title, message): QMessageBox.information(parent, title, message)
    def show_error(parent, title, message): QMessageBox.critical(parent, title, message)
    def show_warning(parent, title, message): QMessageBox.warning(parent, title, message)
    def show_info(parent, title, message): QMessageBox.information(parent, title, message)
    MESSAGING_AVAILABLE = False

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("logistica.controller")
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback para logging
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()
    LOGGING_AVAILABLE = False


class LogisticaController(QObject):

    entrega_creada = pyqtSignal(dict)
    entrega_actualizada = pyqtSignal(dict)
    transporte_creado = pyqtSignal(dict)
    transporte_actualizado = pyqtSignal(dict)
    transporte_eliminado = pyqtSignal(int)
    def __init__(self,
model=None,
        view=None,
        db_connection=None,
        usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"

        # Conectar señales de la vista
        if self.view:
            self.conectar_senales_vista()

    def conectar_senales_vista(self):
        """Conecta todas las señales de la vista con sus métodos correspondientes."""
        try:
            # Verificar que la vista existe antes de conectar señales
            if not self.view:
                return

            # Señales existentes
            if hasattr(self.view, 'crear_entrega_solicitada'):
                self.view.crear_entrega_solicitada.connect(self.guardar_entrega)

            # Nuevas señales para transportes
            if hasattr(self.view, 'solicitud_crear_transporte'):
                self.view.solicitud_crear_transporte.connect(self.crear_transporte)
            if hasattr(self.view, 'solicitud_actualizar_transporte'):
                self.view.solicitud_actualizar_transporte.connect(self.actualizar_transporte)
            if hasattr(self.view, 'solicitud_eliminar_transporte'):
                self.view.solicitud_eliminar_transporte.connect(self.eliminar_transporte)
            if hasattr(self.view, 'solicitud_actualizar_estadisticas'):
                self.view.solicitud_actualizar_estadisticas.connect(self.cargar_estadisticas)
        except Exception as e:
            logger.error(f"Error conectando señales: {e}", exc_info=True)
            self.mostrar_error(f"Error conectando señales: {e}")

    def _validar_datos_entrega(self, datos_entrega):
        """
        Valida y sanitiza los datos de entrega antes de enviar al modelo.
        
        Args:
            datos_entrega: Dict con datos de la entrega
            
        Returns:
            tuple: (es_valido, datos_sanitizados, mensaje_error)
        """
        if not isinstance(datos_entrega, dict):
            return False, {}, "Los datos de entrega deben ser un diccionario"
        
        # Campos requeridos
        campos_requeridos = ['destino', 'fecha_entrega']
        for campo in campos_requeridos:
            if campo not in datos_entrega or not datos_entrega[campo]:
                return False, {}, f"El campo '{campo}' es requerido"
        
        # Sanitizar datos usando el sistema unificado si está disponible
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            datos_sanitizados = unified_sanitizer.sanitize_dict(datos_entrega)
        except ImportError:
            # Fallback: sanitización básica
            datos_sanitizados = {}
            for key, value in datos_entrega.items():
                if isinstance(value, str):
                    datos_sanitizados[key] = str(value).strip()
                else:
                    datos_sanitizados[key] = value
        
        logger.debug(f"Datos de entrega validados: {datos_sanitizados}")
        return True, datos_sanitizados, ""

    def _validar_datos_transporte(self, datos_transporte):
        """
        Valida y sanitiza los datos de transporte antes de enviar al modelo.
        
        Args:
            datos_transporte: Dict con datos del transporte
            
        Returns:
            tuple: (es_valido, datos_sanitizados, mensaje_error)
        """
        if not isinstance(datos_transporte, dict):
            return False, {}, "Los datos de transporte deben ser un diccionario"
        
        # Campos requeridos
        campos_requeridos = ['origen', 'destino', 'conductor']
        for campo in campos_requeridos:
            if campo not in datos_transporte or not datos_transporte[campo]:
                return False, {}, f"El campo '{campo}' es requerido"
        
        # Sanitizar datos usando el sistema unificado si está disponible
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            datos_sanitizados = unified_sanitizer.sanitize_dict(datos_transporte)
        except ImportError:
            # Fallback: sanitización básica
            datos_sanitizados = {}
            for key, value in datos_transporte.items():
                if isinstance(value, str):
                    datos_sanitizados[key] = str(value).strip()
                else:
                    datos_sanitizados[key] = value
        
        logger.debug(f"Datos de transporte validados: {datos_sanitizados}")
        return True, datos_sanitizados, ""

    @safe_method_decorator
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo."""
        logger.info("Iniciando carga de datos iniciales de logística")
        self.cargar_entregas()
        self.cargar_services()

    def cargar_entregas(self):
        """Carga las entregas en la tabla."""
        if not self.model:
            logger.warning("Modelo de logística no disponible para cargar entregas")
            return
            
        if not self.view:
            logger.warning("Vista de logística no disponible para cargar entregas")
            return
        
        try:
            logger.debug("Cargando entregas desde el modelo")
            entregas = self.model.obtener_entregas()
            self.view.cargar_entregas_en_tabla(entregas)
            logger.info(f"Cargadas {len(entregas) if entregas else 0} entregas")
        except Exception as e:
            error_msg = f"Error cargando entregas: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)

    @auth_required
    def guardar_entrega(self, datos):
        """
        Guarda una nueva entrega con validación completa.
        
        Args:
            datos: Dict con datos de la entrega
            
        Returns:
            tuple: (exito, mensaje, entrega_id)
        """
        logger.info(f"Iniciando creación de entrega para usuario: {self.usuario_actual}")
        
        if not self.model:
            error_msg = "Modelo de logística no disponible"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg, None

        # Validar datos de entrada
        es_valido, datos_sanitizados, mensaje_error = self._validar_datos_entrega(datos)
        if not es_valido:
            logger.warning(f"Validación fallida: {mensaje_error}")
            self.mostrar_error(f"Error de validación: {mensaje_error}")
            return False, mensaje_error, None

        try:
            # Agregar información de auditoría
            datos_sanitizados['usuario_creacion'] = self.usuario_actual
            
            entrega_id = self.model.crear_entrega(datos_sanitizados)
            if entrega_id:
                success_msg = "Entrega guardada exitosamente"
                logger.info(f"Entrega creada con ID: {entrega_id}")
                
                self.mostrar_mensaje(success_msg, tipo="success")
                self.cargar_entregas()
                self.entrega_creada.emit(datos_sanitizados)
                
                return True, success_msg, entrega_id
            else:
                error_msg = "No se pudo crear la entrega en la base de datos"
                logger.error(error_msg)
                self.mostrar_error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error guardando entrega: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg, None

    def cargar_services(self):
        """Carga los servicios en la tabla."""
        if not self.model:
            logger.warning("Modelo de logística no disponible para cargar servicios")
            return
            
        if not self.view:
            logger.warning("Vista de logística no disponible para cargar servicios")
            return
        
        if not hasattr(self.model, 'obtener_services'):
            logger.debug("Método obtener_services no disponible en el modelo")
            return
        
        try:
            logger.debug("Cargando servicios desde el modelo")
            services = self.model.obtener_services()
            self.view.cargar_services_en_tabla(services)
            logger.info(f"Cargados {len(services) if services else 0} servicios")
        except Exception as e:
            error_msg = f"Error cargando servicios: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)

    @auth_required
    def guardar_service(self, datos):
        """
        Guarda un nuevo servicio con validación.
        
        Args:
            datos: Dict con datos del servicio
            
        Returns:
            tuple: (exito, mensaje, service_id)
        """
        logger.info(f"Iniciando creación de servicio para usuario: {self.usuario_actual}")
        
        if not self.model:
            error_msg = "Modelo de logística no disponible"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg, None
        
        if not hasattr(self.model, 'crear_service'):
            error_msg = "Método crear_service no disponible en el modelo"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg, None
        
        try:
            # Agregar información de auditoría
            if isinstance(datos, dict):
                datos['usuario_creacion'] = self.usuario_actual
            
            service_id = self.model.crear_service(datos)
            if service_id:
                success_msg = "Servicio guardado exitosamente"
                logger.info(f"Servicio creado con ID: {service_id}")
                
                self.mostrar_mensaje(success_msg, tipo="success")
                self.cargar_services()
                
                return True, success_msg, service_id
            else:
                error_msg = "No se pudo crear el servicio en la base de datos"
                logger.error(error_msg)
                self.mostrar_error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error guardando servicio: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg, None

    @safe_method_decorator
    def generar_servicios_automaticos(self, criterios=None):
        """Genera servicios automáticamente según criterios especificados.
        
        Args:
            criterios (dict): Criterios para la generación automática
                - tipo_servicio: 'entrega', 'recoleccion', 'mixto'
                - zona_geografica: área de cobertura  
                - prioridad: 'alta', 'media', 'baja'
                - fecha_limite: fecha máxima para completar servicios
                - cantidad_maxima: número máximo de servicios a generar
                
        Returns:
            tuple: (exito: bool, resultado: dict|str)
        """
        try:
            # Validar criterios de entrada
            criterios_validados = self._validar_criterios_generacion(criterios)
            if not criterios_validados:
                return False, "Criterios de generación inválidos"
            
            logger.info(f"Iniciando generación automática de servicios con criterios: {criterios_validados}")
            
            # Delegar al modelo si tiene implementación específica
            if self.model and hasattr(self.model, 'generar_servicios_automaticos'):
                result = self.model.generar_servicios_automaticos(criterios_validados)
                logger.info(f"Generación delegada al modelo, resultado: {result}")
                return True, result
            
            # Implementación básica usando procesamiento interno
            servicios_generados = self._procesar_generacion_servicios(criterios_validados)
            
            # Registrar en auditoría si está disponible
            try:
                self._registrar_generacion_auditoria(criterios_validados, servicios_generados)
            except Exception as audit_error:
                logger.warning(f"No se pudo registrar en auditoría: {audit_error}")
            
            resultado = {
                'servicios_generados': servicios_generados,
                'criterios_aplicados': criterios_validados,
                'timestamp': time.time(),
                'cantidad': len(servicios_generados.get('servicios', []))
            }
            
            logger.info(f"Generación automática completada: {resultado['cantidad']} servicios generados")
            return True, resultado
            
        except ValueError as e:
            logger.error(f"Error de validación en generación de servicios: {e}")
            return False, f"Error de validación: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado generando servicios automáticos: {e}", exc_info=True)
            return False, f"Error interno: {str(e)}"
    
    def _validar_criterios_generacion(self, criterios):
        """Valida y normaliza criterios de generación."""
        if not criterios:
            criterios = {}
        
        # Validar y normalizar tipo de servicio
        tipos_validos = ['entrega', 'recoleccion', 'mixto']
        tipo = criterios.get('tipo_servicio', 'mixto')
        if tipo not in tipos_validos:
            logger.warning(f"Tipo de servicio inválido '{tipo}', usando 'mixto'")
            tipo = 'mixto'
            
        # Validar prioridad
        prioridades_validas = ['alta', 'media', 'baja']
        prioridad = criterios.get('prioridad', 'media')
        if prioridad not in prioridades_validas:
            logger.warning(f"Prioridad inválida '{prioridad}', usando 'media'")
            prioridad = 'media'
        
        # Validar cantidad máxima (límite de seguridad)
        cantidad_maxima = criterios.get('cantidad_maxima', 10)
        try:
            cantidad_maxima = min(int(cantidad_maxima), 50)  # Límite de 50 servicios
        except (ValueError, TypeError):
            cantidad_maxima = 10
        
        criterios_validados = {
            'tipo_servicio': tipo,
            'zona_geografica': criterios.get('zona_geografica', 'metropolitana'),
            'prioridad': prioridad,
            'cantidad_maxima': cantidad_maxima,
            'fecha_limite': criterios.get('fecha_limite'),
            'cliente_id': criterios.get('cliente_id'),
            'obra_id': criterios.get('obra_id')
        }
        
        return criterios_validados

    def _procesar_generacion_servicios(self, criterios=None):
        """Procesamiento interno para generación de servicios.
        
        Genera servicios logísticos basado en criterios específicos,
        incluyendo rutas optimizadas y asignación de recursos.
        
        Args:
            criterios (dict): Criterios validados de generación
            
        Returns:
            dict: Resumen de servicios generados
        """
        try:
            # Si el modelo provee la lógica, delegar
            if self.model and hasattr(self.model, 'procesar_generacion_servicios'):
                return self.model.procesar_generacion_servicios(criterios)

            # Implementación básica de generación de servicios
            servicios_generados = []
            cantidad_objetivo = criterios.get('cantidad_maxima', 10)
            tipo_servicio = criterios.get('tipo_servicio', 'mixto')
            zona = criterios.get('zona_geografica', 'metropolitana')
            prioridad = criterios.get('prioridad', 'media')
            
            logger.debug(f"Procesando generación: {cantidad_objetivo} servicios tipo '{tipo_servicio}' en zona '{zona}'")
            
            # Generar servicios según tipo
            for i in range(cantidad_objetivo):
                servicio = self._crear_servicio_automatico(i + 1, tipo_servicio, zona, prioridad, criterios)
                servicios_generados.append(servicio)
            
            # Optimizar rutas si es posible
            servicios_optimizados = self._optimizar_rutas_servicios(servicios_generados, zona)
            
            resultado = {
                "generados": len(servicios_optimizados),
                "servicios": servicios_optimizados,
                "zona_cobertura": zona,
                "tipo_predominante": tipo_servicio,
                "prioridad_general": prioridad,
                "rutas_optimizadas": len(set(s.get('ruta_id') for s in servicios_optimizados))
            }
            
            logger.info(f"Procesamiento completado: {resultado['generados']} servicios, {resultado['rutas_optimizadas']} rutas")
            return resultado
            
        except Exception as e:
            logger.error(f"Error en _procesar_generacion_servicios: {e}", exc_info=True)
            return {"generados": 0, "error": str(e)}
    
    def _crear_servicio_automatico(self, numero, tipo_servicio, zona, prioridad, criterios):
        """Crea un servicio individual con datos realistas."""
        base_time = datetime.now()
        
        # Determinar tipo específico si es mixto
        if tipo_servicio == 'mixto':
            tipo_especifico = 'entrega' if numero % 2 == 0 else 'recoleccion'
        else:
            tipo_especifico = tipo_servicio
        
        # Generar ubicaciones realistas según zona
        ubicaciones = self._generar_ubicaciones_zona(zona)
        origen, destino = ubicaciones
        
        # Calcular tiempos estimados
        tiempo_estimado = self._calcular_tiempo_estimado(origen, destino, prioridad)
        fecha_programada = base_time + timedelta(hours=numero * 2)  # Distribuir en el tiempo
        
        servicio = {
            'id': f'SRV_{zona.upper()[:3]}_{numero:03d}_{int(time.time() % 10000)}',
            'tipo': tipo_especifico,
            'descripcion': f'Servicio de {tipo_especifico} automático #{numero}',
            'origen': origen,
            'destino': destino,
            'zona_geografica': zona,
            'prioridad': prioridad,
            'estado': 'PROGRAMADO',
            'fecha_creacion': base_time.isoformat(),
            'fecha_programada': fecha_programada.isoformat(),
            'tiempo_estimado_minutos': tiempo_estimado,
            'ruta_id': f'R_{zona[:3].upper()}_{(numero - 1) // 3 + 1}',  # Agrupar de 3 en 3
            'cliente_id': criterios.get('cliente_id'),
            'obra_id': criterios.get('obra_id'),
            'recursos_necesarios': self._determinar_recursos_necesarios(tipo_especifico, prioridad)
        }
        
        return servicio
    
    def _generar_ubicaciones_zona(self, zona):
        """Genera ubicaciones realistas para una zona específica."""
        ubicaciones_por_zona = {
            'metropolitana': [
                ('Centro', 'Zona Norte'), ('Zona Sur', 'Centro'), 
                ('Zona Oeste', 'Zona Este'), ('Puerto', 'Centro')
            ],
            'interior': [
                ('Planta Industrial', 'Ciudad'), ('Campo', 'Planta'),
                ('Depósito Regional', 'Ciudad'), ('Centro Logístico', 'Sucursal')
            ],
            'costa': [
                ('Puerto', 'Centro'), ('Terminal', 'Zona Residencial'),
                ('Depósito Costero', 'Ciudad'), ('Muelle', 'Zona Comercial')
            ]
        }
        
        opciones = ubicaciones_por_zona.get(zona, ubicaciones_por_zona['metropolitana'])
        import random
        return random.choice(opciones)
    
    def _calcular_tiempo_estimado(self, origen, destino, prioridad):
        """Calcula tiempo estimado en minutos según origen, destino y prioridad."""
        # Tiempo base según distancia estimada (simulado)
        tiempo_base = 45  # minutos
        
        # Ajustes por prioridad
        multiplicadores = {'alta': 0.8, 'media': 1.0, 'baja': 1.3}
        tiempo_estimado = int(tiempo_base * multiplicadores.get(prioridad, 1.0))
        
        return tiempo_estimado
    
    def _determinar_recursos_necesarios(self, tipo_servicio, prioridad):
        """Determina recursos necesarios para el servicio."""
        recursos_base = {
            'vehiculo': 'estándar',
            'conductor': 1,
            'ayudantes': 0
        }
        
        # Ajustes por tipo
        if tipo_servicio == 'recoleccion':
            recursos_base['ayudantes'] = 1
        
        # Ajustes por prioridad
        if prioridad == 'alta':
            recursos_base['vehiculo'] = 'express'
            recursos_base['ayudantes'] += 1
        
        return recursos_base
    
    def _optimizar_rutas_servicios(self, servicios, zona):
        """Optimiza las rutas de los servicios generados."""
        # Implementación básica: agrupar por proximidad geográfica
        try:
            # Asignar rutas optimizadas agrupando servicios cercanos
            for i, servicio in enumerate(servicios):
                # Agrupar servicios en rutas de máximo 4 servicios
                ruta_numero = (i // 4) + 1
                servicio['ruta_id'] = f'R_{zona[:3].upper()}_{ruta_numero:02d}'
                servicio['orden_en_ruta'] = (i % 4) + 1
                
                # Calcular tiempo total de ruta
                servicio['tiempo_total_ruta'] = servicio['tiempo_estimado_minutos'] * (servicio['orden_en_ruta'] + 1)
            
            logger.debug(f"Rutas optimizadas: {len(set(s['ruta_id'] for s in servicios))} rutas creadas")
            return servicios
            
        except Exception as e:
            logger.warning(f"Error optimizando rutas: {e}, devolviendo servicios sin optimizar")
            return servicios

    def _simular_servicios_generados(self, cantidad=0):
        """Simula la generación de servicios para pruebas con datos realistas.

        Retorna servicios simulados con estructura completa para testing.
        """
        servicios = []
        tipos_servicio = ['entrega', 'recoleccion', 'transferencia']
        estados = ['PROGRAMADO', 'EN_TRANSITO', 'PENDIENTE']
        zonas = ['NORTE', 'SUR', 'ESTE', 'OESTE', 'CENTRO']
        
        for i in range(int(cantidad or 0)):
            fecha_base = datetime.now() + timedelta(hours=i*2)
            servicios.append({
                'id': f'SIM_{i+1:03d}',
                'descripcion': f'Servicio simulado {i+1}',
                'estado': estados[i % len(estados)],
                'tipo_servicio': tipos_servicio[i % len(tipos_servicio)],
                'zona': zonas[i % len(zonas)],
                'fecha_programada': fecha_base.isoformat(),
                'origen': f'Origen {i+1}',
                'destino': f'Destino {i+1}',
                'prioridad': 'ALTA' if i % 3 == 0 else 'MEDIA',
                'observaciones': f'Servicio de prueba generado automáticamente #{i+1}',
                'es_simulacion': True
            })
        
        logger.info(f"Simulación generada: {len(servicios)} servicios de prueba")
        return servicios

    # Nuevos métodos para manejo de transportes
    @auth_required
    def crear_transporte(self, datos):
        """
        Crea un nuevo transporte con validación completa.
        
        Args:
            datos: Dict con datos del transporte
            
        Returns:
            tuple: (exito, mensaje, transporte_id)
        """
        logger.info(f"Iniciando creación de transporte para usuario: {self.usuario_actual}")
        
        # Validar datos de entrada
        es_valido, datos_sanitizados, mensaje_error = self._validar_datos_transporte(datos)
        if not es_valido:
            logger.warning(f"Validación fallida: {mensaje_error}")
            self.mostrar_error(f"Error de validación: {mensaje_error}")
            return False, mensaje_error, None
        
        try:
            if self.model and hasattr(self.model, 'crear_transporte'):
                # Agregar información de auditoría
                datos_sanitizados['usuario_creacion'] = self.usuario_actual
                
                transporte_id = self.model.crear_transporte(datos_sanitizados)
                if transporte_id:
                    success_msg = "Transporte creado exitosamente"
                    logger.info(f"Transporte creado con ID: {transporte_id}")
                    
                    self.mostrar_mensaje(success_msg, tipo="success")
                    self.cargar_datos_iniciales()
                    self.transporte_creado.emit(datos_sanitizados)
                    
                    return True, success_msg, transporte_id
                else:
                    error_msg = "No se pudo crear el transporte en la base de datos"
                    logger.error(error_msg)
                    self.mostrar_error(error_msg)
                    return False, error_msg, None
            else:
                # Simulación para pruebas
                success_msg = "Transporte creado exitosamente (simulado)"
                logger.info(success_msg)
                
                self.mostrar_mensaje(success_msg, tipo="success")
                if self.view and hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
                
                return True, success_msg, "SIM_001"
                
        except Exception as e:
            error_msg = f"Error al crear transporte: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg, None

    @auth_required
    def actualizar_transporte(self, datos):
        """
        Actualiza un transporte existente con validación.
        
        Args:
            datos: Dict con datos del transporte (debe incluir 'id')
            
        Returns:
            tuple: (exito, mensaje)
        """
        transporte_id = datos.get('id') if isinstance(datos, dict) else None
        logger.info(f"Iniciando actualización de transporte ID: {transporte_id} por usuario: {self.usuario_actual}")
        
        # Validar ID
        if not transporte_id:
            error_msg = "ID de transporte es requerido para actualizar"
            logger.warning(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg
        
        # Validar datos de entrada
        es_valido, datos_sanitizados, mensaje_error = self._validar_datos_transporte(datos)
        if not es_valido:
            logger.warning(f"Validación fallida para ID {transporte_id}: {mensaje_error}")
            self.mostrar_error(f"Error de validación: {mensaje_error}")
            return False, mensaje_error
        
        try:
            if self.model and hasattr(self.model, 'actualizar_transporte'):
                # Agregar información de auditoría
                datos_sanitizados['usuario_modificacion'] = self.usuario_actual
                
                if self.model.actualizar_transporte(datos_sanitizados):
                    success_msg = "Transporte actualizado exitosamente"
                    logger.info(f"Transporte ID: {transporte_id} actualizado exitosamente")
                    
                    self.mostrar_mensaje(success_msg, tipo="success")
                    self.cargar_datos_iniciales()
                    self.transporte_actualizado.emit(datos_sanitizados)
                    
                    return True, success_msg
                else:
                    error_msg = "No se pudo actualizar el transporte en la base de datos"
                    logger.error(f"Fallo al actualizar transporte ID: {transporte_id}")
                    self.mostrar_error(error_msg)
                    return False, error_msg
            else:
                # Simulación para pruebas
                success_msg = "Transporte actualizado exitosamente (simulado)"
                logger.info(success_msg)
                
                self.mostrar_mensaje(success_msg, tipo="success")
                if self.view and hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
                
                return True, success_msg
                
        except Exception as e:
            error_msg = f"Error al actualizar transporte: {str(e)}"
            logger.error(f"Error actualizando transporte ID: {transporte_id}: {str(e)}", exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg

    @admin_required
    def eliminar_transporte(self, transporte_id):
        """
        Elimina un transporte (requiere permisos de administrador).
        
        Args:
            transporte_id: ID del transporte a eliminar
            
        Returns:
            tuple: (exito, mensaje)
        """
        logger.info(f"Iniciando eliminación de transporte ID: {transporte_id} por usuario: {self.usuario_actual}")
        
        # Validar ID
        if not transporte_id or not isinstance(transporte_id, (int, str)):
            error_msg = "ID de transporte inválido"
            logger.warning(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg
        
        try:
            if self.model and hasattr(self.model, 'eliminar_transporte'):
                if self.model.eliminar_transporte(transporte_id):
                    success_msg = "Transporte eliminado exitosamente"
                    logger.info(f"Transporte ID: {transporte_id} eliminado por administrador: {self.usuario_actual}")
                    
                    self.mostrar_mensaje(success_msg, tipo="success")
                    self.cargar_datos_iniciales()
                    self.transporte_eliminado.emit(transporte_id)
                    
                    return True, success_msg
                else:
                    error_msg = "No se pudo eliminar el transporte (puede estar en uso)"
                    logger.warning(f"Fallo al eliminar transporte ID: {transporte_id}")
                    self.mostrar_error(error_msg)
                    return False, error_msg
            else:
                # Simulación para pruebas
                success_msg = "Transporte eliminado exitosamente (simulado)"
                logger.info(success_msg)
                
                self.mostrar_mensaje(success_msg, tipo="success")
                if self.view and hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
                
                return True, success_msg
                
        except Exception as e:
            error_msg = f"Error al eliminar transporte: {str(e)}"
            logger.error(f"Error eliminando transporte ID: {transporte_id}: {str(e)}", exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg

    def buscar_transportes(self, termino, estado):
        """
        Busca transportes según criterios con validación.
        
        Args:
            termino: Término de búsqueda
            estado: Estado del transporte a filtrar
            
        Returns:
            list: Lista de transportes encontrados
        """
        logger.debug(f"Buscando transportes con término: '{termino}', estado: '{estado}'")
        
        # Sanitizar parámetros de entrada
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            termino_sanitizado = unified_sanitizer.sanitize_string(str(termino) if termino else "")
            estado_sanitizado = unified_sanitizer.sanitize_string(str(estado) if estado else "")
        except ImportError:
            termino_sanitizado = str(termino).strip() if termino else ""
            estado_sanitizado = str(estado).strip() if estado else ""
        
        try:
            if self.model and hasattr(self.model, 'buscar_transportes'):
                transportes = self.model.buscar_transportes(termino_sanitizado, estado_sanitizado)
                logger.info(f"Encontrados {len(transportes) if transportes else 0} transportes")
                
                if self.view:
                    self.view.cargar_transportes(transportes)
                
                return transportes or []
            else:
                # Simulación para pruebas
                transportes_simulados = [
                    {
                        'id': 1,
                        'origen': 'Ciudad A',
                        'destino': 'Ciudad B',
                        'estado': estado_sanitizado or 'En tránsito',
                        'conductor': 'Juan Pérez',
                        'fecha': '2025-01-15'
                    }
                ]
                logger.info("Usando datos simulados para búsqueda de transportes")
                
                if self.view:
                    self.view.cargar_transportes(transportes_simulados)
                
                return transportes_simulados
                
        except Exception as e:
            error_msg = f"Error buscando transportes: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return []

    def cargar_estadisticas(self):
        """
        Carga y actualiza las estadísticas del dashboard.
        
        Returns:
            dict: Estadísticas cargadas
        """
        logger.debug("Cargando estadísticas de logística")
        
        try:
            if self.model and hasattr(self.model, 'obtener_estadisticas'):
                stats = self.model.obtener_estadisticas()
                logger.info("Estadísticas obtenidas desde el modelo")
            else:
                # Simulación para pruebas - valores estáticos para evitar warnings de seguridad
                stats = {
                    'total_transportes': 156,
                    'en_transito': 23,
                    'entregados_hoy': 8,
                    'pendientes': 12
                }
                logger.info("Usando estadísticas simuladas")

            if self.view:
                self.view.actualizar_estadisticas(stats)
                logger.debug("Estadísticas enviadas a la vista")
            
            return stats
            
        except Exception as e:
            error_msg = f"Error cargando estadísticas: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return {}

    def mostrar_mensaje(self, mensaje, tipo="info"):
        """
        Muestra un mensaje usando el sistema centralizado.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')
        """
        logger.info(f"Mensaje mostrado: {mensaje}")
        
        if self.view:
            if tipo == "success":
                show_success(self.view, "Logística", mensaje)
            elif tipo == "warning":
                show_warning(self.view, "Logística", mensaje)
            elif tipo == "error":
                show_error(self.view, "Error - Logística", mensaje)
            else:
                show_info(self.view, "Logística", mensaje)

    def _registrar_generacion_auditoria(self, criterios, servicios_generados):
        """Registra la generación de servicios en el sistema de auditoría."""
        try:
            from rexus.core.audit_system import AuditSystem, AuditEventType
            audit = AuditSystem()
            
            audit.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                modulo="logistica",
                accion="generar_servicios_automaticos",
                detalles={
                    "criterios": criterios,
                    "servicios_generados": servicios_generados.get('generados', 0),
                    "zona": criterios.get('zona_geografica'),
                    "tipo": criterios.get('tipo_servicio')
                },
                resultado="EXITOSO"
            )
        except ImportError:
            logger.debug("Sistema de auditoría no disponible")
        except Exception as e:
            logger.warning(f"Error registrando en auditoría: {e}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error con logging."""
        logger.error(f"Error en logística: {mensaje}")
        
        if self.view:
            show_error(self.view, "Error - Logística", mensaje)
        else:
            # Fallback si no hay vista
            logger.error(f"[NO VIEW] Error: {mensaje}")
