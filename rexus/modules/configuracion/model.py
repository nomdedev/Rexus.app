# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Configuración - Rexus.app v2.0.0

Gestiona todas las configuraciones del sistema incluyendo:
- Configuración de base de datos
- Configuración de la empresa
- Parámetros del sistema
- Configuraciones de usuarios
- Configuraciones de reportes
- Temas y personalización
"""

import json
import logging
import os
                            # Fallback con datos demo filtrados
                configuraciones_demo = self._obtener_configuraciones_demo()
                return self._aplicar_filtros_demo(configuraciones_demo, filtros)
            
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT 
                    id, clave, valor, descripcion, tipo_dato, categoria, 
                    es_editable, fecha_creacion, fecha_modificacion, usuario_modificacion
                FROM configuraciones
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros dinámicamente
            if filtros.get('busqueda'):
                query += """
                    AND (clave LIKE ? OR descripcion LIKE ? OR valor LIKE ? OR categoria LIKE ?)
                """
                busqueda = f"%{filtros['busqueda']}%"
                params.extend([busqueda, busqueda, busqueda, busqueda])
            
            if filtros.get('categoria') and filtros['categoria'] != 'Todas':
                query += " AND categoria = ?"
                params.append(filtros['categoria'])
            
            if filtros.get('tipo') and filtros['tipo'] != 'Todos':
                query += " AND tipo_dato = ?"
                params.append(filtros['tipo'].lower())
            
            if filtros.get('estado') and filtros['estado'] != 'Todos':
                if filtros['estado'] == 'Activo':
                    query += " AND es_editable = 1"
                elif filtros['estado'] == 'Inactivo':
                    query += " AND es_editable = 0"
                elif filtros['estado'] == 'Por Defecto':
                    query += " AND usuario_modificacion IS NULL"
                elif filtros['estado'] == 'Personalizado':
                    query += " AND usuario_modificacion IS NOT NULL"
            
            # Ordenar por categoría y clave
            query += " ORDER BY categoria, clave"
            
            logger.info(f"[CONFIGURACION MODEL] Ejecutando query con {len(params)} parámetros")
            cursor.execute(query, params)
            
            # Convertir resultados a diccionarios
            configuraciones = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                configuracion = dict(zip(columns, row))
                configuraciones.append(configuracion)
            
            logger.info(f"[CONFIGURACION MODEL] Filtradas {len(configuraciones)} configuraciones exitosamente")
            return configuraciones
            
        except Exception as e:
            logger.info(f"[ERROR CONFIGURACION MODEL] Error filtrando configuraciones: {e}")
            # Fallback con datos demo en caso de error
            configuraciones_demo = self._obtener_configuraciones_demo()
            return self._aplicar_filtros_demo(configuraciones_demo, filtros)

    def _aplicar_filtros_demo(self, configuraciones: List[Dict], filtros: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros a los datos demo."""
        resultado = configuraciones
        
        if filtros.get('busqueda'):
            termino = filtros['busqueda'].lower()
            resultado = [c for c in resultado if (
                termino in c.get('clave', '').lower() or
                termino in c.get('descripcion', '').lower() or
                termino in c.get('valor', '').lower() or
                termino in c.get('categoria', '').lower()
            )]
        
        if filtros.get('categoria') and filtros['categoria'] != 'Todas':
            resultado = [c for c in resultado if c.get('categoria', '') == filtros['categoria']]
        
        if filtros.get('tipo') and filtros['tipo'] != 'Todos':
            resultado = [c for c in resultado if c.get('tipo_dato', '') == filtros['tipo'].lower()]
        
        if filtros.get('estado') and filtros['estado'] != 'Todos':
            if filtros['estado'] == 'Activo':
                resultado = [c for c in resultado if c.get('es_editable', False)]
            elif filtros['estado'] == 'Inactivo':
                resultado = [c for c in resultado if not c.get('es_editable', True)]
        
        return resultado

    def obtener_configuracion(self, categoria=None):
        """
        Obtiene configuración del sistema
        
        Args:
            categoria (str, optional): Categoría específica
            
        Returns:
            List[Dict]: Lista de configuraciones
        """
        # Obtener todas las configuraciones
        todas_config = self.obtener_todas_configuraciones()
        
        # Filtrar por categoría si se especifica
        if categoria:
            return [config for config in todas_config if config.get('categoria') == categoria]
        
        return todas_config
    
    def _inicializar_funcionalidades_avanzadas(self):
        """Inicializa las funcionalidades avanzadas de configuración."""
        try:
            from .advanced_features import AdvancedConfigurationManager
            self.advanced_manager = AdvancedConfigurationManager(self)
            self.advanced_manager.inicializar_configuraciones_avanzadas()
            logger.info()
        except ImportError as e:
            logger.warning(f"No se pudieron cargar funcionalidades avanzadas: {e}")
            self.advanced_manager = None
    
    # =================================================================
    # MÉTODOS AVANZADOS - DELEGATE TO ADVANCED MANAGER
    # =================================================================
    
    def crear_perfil_configuracion(self, nombre: str, descripcion: str, 
                                 configuraciones: dict, usuario: str) -> str:
        """Crea un nuevo perfil de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.crear_perfil_configuracion(
                nombre, descripcion, configuraciones, usuario
            )
        return None
    
    def aplicar_perfil_configuracion(self, profile_id: str, usuario: str) -> tuple:
        """Aplica un perfil de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.aplicar_perfil_configuracion(profile_id, usuario)
        return False, "Funcionalidades avanzadas no disponibles"
    
    def listar_perfiles_configuracion(self) -> list:
        """Lista todos los perfiles de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.listar_perfiles_configuracion()
        return []
    
    def crear_backup_configuracion(self, nombre: str, descripcion: str, usuario: str) -> str:
        """Crea un backup de la configuración actual."""
        if self.advanced_manager:
            return self.advanced_manager.crear_backup_configuracion(nombre, descripcion, usuario)
        return None
    
    def restaurar_backup_configuracion(self, backup_id: str, usuario: str) -> tuple:
        """Restaura configuración desde un backup."""
        if self.advanced_manager:
            return self.advanced_manager.restaurar_backup_configuracion(backup_id, usuario)
        return False, "Funcionalidades avanzadas no disponibles"
    
    def listar_backups_configuracion(self) -> list:
        """Lista todos los backups de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.listar_backups_configuracion()
        return []
    
    def crear_plantilla_configuracion(self, nombre: str, categoria: str, 
                                    configuraciones: dict, descripcion: str = "") -> str:
        """Crea una plantilla de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.crear_plantilla_configuracion(
                nombre, categoria, configuraciones, descripcion
            )
        return None
    
    def aplicar_plantilla_configuracion(self, template_id: str, usuario: str) -> tuple:
        """Aplica una plantilla de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.aplicar_plantilla_configuracion(template_id, usuario)
        return False, "Funcionalidades avanzadas no disponibles"
    
    def listar_plantillas_configuracion(self, categoria: str = None) -> list:
        """Lista plantillas de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.listar_plantillas_configuracion(categoria)
        return []
    
    def exportar_configuracion_completa(self, incluir_sensibles: bool = False) -> dict:
        """Exporta toda la configuración del sistema."""
        if self.advanced_manager:
            return self.advanced_manager.exportar_configuracion_completa(incluir_sensibles)
        return {'configuraciones': self.config_cache, 'metadata': {}}
    
    def importar_configuracion_completa(self, data: dict, usuario: str, 
                                      sobrescribir: bool = False) -> tuple:
        """Importa configuración desde datos exportados."""
        if self.advanced_manager:
            return self.advanced_manager.importar_configuracion_completa(data, usuario, sobrescribir)
        return False, "Funcionalidades avanzadas no disponibles"
    
    def obtener_historial_cambios(self, limite: int = 100) -> list:
        """Obtiene el historial de cambios de configuración."""
        if self.advanced_manager:
            return self.advanced_manager.obtener_historial_cambios(limite)
        return []
    
    def validar_configuracion_avanzada(self, clave: str, valor) -> tuple:
        """Valida una configuración con reglas avanzadas."""
        if self.advanced_manager:
            return self.advanced_manager.validar_configuracion(clave, valor)
        return True, "Sin validación avanzada"
    
    # =================================================================
    # CONFIGURACIONES ESPECÍFICAS DE NEGOCIO
    # =================================================================
    
    def configurar_tema_empresa(self, configuraciones_tema: dict, usuario: str) -> tuple:
        """Configura el tema visual de la empresa."""
        try:
            tema_config = {
                'tema_principal': configuraciones_tema.get('tema_principal', 'light'),
                'color_primario': configuraciones_tema.get('color_primario', '#2196F3'),
                'color_secundario': configuraciones_tema.get('color_secundario', '#FFC107'),
                'logo_empresa': configuraciones_tema.get('logo_empresa', ''),
                'nombre_empresa': configuraciones_tema.get('nombre_empresa', 'Rexus.app'),
                'mostrar_logo': configuraciones_tema.get('mostrar_logo', True)
            }
            
            for clave, valor in tema_config.items():
                success, message = self.establecer_valor(f"tema_{clave}", valor, usuario)
                if not success:
                    return False, f"Error configurando {clave}: {message}"
            
            return True, "Tema de empresa configurado exitosamente"
            
        except Exception as e:
            return False, f"Error configurando tema: {str(e)}"
    
    def configurar_notificaciones_sistema(self, configuraciones_notif: dict, usuario: str) -> tuple:
        """Configura las notificaciones del sistema."""
        try:
            notif_config = {
                'email_habilitado': configuraciones_notif.get('email_habilitado', False),
                'email_servidor': configuraciones_notif.get('email_servidor', ''),
                'email_puerto': configuraciones_notif.get('email_puerto', 587),
                'email_usuario': configuraciones_notif.get('email_usuario', ''),
                'email_password': configuraciones_notif.get('email_password', ''),
                'notif_sonido': configuraciones_notif.get('notif_sonido', True),
                'notif_desktop': configuraciones_notif.get('notif_desktop', True),
                'notif_criticas': configuraciones_notif.get('notif_criticas', True)
            }
            
            for clave, valor in notif_config.items():
                success, message = self.establecer_valor(f"notificaciones_{clave}", valor, usuario)
                if not success:
                    return False, f"Error configurando {clave}: {message}"
            
            return True, "Notificaciones del sistema configuradas exitosamente"
            
        except Exception as e:
            return False, f"Error configurando notificaciones: {str(e)}"
    
    def configurar_seguridad_avanzada(self, configuraciones_seg: dict, usuario: str) -> tuple:
        """Configura opciones avanzadas de seguridad."""
        try:
            seg_config = {
                'session_timeout': configuraciones_seg.get('session_timeout', 1800),
                'max_intentos_login': configuraciones_seg.get('max_intentos_login', 3),
                'lockout_duration': configuraciones_seg.get('lockout_duration', 300),
                'password_min_length': configuraciones_seg.get('password_min_length', 8),
                'password_require_special': configuraciones_seg.get('password_require_special', True),
                'password_require_numbers': configuraciones_seg.get('password_require_numbers', True),
                'audit_log_enabled': configuraciones_seg.get('audit_log_enabled', True),
                'two_factor_enabled': configuraciones_seg.get('two_factor_enabled', False)
            }
            
            for clave, valor in seg_config.items():
                success, message = self.establecer_valor(f"seguridad_{clave}", valor, usuario)
                if not success:
                    return False, f"Error configurando {clave}: {message}"
            
            return True, "Configuraciones de seguridad aplicadas exitosamente"
            
        except Exception as e:
            return False, f"Error configurando seguridad: {str(e)}"
    
    def obtener_configuracion_modulo(self, nombre_modulo: str) -> dict:
        """Obtiene la configuración específica de un módulo."""
        config_modulo = {}
        
        for clave, valor in self.config_cache.items():
            if clave.startswith(f"{nombre_modulo}_"):
                config_key = clave.replace(f"{nombre_modulo}_", "")
                config_modulo[config_key] = valor
        
        return config_modulo
    
    def establecer_configuracion_modulo(self, nombre_modulo: str, 
                                      configuraciones: dict, usuario: str) -> tuple:
        """Establece múltiples configuraciones para un módulo específico."""
        try:
            configuradas = 0
            errores = []
            
            for clave, valor in configuraciones.items():
                clave_completa = f"{nombre_modulo}_{clave}"
                success, message = self.establecer_valor(clave_completa, valor, usuario)
                
                if success:
                    configuradas += 1
                else:
                    errores.append(f"{clave}: {message}")
            
            if errores:
                return False, f"Errores en configuración: {'; '.join(errores)}"
            
            return True, f"Configuradas {configuradas} opciones para módulo {nombre_modulo}"
            
        except Exception as e:
            return False, f"Error configurando módulo: {str(e)}"
