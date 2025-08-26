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

import logging
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, filename):
            script_name = filename
            return self.sql_loader.load_script(script_name)

class ConfiguracionModel:
    ORDER_BY_CLAUSE = "ORDER BY categoria, clave"
    NO_DB_CONNECTION_MSG = "No hay conexión a BD disponible"

    """Modelo para gestionar configuraciones del sistema."""

    def __init__(self, db_connection=None):
        """
        Inicializar modelo de configuración.

        Args:
        db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.configuraciones_cache = {}
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'configuracion'
        logger.info("ConfiguracionModel inicializado")

    def verificar_configuracion(self):
        """Verifica que las tablas de configuración existan."""
        if not self.db_connection:
            logger.error(self.NO_DB_CONNECTION_MSG)
            return False
        try:
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query('verificar_configuracion')
            cursor.execute(query)
            return True
        except Exception as e:
            logger.error(f"Error verificando configuración: {e}")
            return False

    def crear_configuraciones_default(self):
        """Crea configuraciones por defecto si no existen"""
        try:
            self._insertar_configuraciones_default()
            logger.debug("Tablas de configuración creadas exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error creando configuraciones default: {e}")
            return False

    def _insertar_configuraciones_default(self):
        """Inserta configuraciones por defecto del sistema."""
        if not self.db_connection:
            logger.error(self.NO_DB_CONNECTION_MSG)
            return
        try:
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query('insert_configuraciones_default')
            cursor.execute(query)
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
            query = self.sql_manager.get_query('select_configuraciones_all')
            cursor.execute(query)

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
            base_query = self.sql_manager.get_query('select_configuraciones_filtered')

            if not base_query:
                logger.error("No se pudo cargar query de configuraciones filtradas")
                return []

            query = base_query
            params = []

            # Aplicar filtros modificando la query
            if filtros.get('categoria'):
                query = query.replace(self.ORDER_BY_CLAUSE, "AND categoria = ? " + self.ORDER_BY_CLAUSE)
                params.append(filtros['categoria'])

            if filtros.get('clave'):
                query = query.replace(self.ORDER_BY_CLAUSE, "AND clave LIKE ? " + self.ORDER_BY_CLAUSE)
                params.append(f"%{filtros['clave']}%")

            if filtros.get('es_editable') is not None:
                query = query.replace(self.ORDER_BY_CLAUSE, "AND es_editable = ? " + self.ORDER_BY_CLAUSE)
                params.append(filtros['es_editable'])

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
            query = self.sql_manager.get_query('select_valor_by_clave')
            cursor.execute(query, {'clave': clave})

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
                logger.error(self.NO_DB_CONNECTION_MSG)
                return False

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query('insert_configuracion')
            cursor.execute(query, {
                'clave': datos_config.get('clave'),
                'valor': datos_config.get('valor'),
                'tipo': datos_config.get('tipo', 'string'),
                'categoria': datos_config.get('categoria', 'general'),
                'descripcion': datos_config.get('descripcion', ''),
                'es_editable': datos_config.get('es_editable', True),
                'usuario_modificacion': datos_config.get('usuario_modificacion', 'SISTEMA')
            })

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
                logger.error(self.NO_DB_CONNECTION_MSG)
                return False

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query('update_configuracion_by_id')
            cursor.execute(query, {
                'valor': datos_config.get('valor'),
                'tipo': datos_config.get('tipo', 'string'),
                'categoria': datos_config.get('categoria', 'general'),
                'descripcion': datos_config.get('descripcion', ''),
                'es_editable': datos_config.get('es_editable', True),
                'usuario_modificacion': datos_config.get('usuario_modificacion', 'SISTEMA'),
                'config_id': config_id
            })

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
                logger.error(self.NO_DB_CONNECTION_MSG)
                return False

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query('delete_configuracion')
            cursor.execute(query, {'config_id': config_id})
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