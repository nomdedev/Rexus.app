"""
Modelo de Auditoría - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de auditoría.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar utilidades de sanitización
try:
    from ...utils.data_sanitizer import sanitize_string, validate_input
    SANITIZER_AVAILABLE = True
except ImportError:
    logger.warning("Sanitizador no disponible, usando métodos básicos")
    SANITIZER_AVAILABLE = False
    
    def sanitize_string(s):
        return str(s).replace("'", "''").replace(";", "") if s else ""
    
    def validate_input(s, input_type="string"):
        return bool(s and len(str(s)) < 1000)


class AuditoriaModel:
    """Modelo para gestionar el sistema de auditoría."""
    
    def __init__(self, db_connection=None):
        """
        Inicializar modelo de auditoría.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("AuditoriaModel inicializado")
    
    def crear_tablas(self):
        """Crea las tablas necesarias para auditoría."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            
            # Tabla principal de auditoría
            create_audit_table = """
                CREATE TABLE IF NOT EXISTS auditoria_eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    modulo TEXT NOT NULL,
                    tabla_afectada TEXT,
                    registro_id TEXT,
                    datos_anteriores TEXT,
                    datos_nuevos TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    resultado TEXT,
                    detalles TEXT,
                    nivel_riesgo TEXT DEFAULT 'NORMAL',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            cursor.execute(create_audit_table)
            
            # Tabla de configuración de auditoría
            create_config_table = """
                CREATE TABLE IF NOT EXISTS auditoria_configuracion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modulo TEXT NOT NULL,
                    tabla TEXT NOT NULL,
                    auditoria_activa BOOLEAN DEFAULT 1,
                    auditoria_inserts BOOLEAN DEFAULT 1,
                    auditoria_updates BOOLEAN DEFAULT 1,
                    auditoria_deletes BOOLEAN DEFAULT 1,
                    retencion_dias INTEGER DEFAULT 365,
                    nivel_detalle TEXT DEFAULT 'COMPLETO',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            cursor.execute(create_config_table)
            
            # Índices para optimizar consultas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_timestamp ON auditoria_eventos(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria_eventos(usuario)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_modulo ON auditoria_eventos(modulo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria_eventos(accion)")
            
            self.db_connection.commit()
            
            # Insertar configuraciones por defecto
            self._insertar_configuraciones_default()
            
            logger.debug("Tablas de auditoría creadas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tablas de auditoría: {e}")
            return False
    
    def _insertar_configuraciones_default(self):
        """Inserta configuraciones por defecto de auditoría."""
        try:
            cursor = self.db_connection.cursor()
            
            configuraciones_default = [
                ('usuarios', 'usuarios', 1, 1, 1, 1, 365, 'COMPLETO'),
                ('inventario', 'productos', 1, 1, 1, 1, 180, 'COMPLETO'),
                ('compras', 'compras', 1, 1, 1, 0, 180, 'BASICO'),
                ('obras', 'obras', 1, 1, 1, 0, 365, 'COMPLETO'),
                ('configuracion', 'configuraciones', 1, 1, 1, 0, 730, 'COMPLETO')
            ]
            
            for config in configuraciones_default:
                cursor.execute("""
                    INSERT OR IGNORE INTO auditoria_configuracion 
                    (modulo, tabla, auditoria_activa, auditoria_inserts, 
                     auditoria_updates, auditoria_deletes, retencion_dias, nivel_detalle) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, config)
            
            self.db_connection.commit()
            logger.debug("Configuraciones de auditoría insertadas")
            
        except Exception as e:
            logger.error(f"Error insertando configuraciones de auditoría: {e}")
    
    def registrar_evento(self, usuario: str, accion: str, modulo: str, 
                        tabla_afectada: str = None, registro_id: str = None,
                        datos_anteriores: Dict = None, datos_nuevos: Dict = None,
                        detalles: str = None, nivel_riesgo: str = "NORMAL",
                        ip_address: str = None, user_agent: str = None) -> bool:
        """
        Registra un evento de auditoría.
        
        Args:
            usuario: Usuario que realiza la acción
            accion: Acción realizada (CREATE, UPDATE, DELETE, LOGIN, etc.)
            modulo: Módulo donde se realiza la acción
            tabla_afectada: Tabla afectada por la acción
            registro_id: ID del registro afectado
            datos_anteriores: Datos antes del cambio
            datos_nuevos: Datos después del cambio
            detalles: Detalles adicionales
            nivel_riesgo: Nivel de riesgo (BAJO, NORMAL, ALTO, CRÍTICO)
            ip_address: Dirección IP del usuario
            user_agent: User agent del navegador
            
        Returns:
            True si se registró exitosamente
        """
        try:
            # Validar y sanitizar entradas
            usuario = sanitize_string(usuario) if usuario else "SISTEMA"
            accion = sanitize_string(accion) if accion else "UNKNOWN"
            modulo = sanitize_string(modulo) if modulo else "UNKNOWN"
            
            if not validate_input(usuario) or not validate_input(accion):
                logger.error("Datos de auditoría inválidos")
                return False
            
            if not self.db_connection:
                # Fallback a log si no hay BD
                logger.info(f"AUDITORIA: {usuario} - {accion} - {modulo}")
                return True
            
            # Verificar si la auditoría está activa para este módulo
            if not self._esta_auditoria_activa(modulo, tabla_afectada, accion):
                return True  # No registrar, pero no es error
            
            cursor = self.db_connection.cursor()
            
            # Convertir datos a JSON
            datos_ant_json = json.dumps(datos_anteriores) if datos_anteriores else None
            datos_new_json = json.dumps(datos_nuevos) if datos_nuevos else None
            
            cursor.execute("""
                INSERT INTO auditoria_eventos 
                (usuario, accion, modulo, tabla_afectada, registro_id, 
                 datos_anteriores, datos_nuevos, detalles, nivel_riesgo,
                 ip_address, user_agent, resultado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario, accion, modulo, tabla_afectada, registro_id,
                datos_ant_json, datos_new_json, detalles, nivel_riesgo,
                ip_address, user_agent, "SUCCESS"
            ))
            
            self.db_connection.commit()
            
            # Log crítico para eventos de alto riesgo
            if nivel_riesgo in ["ALTO", "CRÍTICO"]:
                logger.warning(f"EVENTO CRÍTICO: {usuario} - {accion} - {modulo} - {detalles}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error registrando evento de auditoría: {e}")
            return False
    
    def obtener_eventos(self, filtros: Dict[str, Any] = None, 
                       limite: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene eventos de auditoría con filtros.
        
        Args:
            filtros: Filtros a aplicar
            limite: Número máximo de registros
            offset: Desplazamiento para paginación
            
        Returns:
            Lista de eventos de auditoría
        """
        try:
            if not self.db_connection:
                logger.warning("BD no disponible, usando datos demo")
                return self._obtener_eventos_demo()
            
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT id, timestamp, usuario, accion, modulo, tabla_afectada,
                       registro_id, datos_anteriores, datos_nuevos, detalles,
                       nivel_riesgo, ip_address, user_agent, resultado
                FROM auditoria_eventos 
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros
            if filtros:
                if filtros.get('usuario'):
                    query += " AND usuario LIKE ?"
                    params.append(f"%{sanitize_string(filtros['usuario'])}%")
                
                if filtros.get('modulo'):
                    query += " AND modulo = ?"
                    params.append(sanitize_string(filtros['modulo']))
                
                if filtros.get('accion'):
                    query += " AND accion = ?"
                    params.append(sanitize_string(filtros['accion']))
                
                if filtros.get('fecha_desde'):
                    query += " AND timestamp >= ?"
                    params.append(filtros['fecha_desde'])
                
                if filtros.get('fecha_hasta'):
                    query += " AND timestamp <= ?"
                    params.append(filtros['fecha_hasta'])
                
                if filtros.get('nivel_riesgo'):
                    query += " AND nivel_riesgo = ?"
                    params.append(filtros['nivel_riesgo'])
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            
            eventos = []
            for row in cursor.fetchall():
                evento = {
                    'id': row[0],
                    'timestamp': row[1],
                    'usuario': row[2],
                    'accion': row[3],
                    'modulo': row[4],
                    'tabla_afectada': row[5],
                    'registro_id': row[6],
                    'datos_anteriores': json.loads(row[7]) if row[7] else None,
                    'datos_nuevos': json.loads(row[8]) if row[8] else None,
                    'detalles': row[9],
                    'nivel_riesgo': row[10],
                    'ip_address': row[11],
                    'user_agent': row[12],
                    'resultado': row[13]
                }
                eventos.append(evento)
            
            logger.debug(f"Obtenidos {len(eventos)} eventos de auditoría")
            return eventos
            
        except Exception as e:
            logger.error(f"Error obteniendo eventos de auditoría: {e}")
            return self._obtener_eventos_demo()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de auditoría.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            if not self.db_connection:
                return self._obtener_estadisticas_demo()
            
            cursor = self.db_connection.cursor()
            
            # Total de eventos
            cursor.execute("SELECT COUNT(*) FROM auditoria_eventos")
            total_eventos = cursor.fetchone()[0]
            
            # Eventos por módulo
            cursor.execute("""
                SELECT modulo, COUNT(*) as count 
                FROM auditoria_eventos 
                GROUP BY modulo 
                ORDER BY count DESC
            """)
            eventos_por_modulo = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Eventos por usuario
            cursor.execute("""
                SELECT usuario, COUNT(*) as count 
                FROM auditoria_eventos 
                GROUP BY usuario 
                ORDER BY count DESC 
                LIMIT 10
            """)
            eventos_por_usuario = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Eventos de alto riesgo recientes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM auditoria_eventos 
                WHERE nivel_riesgo IN ('ALTO', 'CRÍTICO')
                AND timestamp >= datetime('now', '-7 days')
            """)
            eventos_criticos_recientes = cursor.fetchone()[0]
            
            # Eventos del día actual
            cursor.execute("""
                SELECT COUNT(*) 
                FROM auditoria_eventos 
                WHERE DATE(timestamp) = DATE('now')
            """)
            eventos_hoy = cursor.fetchone()[0]
            
            estadisticas = {
                'total_eventos': total_eventos,
                'eventos_hoy': eventos_hoy,
                'eventos_criticos_recientes': eventos_criticos_recientes,
                'eventos_por_modulo': eventos_por_modulo,
                'eventos_por_usuario': eventos_por_usuario,
                'ultima_actualizacion': datetime.datetime.now().isoformat()
            }
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de auditoría: {e}")
            return self._obtener_estadisticas_demo()
    
    def limpiar_eventos_antiguos(self, dias_retencion: int = None) -> int:
        """
        Limpia eventos antiguos según la política de retención.
        
        Args:
            dias_retencion: Días de retención (usa configuración si no se especifica)
            
        Returns:
            Número de eventos eliminados
        """
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a BD para limpieza")
                return 0
            
            if dias_retencion is None:
                # Usar configuración por defecto
                dias_retencion = 365
            
            cursor = self.db_connection.cursor()
            
            # Eliminar eventos antiguos
            cursor.execute("""
                DELETE FROM auditoria_eventos 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(dias_retencion))
            
            eliminados = cursor.rowcount
            self.db_connection.commit()
            
            logger.info(f"Eliminados {eliminados} eventos de auditoría antiguos")
            return eliminados
            
        except Exception as e:
            logger.error(f"Error limpiando eventos antiguos: {e}")
            return 0
    
    def _esta_auditoria_activa(self, modulo: str, tabla: str, accion: str) -> bool:
        """Verifica si la auditoría está activa para un módulo/tabla/acción."""
        try:
            if not self.db_connection:
                return True  # Por defecto auditar si no hay config
            
            cursor = self.db_connection.cursor()
            
            cursor.execute("""
                SELECT auditoria_activa, auditoria_inserts, auditoria_updates, auditoria_deletes
                FROM auditoria_configuracion 
                WHERE modulo = ? AND tabla = ?
            """, (modulo, tabla or modulo))
            
            result = cursor.fetchone()
            if not result:
                return True  # Auditar si no hay configuración específica
            
            auditoria_activa, inserts, updates, deletes = result
            
            if not auditoria_activa:
                return False
            
            # Verificar tipo de acción
            if accion.upper() in ['CREATE', 'INSERT'] and not inserts:
                return False
            elif accion.upper() in ['UPDATE', 'MODIFY'] and not updates:
                return False
            elif accion.upper() in ['DELETE', 'REMOVE'] and not deletes:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando configuración de auditoría: {e}")
            return True
    
    def _obtener_eventos_demo(self) -> List[Dict[str, Any]]:
        """Datos demo para cuando no hay BD disponible."""
        return [
            {
                'id': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'usuario': 'SISTEMA',
                'accion': 'LOGIN',
                'modulo': 'USUARIOS',
                'tabla_afectada': 'usuarios',
                'registro_id': '1',
                'datos_anteriores': None,
                'datos_nuevos': {'status': 'logged_in'},
                'detalles': 'Inicio de sesión exitoso',
                'nivel_riesgo': 'NORMAL',
                'ip_address': '127.0.0.1',
                'user_agent': 'Rexus App',
                'resultado': 'SUCCESS'
            }
        ]
    
    def _obtener_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo para cuando no hay BD disponible."""
        return {
            'total_eventos': 150,
            'eventos_hoy': 25,
            'eventos_criticos_recientes': 3,
            'eventos_por_modulo': {
                'USUARIOS': 45,
                'INVENTARIO': 35,
                'OBRAS': 30,
                'COMPRAS': 25,
                'CONFIGURACION': 15
            },
            'eventos_por_usuario': {
                'SISTEMA': 50,
                'admin': 35,
                'operador1': 25,
                'manager': 15
            },
            'ultima_actualizacion': datetime.datetime.now().isoformat()
        }