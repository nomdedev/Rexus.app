"""
Modelo de Mantenimiento - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para mantenimiento.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)

class MantenimientoModel:
    """Modelo para el módulo de mantenimiento."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de mantenimiento."""
        self.db_connection = db_connection
        self.logger = logger
        
    def obtener_estado_equipos(self) -> Dict[str, Any]:
        """Obtiene el estado general de los equipos."""
        try:
            if not self.db_connection:
                return {
                    'estado_general': 'Desconocido',
                    'color_estado': 'gray',
                    'total_equipos': 0,
                    'equipos_operativos': 0,
                    'equipos_criticos': 0,
                    'porcentaje_operativo': 0
                }
                
            cursor = self.db_connection.cursor()
            
            # Obtener totales
            cursor.execute("SELECT COUNT(*) FROM equipos")
            total_equipos = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM equipos WHERE estado = 'operativo'")
            equipos_operativos = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM equipos WHERE estado = 'critico'")
            equipos_criticos = cursor.fetchone()[0] or 0
            
            # Calcular estado general
            if total_equipos == 0:
                estado_general = "Sin equipos"
                color_estado = "gray"
            elif equipos_criticos > 0:
                estado_general = "Crítico"
                color_estado = "red"
            elif equipos_operativos / total_equipos >= 0.8:
                estado_general = "Bueno"
                color_estado = "green"
            else:
                estado_general = "Regular"
                color_estado = "yellow"
                
            return {
                'estado_general': estado_general,
                'color_estado': color_estado,
                'total_equipos': total_equipos,
                'equipos_operativos': equipos_operativos,
                'equipos_criticos': equipos_criticos,
                'porcentaje_operativo': round((equipos_operativos / total_equipos * 100) if total_equipos > 0 else 100, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de equipos: {e}")
            return {
                'estado_general': 'Error',
                'color_estado': 'red',
                'total_equipos': 0,
                'equipos_operativos': 0,
                'equipos_criticos': 0,
                'porcentaje_operativo': 0
            }

    def obtener_todos_equipos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los equipos."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, nombre, tipo, estado, ubicacion, fecha_instalacion, ultimo_mantenimiento
                FROM equipos 
                ORDER BY nombre
            """)
            
            equipos = []
            for row in cursor.fetchall():
                equipos.append({
                    'id': row[0],
                    'nombre': row[1],
                    'tipo': row[2],
                    'estado': row[3],
                    'ubicacion': row[4],
                    'fecha_instalacion': row[5],
                    'ultimo_mantenimiento': row[6]
                })
            
            return equipos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo equipos: {e}")
            return []

    def crear_equipo(self, datos: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo equipo."""
        try:
            if not self.db_connection:
                return None
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO equipos (nombre, tipo, estado, ubicacion, fecha_instalacion)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datos.get('nombre'),
                datos.get('tipo'),
                datos.get('estado', 'operativo'),
                datos.get('ubicacion'),
                datos.get('fecha_instalacion', date.today().isoformat())
            ))
            
            equipo_id = cursor.lastrowid
            self.db_connection.commit()
            self.logger.info(f"Equipo creado exitosamente: {equipo_id}")
            return equipo_id
            
        except Exception as e:
            self.logger.error(f"Error creando equipo: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def programar_mantenimiento(self, equipo_id: int, fecha_programada: str, tipo: str, observaciones: str = "") -> bool:
        """Programa un mantenimiento."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO mantenimientos_programados (equipo_id, fecha_programada, tipo, observaciones, estado)
                VALUES (?, ?, ?, ?, 'programado')
            """, (equipo_id, fecha_programada, tipo, observaciones))
            
            self.db_connection.commit()
            self.logger.info(f"Mantenimiento programado para equipo {equipo_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error programando mantenimiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def ejecutar_mantenimiento(self, programacion_id: int, datos_ejecucion: Dict[str, Any]) -> bool:
        """Ejecuta un mantenimiento programado."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            
            # Actualizar la programación
            cursor.execute("""
                UPDATE mantenimientos_programados 
                SET estado = 'ejecutado', fecha_ejecucion = ?, observaciones_ejecucion = ?
                WHERE id = ?
            """, (
                datos_ejecucion.get('fecha_ejecucion', date.today().isoformat()),
                datos_ejecucion.get('observaciones', ''),
                programacion_id
            ))
            
            # Obtener el equipo_id
            cursor.execute("SELECT equipo_id FROM mantenimientos_programados WHERE id = ?", (programacion_id,))
            row = cursor.fetchone()
            if row:
                equipo_id = row[0]
                # Actualizar fecha de último mantenimiento del equipo
                cursor.execute("""
                    UPDATE equipos 
                    SET ultimo_mantenimiento = ? 
                    WHERE id = ?
                """, (datos_ejecucion.get('fecha_ejecucion', date.today().isoformat()), equipo_id))
            
            self.db_connection.commit()
            self.logger.info(f"Mantenimiento ejecutado: {programacion_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando mantenimiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_historial_mantenimiento(self, equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene el historial de mantenimientos."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            
            if equipo_id:
                cursor.execute("""
                    SELECT mp.id, mp.equipo_id, e.nombre, mp.tipo, mp.fecha_programada, 
                           mp.fecha_ejecucion, mp.estado, mp.observaciones
                    FROM mantenimientos_programados mp
                    JOIN equipos e ON mp.equipo_id = e.id
                    WHERE mp.equipo_id = ?
                    ORDER BY mp.fecha_programada DESC
                """, (equipo_id,))
            else:
                cursor.execute("""
                    SELECT mp.id, mp.equipo_id, e.nombre, mp.tipo, mp.fecha_programada, 
                           mp.fecha_ejecucion, mp.estado, mp.observaciones
                    FROM mantenimientos_programados mp
                    JOIN equipos e ON mp.equipo_id = e.id
                    ORDER BY mp.fecha_programada DESC
                """)
            
            historial = []
            for row in cursor.fetchall():
                historial.append({
                    'id': row[0],
                    'equipo_id': row[1],
                    'equipo_nombre': row[2],
                    'tipo': row[3],
                    'fecha_programada': row[4],
                    'fecha_ejecucion': row[5],
                    'estado': row[6],
                    'observaciones': row[7]
                })
            
            return historial
            
        except Exception as e:
            self.logger.error(f"Error obteniendo historial: {e}")
            return []
