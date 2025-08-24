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
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ConfiguracionModel:
    """Modelo para gestionar configuraciones del sistema."""
    
    def __init__(self, db_connection=None):
        """
        Inicializar modelo de configuración.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.configuraciones_cache = {}
        logger.info("ConfiguracionModel inicializado")
    
    def crear_tablas(self):
        """Crea las tablas necesarias para configuraciones."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            
            # Tabla principal de configuraciones
            create_config_table = """
                CREATE TABLE IF NOT EXISTS configuraciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clave TEXT NOT NULL UNIQUE,
                    valor TEXT NOT NULL,
                    tipo TEXT DEFAULT 'string',
                    categoria TEXT DEFAULT 'general',
                    descripcion TEXT,
                    es_editable BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_modificacion TEXT DEFAULT 'SISTEMA'
                )
            """
            
            cursor.execute(create_config_table)
            self.db_connection.commit()
            
            # Insertar configuraciones por defecto si no existen
            self._insertar_configuraciones_default()
            
            logger.debug("Tablas de configuración creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tablas de configuración: {e}")
            return False
    
    def _insertar_configuraciones_default(self):
        """Inserta configuraciones por defecto del sistema."""
        try:
            cursor = self.db_connection.cursor()
            
            configuraciones_default = [
                ('empresa_nombre', 'Rexus.app', 'string', 'empresa', 'Nombre de la empresa'),
                ('empresa_direccion', '', 'string', 'empresa', 'Dirección de la empresa'),
                ('empresa_telefono', '', 'string', 'empresa', 'Teléfono de la empresa'),
                ('empresa_email', '', 'string', 'empresa', 'Email de la empresa'),
                ('sistema_tema', 'light', 'string', 'sistema', 'Tema del sistema'),
                ('sistema_idioma', 'es', 'string', 'sistema', 'Idioma del sistema'),
                ('bd_backup_auto', 'true', 'boolean', 'database', 'Backup automático'),
                ('bd_backup_frecuencia', '24', 'number', 'database', 'Frecuencia backup (horas)'),
                ('usuario_sesion_timeout', '480', 'number', 'usuario', 'Timeout de sesión (minutos)'),
                ('sistema_logs_nivel', 'INFO', 'string', 'sistema', 'Nivel de logs')
            ]
            
            for config in configuraciones_default:
                cursor.execute("""
                    INSERT OR IGNORE INTO configuraciones 
                    (clave, valor, tipo, categoria, descripcion) 
                    VALUES (?, ?, ?, ?, ?)
                """, config)
            
            self.db_connection.commit()
            logger.debug("Configuraciones por defecto insertadas")
            
        except Exception as e:
            logger.error(f"Error insertando configuraciones default: {e}")
    
    def obtener_todas_configuraciones(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las configuraciones del sistema.
        
        Returns:
            Lista de configuraciones
        """
        try:
            if not self.db_connection:
                logger.warning("BD no disponible, usando datos demo")
                return self._obtener_configuraciones_demo()
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, clave, valor, tipo, categoria, descripcion, 
                       es_editable, fecha_creacion, fecha_modificacion, 
                       usuario_modificacion
                FROM configuraciones 
                ORDER BY categoria, clave
            """)
            
            configuraciones = []
            for row in cursor.fetchall():
                config = {
                    'id': row[0],
                    'clave': row[1],
                    'valor': row[2],
                    'tipo': row[3],
                    'categoria': row[4],
                    'descripcion': row[5],
                    'es_editable': bool(row[6]),
                    'fecha_creacion': row[7],
                    'fecha_modificacion': row[8],
                    'usuario_modificacion': row[9]
                }
                configuraciones.append(config)
            
            # Actualizar cache
            self.configuraciones_cache = {c['clave']: c['valor'] for c in configuraciones}
            
            logger.debug(f"Obtenidas {len(configuraciones)} configuraciones")
            return configuraciones
            
        except Exception as e:
            logger.error(f"Error obteniendo configuraciones: {e}")
            return self._obtener_configuraciones_demo()
    
    def obtener_configuraciones_filtradas(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtiene configuraciones aplicando filtros.
        
        Args:
            filtros: Diccionario con filtros a aplicar
            
        Returns:
            Lista de configuraciones filtradas
        """
        try:
            if not self.db_connection:
                logger.warning("BD no disponible, usando datos demo")
                configuraciones_demo = self._obtener_configuraciones_demo()
                return self._aplicar_filtros_demo(configuraciones_demo, filtros)
            
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT id, clave, valor, tipo, categoria, descripcion, 
                       es_editable, fecha_creacion, fecha_modificacion, 
                       usuario_modificacion
                FROM configuraciones 
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros
            if filtros.get('categoria'):
                query += " AND categoria = ?"
                params.append(filtros['categoria'])
            
            if filtros.get('clave'):
                query += " AND clave LIKE ?"
                params.append(f"%{filtros['clave']}%")
            
            if filtros.get('es_editable') is not None:
                query += " AND es_editable = ?"
                params.append(filtros['es_editable'])
            
            query += " ORDER BY categoria, clave"
            
            cursor.execute(query, params)
            
            configuraciones = []
            for row in cursor.fetchall():
                config = {
                    'id': row[0],
                    'clave': row[1],
                    'valor': row[2],
                    'tipo': row[3],
                    'categoria': row[4],
                    'descripcion': row[5],
                    'es_editable': bool(row[6]),
                    'fecha_creacion': row[7],
                    'fecha_modificacion': row[8],
                    'usuario_modificacion': row[9]
                }
                configuraciones.append(config)
            
            logger.debug(f"Filtradas {len(configuraciones)} configuraciones")
            return configuraciones
            
        except Exception as e:
            logger.error(f"Error filtrando configuraciones: {e}")
            return []
    
    def obtener_valor_configuracion(self, clave: str) -> Optional[str]:
        """
        Obtiene el valor de una configuración específica.
        
        Args:
            clave: Clave de la configuración
            
        Returns:
            Valor de la configuración o None
        """
        try:
            # Usar cache si está disponible
            if clave in self.configuraciones_cache:
                return self.configuraciones_cache[clave]
            
            if not self.db_connection:
                return self._obtener_valor_demo(clave)
            
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT valor FROM configuraciones WHERE clave = ?", 
                (clave,)
            )
            
            result = cursor.fetchone()
            if result:
                valor = result[0]
                self.configuraciones_cache[clave] = valor
                return valor
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo valor de configuración '{clave}': {e}")
            return None
    
    def crear_configuracion(self, datos_config: Dict[str, Any]) -> bool:
        """
        Crea una nueva configuración.
        
        Args:
            datos_config: Datos de la configuración
            
        Returns:
            True si se creó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO configuraciones 
                (clave, valor, tipo, categoria, descripcion, es_editable, usuario_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datos_config.get('clave'),
                datos_config.get('valor'),
                datos_config.get('tipo', 'string'),
                datos_config.get('categoria', 'general'),
                datos_config.get('descripcion', ''),
                datos_config.get('es_editable', True),
                datos_config.get('usuario_modificacion', 'SISTEMA')
            ))
            
            self.db_connection.commit()
            
            # Limpiar cache
            self.configuraciones_cache.clear()
            
            logger.info(f"Configuración '{datos_config.get('clave')}' creada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando configuración: {e}")
            return False
    
    def actualizar_configuracion(self, config_id: int, datos_config: Dict[str, Any]) -> bool:
        """
        Actualiza una configuración existente.
        
        Args:
            config_id: ID de la configuración
            datos_config: Nuevos datos de la configuración
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE configuraciones 
                SET valor = ?, tipo = ?, categoria = ?, descripcion = ?, 
                    es_editable = ?, fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = ?
                WHERE id = ?
            """, (
                datos_config.get('valor'),
                datos_config.get('tipo', 'string'),
                datos_config.get('categoria', 'general'),
                datos_config.get('descripcion', ''),
                datos_config.get('es_editable', True),
                datos_config.get('usuario_modificacion', 'SISTEMA'),
                config_id
            ))
            
            self.db_connection.commit()
            
            # Limpiar cache
            self.configuraciones_cache.clear()
            
            logger.info(f"Configuración ID {config_id} actualizada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}")
            return False
    
    def eliminar_configuracion(self, config_id: int) -> bool:
        """
        Elimina una configuración.
        
        Args:
            config_id: ID de la configuración
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM configuraciones WHERE id = ? AND es_editable = 1", (config_id,))
            self.db_connection.commit()
            
            # Limpiar cache
            self.configuraciones_cache.clear()
            
            logger.info(f"Configuración ID {config_id} eliminada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando configuración: {e}")
            return False
    
    def _obtener_configuraciones_demo(self) -> List[Dict[str, Any]]:
        """Datos demo para cuando no hay BD disponible."""
        return [
            {
                'id': 1,
                'clave': 'empresa_nombre',
                'valor': 'Rexus.app Demo',
                'tipo': 'string',
                'categoria': 'empresa',
                'descripcion': 'Nombre de la empresa',
                'es_editable': True,
                'fecha_creacion': '2025-08-24',
                'fecha_modificacion': '2025-08-24',
                'usuario_modificacion': 'SISTEMA'
            },
            {
                'id': 2,
                'clave': 'sistema_tema',
                'valor': 'light',
                'tipo': 'string',
                'categoria': 'sistema',
                'descripcion': 'Tema del sistema',
                'es_editable': True,
                'fecha_creacion': '2025-08-24',
                'fecha_modificacion': '2025-08-24',
                'usuario_modificacion': 'SISTEMA'
            }
        ]
    
    def _aplicar_filtros_demo(self, configuraciones: List[Dict], filtros: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros a los datos demo."""
        resultado = configuraciones.copy()
        
        if filtros.get('categoria'):
            resultado = [c for c in resultado if c['categoria'] == filtros['categoria']]
        
        if filtros.get('clave'):
            clave_filtro = filtros['clave'].lower()
            resultado = [c for c in resultado if clave_filtro in c['clave'].lower()]
        
        return resultado
    
    def _obtener_valor_demo(self, clave: str) -> Optional[str]:
        """Obtiene valor demo para una clave específica."""
        valores_demo = {
            'empresa_nombre': 'Rexus.app Demo',
            'sistema_tema': 'light',
            'sistema_idioma': 'es'
        }
        return valores_demo.get(clave)