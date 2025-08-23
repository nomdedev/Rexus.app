# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Auditoría - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de auditoría.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import os
import sys
                            return self._get_logs_demo()
                
            cursor = self.db_connection.cursor()
            
            # Query base para obtener logs
            query = """
            SELECT TOP (?) 
                id,
                fecha,
                nivel_criticidad,
                accion,
                descripcion,
                usuario,
                detalles
            FROM auditoria_log
            WHERE 1=1
            """
            
            params = [limite]
            
            # Agregar filtros si se proporcionan
            if filtros:
                if filtros.get('usuario'):
                    query += " AND usuario LIKE ?"
                    params.append(f"%{filtros['usuario']}%")
                if filtros.get('accion'):
                    query += " AND accion LIKE ?"
                    params.append(f"%{filtros['accion']}%")
                if filtros.get('nivel'):
                    query += " AND nivel_criticidad = ?"
                    params.append(filtros['nivel'])
                    
            query += " ORDER BY fecha DESC"
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                log = {
                    'id': row[0],
                    'fecha': row[1],
                    'nivel_criticidad': row[2],
                    'accion': row[3],
                    'descripcion': row[4],
                    'usuario': row[5],
                    'detalles': row[6]
                }
                logs.append(log)
                
            return logs
            
        except Exception as e:
            
    def _get_logs_demo(self):
        """Datos demo para logs cuando no hay conexión o tabla"""
        from datetime import datetime, timedelta
        
        return [
            {
                'id': 1,
                'fecha': datetime.now() - timedelta(hours=1),
                'nivel_criticidad': 'INFO',
                'accion': 'LOGIN',
                'descripcion': 'Usuario inició sesión',
                'usuario': 'demo_user',
                'detalles': 'Sesión demo iniciada correctamente'
            },
            {
                'id': 2,
                'fecha': datetime.now() - timedelta(hours=2),
                'nivel_criticidad': 'WARNING',
                'accion': 'CONEXION_BD',
                'descripcion': 'Intento de conexión fallido',
                'usuario': 'sistema',
                'detalles': 'Error de conectividad temporal'
            }
        ]
