#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Avanzada - Funcionalidades Faltantes
Implementa todas las características que debe tener un módulo de configuración completo
"""

import json
import os
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import uuid

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("configuracion.advanced")
except ImportError:
    logger = logging.getLogger("configuracion.advanced")

@dataclass
class ConfigurationProfile:
    """Perfil de configuración personalizado."""
    id: str
    nombre: str
    descripcion: str
    configuraciones: Dict[str, Any]
    usuario_creador: str
    fecha_creacion: datetime.datetime
    activo: bool = False

@dataclass
class ConfigurationBackup:
    """Backup de configuración."""
    id: str
    nombre: str
    configuraciones: Dict[str, Any]
    fecha_backup: datetime.datetime
    usuario: str
    descripcion: str

class AdvancedConfigurationManager:
    """Manager avanzado de configuraciones con funcionalidades completas."""
    
    def __init__(self, config_model):
        self.config_model = config_model
        self.profiles = {}
        self.backups = []
        self.configuration_templates = {}
        self.validation_rules = {}
        self.change_history = []
        
    # =================================================================
    # GESTIÓN DE PERFILES DE CONFIGURACIÓN
    # =================================================================
    
    def crear_perfil_configuracion(self, nombre: str, descripcion: str, 
                                 configuraciones: Dict[str, Any], 
                                 usuario: str) -> str:
        """Crea un nuevo perfil de configuración personalizado."""
        profile_id = str(uuid.uuid4())
        
        profile = ConfigurationProfile(
            id=profile_id,
            nombre=nombre,
            descripcion=descripcion,
            configuraciones=configuraciones.copy(),
            usuario_creador=usuario,
            fecha_creacion=datetime.datetime.now(),
            activo=False
        )
        
        self.profiles[profile_id] = profile
        
        logger.info(f"Perfil de configuración creado: {nombre} por {usuario}")
        return profile_id
    
    def aplicar_perfil_configuracion(self, profile_id: str, usuario: str) -> Tuple[bool, str]:
        """Aplica un perfil de configuración al sistema."""
        if profile_id not in self.profiles:
            return False, f"Perfil {profile_id} no encontrado"
        
        profile = self.profiles[profile_id]
        
        try:
            # Crear backup antes de aplicar
            backup_id = self.crear_backup_automatico(f"Antes de aplicar perfil {profile.nombre}", usuario)
            
            # Aplicar configuraciones del perfil
            for clave, valor in profile.configuraciones.items():
                success, message = self.config_model.establecer_valor(clave, valor, usuario)
                if not success:
                    logger.warning(f"Error aplicando {clave}: {message}")
            
            # Marcar perfil como activo
            for p in self.profiles.values():
                p.activo = False
            profile.activo = True
            
            self._registrar_cambio("PROFILE_APPLIED", {
                'profile_id': profile_id,
                'profile_name': profile.nombre,
                'backup_id': backup_id
            }, usuario)
            
            return True, f"Perfil {profile.nombre} aplicado exitosamente"
            
        except Exception as e:
            logger.error(f"Error aplicando perfil {profile.nombre}: {str(e)}")
            return False, f"Error aplicando perfil: {str(e)}"
    
    def listar_perfiles_configuracion(self) -> List[Dict[str, Any]]:
        """Lista todos los perfiles de configuración disponibles."""
        return [
            {
                'id': profile.id,
                'nombre': profile.nombre,
                'descripcion': profile.descripcion,
                'usuario_creador': profile.usuario_creador,
                'fecha_creacion': profile.fecha_creacion.isoformat(),
                'activo': profile.activo,
                'total_configuraciones': len(profile.configuraciones)
            }
            for profile in self.profiles.values()
        ]
    
    # =================================================================
    # SISTEMA DE BACKUP Y RESTAURACIÓN
    # =================================================================
    
    def crear_backup_configuracion(self, nombre: str, descripcion: str, 
                                 usuario: str) -> str:
        """Crea un backup completo de la configuración actual."""
        backup_id = str(uuid.uuid4())
        
        # Obtener todas las configuraciones actuales
        configuraciones_actuales = {}
        try:
            # Aquí iría la lógica para obtener todas las configuraciones
            # Por ahora usamos el cache del modelo
            configuraciones_actuales = self.config_model.config_cache.copy()
        except Exception as e:
            logger.error(f"Error obteniendo configuraciones para backup: {str(e)}")
            configuraciones_actuales = {}
        
        backup = ConfigurationBackup(
            id=backup_id,
            nombre=nombre,
            configuraciones=configuraciones_actuales,
            fecha_backup=datetime.datetime.now(),
            usuario=usuario,
            descripcion=descripcion
        )
        
        self.backups.append(backup)
        
        # Guardar backup en archivo
        self._guardar_backup_archivo(backup)
        
        logger.info(f"Backup de configuración creado: {nombre} por {usuario}")
        return backup_id
    
    def crear_backup_automatico(self, descripcion: str, usuario: str) -> str:
        """Crea un backup automático con timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"AUTO_BACKUP_{timestamp}"
        return self.crear_backup_configuracion(nombre, descripcion, usuario)
    
    def restaurar_backup_configuracion(self, backup_id: str, usuario: str) -> Tuple[bool, str]:
        """Restaura la configuración desde un backup."""
        backup = None
        for b in self.backups:
            if b.id == backup_id:
                backup = b
                break
        
        if not backup:
            return False, f"Backup {backup_id} no encontrado"
        
        try:
            # Crear backup de seguridad antes de restaurar
            safety_backup_id = self.crear_backup_automatico(f"Antes de restaurar {backup.nombre}", usuario)
            
            # Restaurar configuraciones
            for clave, valor in backup.configuraciones.items():
                success, message = self.config_model.establecer_valor(clave, valor, usuario)
                if not success:
                    logger.warning(f"Error restaurando {clave}: {message}")
            
            self._registrar_cambio("BACKUP_RESTORED", {
                'backup_id': backup_id,
                'backup_name': backup.nombre,
                'safety_backup_id': safety_backup_id
            }, usuario)
            
            return True, f"Configuración restaurada desde backup {backup.nombre}"
            
        except Exception as e:
            logger.error(f"Error restaurando backup {backup.nombre}: {str(e)}")
            return False, f"Error restaurando backup: {str(e)}"
    
    def listar_backups_configuracion(self) -> List[Dict[str, Any]]:
        """Lista todos los backups de configuración disponibles."""
        return [
            {
                'id': backup.id,
                'nombre': backup.nombre,
                'descripcion': backup.descripcion,
                'fecha_backup': backup.fecha_backup.isoformat(),
                'usuario': backup.usuario,
                'total_configuraciones': len(backup.configuraciones)
            }
            for backup in sorted(self.backups, key=lambda x: x.fecha_backup, reverse=True)
        ]
    
    # =================================================================
    # PLANTILLAS DE CONFIGURACIÓN
    # =================================================================
    
    def crear_plantilla_configuracion(self, nombre: str, categoria: str, 
                                    configuraciones: Dict[str, Any],
                                    descripcion: str = "") -> str:
        """Crea una plantilla de configuración reutilizable."""
        template_id = str(uuid.uuid4())
        
        template = {
            'id': template_id,
            'nombre': nombre,
            'categoria': categoria,
            'configuraciones': configuraciones.copy(),
            'descripcion': descripcion,
            'fecha_creacion': datetime.datetime.now().isoformat(),
            'uso_count': 0
        }
        
        self.configuration_templates[template_id] = template
        
        logger.info(f"Plantilla de configuración creada: {nombre} en categoría {categoria}")
        return template_id
    
    def aplicar_plantilla_configuracion(self, template_id: str, usuario: str) -> Tuple[bool, str]:
        """Aplica una plantilla de configuración."""
        if template_id not in self.configuration_templates:
            return False, f"Plantilla {template_id} no encontrada"
        
        template = self.configuration_templates[template_id]
        
        try:
            # Crear backup antes de aplicar plantilla
            backup_id = self.crear_backup_automatico(f"Antes de aplicar plantilla {template['nombre']}", usuario)
            
            # Aplicar configuraciones de la plantilla
            for clave, valor in template['configuraciones'].items():
                success, message = self.config_model.establecer_valor(clave, valor, usuario)
                if not success:
                    logger.warning(f"Error aplicando configuración de plantilla {clave}: {message}")
            
            # Incrementar contador de uso
            template['uso_count'] += 1
            
            self._registrar_cambio("TEMPLATE_APPLIED", {
                'template_id': template_id,
                'template_name': template['nombre'],
                'backup_id': backup_id
            }, usuario)
            
            return True, f"Plantilla {template['nombre']} aplicada exitosamente"
            
        except Exception as e:
            logger.error(f"Error aplicando plantilla {template['nombre']}: {str(e)}")
            return False, f"Error aplicando plantilla: {str(e)}"
    
    def listar_plantillas_configuracion(self, categoria: str = None) -> List[Dict[str, Any]]:
        """Lista plantillas de configuración, opcionalmente filtradas por categoría."""
        templates = list(self.configuration_templates.values())
        
        if categoria:
            templates = [t for t in templates if t['categoria'] == categoria]
        
        return sorted(templates, key=lambda x: x['uso_count'], reverse=True)
    
    # =================================================================
    # VALIDACIÓN Y REGLAS
    # =================================================================
    
    def agregar_regla_validacion(self, clave: str, regla: Dict[str, Any]) -> bool:
        """Agrega una regla de validación para una clave de configuración."""
        try:
            self.validation_rules[clave] = regla
            logger.info(f"Regla de validación agregada para {clave}")
            return True
        except Exception as e:
            logger.error(f"Error agregando regla de validación para {clave}: {str(e)}")
            return False
    
    def validar_configuracion(self, clave: str, valor: Any) -> Tuple[bool, str]:
        """Valida un valor de configuración contra las reglas definidas."""
        if clave not in self.validation_rules:
            return True, "Sin reglas de validación"
        
        regla = self.validation_rules[clave]
        
        try:
            # Validar tipo
            if 'tipo' in regla:
                tipo_esperado = regla['tipo']
                if not isinstance(valor, tipo_esperado):
                    return False, f"Tipo incorrecto. Esperado: {tipo_esperado.__name__}"
            
            # Validar rango numérico
            if 'min_valor' in regla and valor < regla['min_valor']:
                return False, f"Valor menor al mínimo permitido: {regla['min_valor']}"
            
            if 'max_valor' in regla and valor > regla['max_valor']:
                return False, f"Valor mayor al máximo permitido: {regla['max_valor']}"
            
            # Validar longitud de string
            if 'min_longitud' in regla and len(str(valor)) < regla['min_longitud']:
                return False, f"Longitud menor a la mínima: {regla['min_longitud']}"
            
            if 'max_longitud' in regla and len(str(valor)) > regla['max_longitud']:
                return False, f"Longitud mayor a la máxima: {regla['max_longitud']}"
            
            # Validar valores permitidos
            if 'valores_permitidos' in regla and valor not in regla['valores_permitidos']:
                return False, f"Valor no permitido. Valores válidos: {regla['valores_permitidos']}"
            
            # Validar regex
            if 'patron' in regla:
                import re
                if not re.match(regla['patron'], str(valor)):
                    return False, f"Valor no coincide con el patrón requerido"
            
            return True, "Validación exitosa"
            
        except Exception as e:
            logger.error(f"Error validando configuración {clave}: {str(e)}")
            return False, f"Error en validación: {str(e)}"
    
    # =================================================================
    # EXPORTACIÓN E IMPORTACIÓN
    # =================================================================
    
    def exportar_configuracion_completa(self, incluir_sensibles: bool = False) -> Dict[str, Any]:
        """Exporta toda la configuración del sistema."""
        configuraciones = self.config_model.config_cache.copy()
        
        if not incluir_sensibles:
            # Filtrar configuraciones sensibles
            claves_sensibles = ['db_password', 'secret_key', 'api_key', 'token']
            configuraciones = {
                k: v for k, v in configuraciones.items()
                if not any(sensible in k.lower() for sensible in claves_sensibles)
            }
        
        export_data = {
            'configuraciones': configuraciones,
            'metadata': {
                'fecha_exportacion': datetime.datetime.now().isoformat(),
                'version_sistema': '2.0.0',
                'total_configuraciones': len(configuraciones),
                'incluye_sensibles': incluir_sensibles
            }
        }
        
        return export_data
    
    def importar_configuracion_completa(self, data: Dict[str, Any], 
                                      usuario: str, 
                                      sobrescribir: bool = False) -> Tuple[bool, str]:
        """Importa configuración desde datos exportados."""
        try:
            if 'configuraciones' not in data:
                return False, "Formato de datos inválido"
            
            # Crear backup antes de importar
            backup_id = self.crear_backup_automatico("Antes de importación masiva", usuario)
            
            configuraciones = data['configuraciones']
            importadas = 0
            errores = 0
            
            for clave, valor in configuraciones.items():
                # Validar si existe y si se debe sobrescribir
                if not sobrescribir and clave in self.config_model.config_cache:
                    continue
                
                # Validar configuración
                valido, mensaje = self.validar_configuracion(clave, valor)
                if not valido:
                    logger.warning(f"Configuración {clave} no válida: {mensaje}")
                    errores += 1
                    continue
                
                # Aplicar configuración
                success, message = self.config_model.establecer_valor(clave, valor, usuario)
                if success:
                    importadas += 1
                else:
                    errores += 1
                    logger.warning(f"Error importando {clave}: {message}")
            
            self._registrar_cambio("CONFIGURATION_IMPORTED", {
                'total_configuraciones': len(configuraciones),
                'importadas': importadas,
                'errores': errores,
                'backup_id': backup_id
            }, usuario)
            
            return True, f"Importación completada: {importadas} configuraciones importadas, {errores} errores"
            
        except Exception as e:
            logger.error(f"Error importando configuración: {str(e)}")
            return False, f"Error importando configuración: {str(e)}"
    
    # =================================================================
    # HISTORIAL Y AUDITORÍA
    # =================================================================
    
    def obtener_historial_cambios(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el historial de cambios de configuración."""
        return sorted(self.change_history, key=lambda x: x['timestamp'], reverse=True)[:limite]
    
    def _registrar_cambio(self, accion: str, detalles: Dict[str, Any], usuario: str):
        """Registra un cambio en el historial."""
        cambio = {
            'id': str(uuid.uuid4()),
            'accion': accion,
            'detalles': detalles,
            'usuario': usuario,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.change_history.append(cambio)
        
        # Mantener solo los últimos 1000 cambios
        if len(self.change_history) > 1000:
            self.change_history = self.change_history[-1000:]
    
    def _guardar_backup_archivo(self, backup: ConfigurationBackup):
        """Guarda un backup en archivo."""
        try:
            backups_dir = Path("data/config_backups")
            backups_dir.mkdir(exist_ok=True)
            
            filename = f"backup_{backup.id}_{backup.fecha_backup.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = backups_dir / filename
            
            backup_data = {
                'id': backup.id,
                'nombre': backup.nombre,
                'descripcion': backup.descripcion,
                'fecha_backup': backup.fecha_backup.isoformat(),
                'usuario': backup.usuario,
                'configuraciones': backup.configuraciones
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup guardado en archivo: {filepath}")
            
        except Exception as e:
            logger.error(f"Error guardando backup en archivo: {str(e)}")

    # =================================================================
    # CONFIGURACIONES PREDEFINIDAS
    # =================================================================
    
    def inicializar_configuraciones_avanzadas(self):
        """Inicializa configuraciones y plantillas predefinidas."""
        
        # Plantilla para desarrollo
        self.crear_plantilla_configuracion(
            "Desarrollo",
            "Entorno",
            {
                "debug_mode": True,
                "log_level": "DEBUG",
                "auto_backup": False,
                "session_timeout": 3600,
                "theme": "dark"
            },
            "Configuración optimizada para desarrollo"
        )
        
        # Plantilla para producción
        self.crear_plantilla_configuracion(
            "Producción",
            "Entorno",
            {
                "debug_mode": False,
                "log_level": "WARNING",
                "auto_backup": True,
                "session_timeout": 1800,
                "theme": "light",
                "security_strict": True
            },
            "Configuración optimizada para producción"
        )
        
        # Reglas de validación básicas
        self.agregar_regla_validacion("session_timeout", {
            'tipo': int,
            'min_valor': 300,
            'max_valor': 86400
        })
        
        self.agregar_regla_validacion("theme", {
            'tipo': str,
            'valores_permitidos': ['light', 'dark', 'auto']
        })
        
        logger.info("Configuraciones avanzadas inicializadas")