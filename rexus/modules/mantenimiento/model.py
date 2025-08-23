# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Mantenimiento

Maneja la lógica de negocio para:
- Mantenimiento preventivo
- Mantenimiento correctivo
- Historial de mantenimientos
- Programación de mantenimientos
- Gestión de equipos y herramientas
"""

# Importar utilidades de sanitización
import os

                        
            return {
                'estado_general': estado_general,
                'color_estado': color_estado,
                'total_equipos': total_equipos,
                'equipos_operativos': equipos_operativos,
                'equipos_criticos': equipos_criticos,
                'porcentaje_operativo': round((equipos_operativos / total_equipos * 100) if total_equipos > 0 else 100, 1),
                'tareas_pendientes': estadisticas.get('pendientes', 0),
                'tareas_completadas': estadisticas.get('completadas', 0),
                'ultima_actualizacion': self._get_timestamp(),
                'alertas_activas': equipos_criticos,
                'recomendaciones': self._get_recomendaciones_estado(equipos_criticos, total_equipos)
            }
            
        except Exception as e:
            return {
                'estado_general': 'DESCONOCIDO',
                'color_estado': 'gray',
                'error': str(e),
                'total_equipos': 0,
                'equipos_operativos': 0,
                'equipos_criticos': 0,
                'ultima_actualizacion': self._get_timestamp()
            }
    
    def _get_timestamp(self):
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_recomendaciones_estado(self, criticos, total):
        """Genera recomendaciones basadas en el estado"""
        recomendaciones = []
        
        if criticos == 0:
            recomendaciones.append("Sistema funcionando óptimamente")
        elif criticos <= total * 0.1:
            recomendaciones.append("Revisar equipos en estado crítico")
        elif criticos <= total * 0.3:
            recomendaciones.append("Implementar mantenimiento preventivo urgente")
        else:
            recomendaciones.append("Requiere intervención inmediata del equipo técnico")
            recomendaciones.append("Considerar parada programada para mantenimiento")
        
        return recomendaciones
