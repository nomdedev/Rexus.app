"""
Modelo de Programación de Mantenimiento

Maneja la programación automática y calendario de mantenimientos.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ProgramacionMantenimientoModel:
    """Modelo para programación de mantenimientos."""
    
    def __init__(self, db_connection=None):
        """Inicializar modelo de programación."""
        self.db_connection = db_connection
        
        # Configuración de prioridades
        self.prioridades = {
            'critico': {
                'color': '#FF0000',
                'dias_alerta': 1
            },
            'alto': {
                'color': '#FF8800',
                'dias_alerta': 3
            },
            'normal': {
                'color': '#00AA00',
                'dias_alerta': 7
            }
        }
        
        # Contadores de estado
        self.contadores = {
            'total': 0,
            'completados': 0,
            'pendientes': 0,
            'vencidos': 0,
            'proximos_7_dias': 0,
            'proximos_30_dias': 0
        }

    def obtener_mantenimientos_vencidos(self) -> List[Dict]:
        """Obtiene mantenimientos vencidos."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    m.id,
                    m.equipo_id,
                    e.nombre as equipo_nombre,
                    m.descripcion,
                    m.fecha_programada,
                    m.prioridad,
                    DATEDIFF(DAY, m.fecha_programada, GETDATE()) as dias_vencido
                FROM mantenimientos m
                INNER JOIN equipos e ON m.equipo_id = e.id
                WHERE m.estado = 'PENDIENTE'
                AND m.fecha_programada < GETDATE()
                ORDER BY m.fecha_programada ASC
            """)
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error obteniendo mantenimientos vencidos: {e}")
            return []
    
    def obtener_mantenimientos_proximos(self, dias: int = 7) -> List[Dict]:
        """Obtiene mantenimientos próximos en N días."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            fecha_limite = datetime.now() + timedelta(days=dias)
            
            cursor.execute("""
                SELECT 
                    m.id,
                    m.equipo_id,
                    e.nombre as equipo_nombre,
                    m.descripcion,
                    m.fecha_programada,
                    m.prioridad,
                    DATEDIFF(DAY, GETDATE(), m.fecha_programada) as dias_restantes
                FROM mantenimientos m
                INNER JOIN equipos e ON m.equipo_id = e.id
                WHERE m.estado = 'PENDIENTE'
                AND m.fecha_programada BETWEEN GETDATE() AND ?
                ORDER BY m.fecha_programada ASC
            """, (fecha_limite,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error obteniendo mantenimientos próximos: {e}")
            return []
    
    def programar_mantenimiento(self, datos: Dict[str, Any]) -> bool:
        """Programar nuevo mantenimiento."""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO mantenimientos (
                    equipo_id, descripcion, fecha_programada,
                    prioridad, tipo, usuario_asignado, estado,
                    fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, 'PENDIENTE', GETDATE())
            """, (
                datos.get('equipo_id'),
                datos.get('descripcion'),
                datos.get('fecha_programada'),
                datos.get('prioridad', 'normal'),
                datos.get('tipo', 'preventivo'),
                datos.get('usuario_asignado')
            ))
            
            self.db_connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error programando mantenimiento: {e}")
            return False
    
    def actualizar_contadores(self) -> Dict[str, int]:
        """Actualizar contadores de estado."""
        if not self.db_connection:
            return self.contadores
        
        try:
            cursor = self.db_connection.cursor()
            
            # Total de mantenimientos
            cursor.execute("SELECT COUNT(*) FROM mantenimientos")
            self.contadores['total'] = cursor.fetchone()[0]
            
            # Completados
            cursor.execute("SELECT COUNT(*) FROM mantenimientos WHERE estado = 'COMPLETADO'")
            self.contadores['completados'] = cursor.fetchone()[0]
            
            # Pendientes
            cursor.execute("SELECT COUNT(*) FROM mantenimientos WHERE estado = 'PENDIENTE'")
            self.contadores['pendientes'] = cursor.fetchone()[0]
            
            # Vencidos
            cursor.execute("""
                SELECT COUNT(*) FROM mantenimientos 
                WHERE estado = 'PENDIENTE' AND fecha_programada < GETDATE()
            """)
            self.contadores['vencidos'] = cursor.fetchone()[0]
            
            # Próximos 7 días
            cursor.execute("""
                SELECT COUNT(*) FROM mantenimientos 
                WHERE estado = 'PENDIENTE' 
                AND fecha_programada BETWEEN GETDATE() AND DATEADD(DAY, 7, GETDATE())
            """)
            self.contadores['proximos_7_dias'] = cursor.fetchone()[0]
            
            # Próximos 30 días
            cursor.execute("""
                SELECT COUNT(*) FROM mantenimientos 
                WHERE estado = 'PENDIENTE' 
                AND fecha_programada BETWEEN GETDATE() AND DATEADD(DAY, 30, GETDATE())
            """)
            self.contadores['proximos_30_dias'] = cursor.fetchone()[0]
            
            return self.contadores
            
        except Exception as e:
            logger.error(f"Error actualizando contadores: {e}")
            return self.contadores