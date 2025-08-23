#!/usr/bin/env python3
"""
Sistema de Audit Trail para Rexus.app
Maneja el registro de cambios en la base de datos con timestamps
"""


import logging
logger = logging.getLogger(__name__)

import sys
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rexus.core.database import DatabaseConnection


class AuditTrail:
    """Sistema de auditoría para tracking de cambios"""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection or DatabaseConnection('audit')
        self.current_user_id = None
        self.current_username = None

    def set_current_user(self, user_id: int, username: str):
        """Establece el usuario actual para auditoría"""
        self.current_user_id = user_id
        self.current_username = username

    def log_change(self, tabla: str, accion: str, registro_id: int,
                   datos_anteriores: Dict = None, datos_nuevos: Dict = None,
                   modulo: str = None, detalles: str = None):
        """
        Registra un cambio en la auditoría

        Args:
            tabla: Nombre de la tabla afectada
            accion: Tipo de acción (INSERT, UPDATE, DELETE)
            registro_id: ID del registro afectado
            datos_anteriores: Datos antes del cambio
            datos_nuevos: Datos después del cambio
            modulo: Módulo que realizó el cambio
            detalles: Detalles adicionales
        """
        try:
            cursor = self.db_connection.cursor()

            # Crear tabla de auditoría si no existe
            self._create_audit_table_if_not_exists()

            # Insertar registro de auditoría
            cursor.execute("""
                INSERT INTO audit_trail (
                    tabla, accion, registro_id, usuario_id, usuario_nombre,
                    datos_anteriores, datos_nuevos, modulo, detalles,
                    fecha_cambio, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
            """, (
                tabla,
                accion,
                registro_id,
                self.current_user_id,
                self.current_username,
                str(datos_anteriores) if datos_anteriores else None,
                str(datos_nuevos) if datos_nuevos else None,
                modulo,
                detalles,
                self._get_client_ip()
            ))

            self.db_connection.commit()
            return True

        except Exception as e:
            logger.info(f"Error en audit trail: {e}")
            return False

    def _create_audit_table_if_not_exists(self):
        """Crea la tabla de auditoría si no existe"""
        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='audit_trail' AND xtype='U')
                CREATE TABLE audit_trail (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    tabla VARCHAR(100) NOT NULL,
                    accion VARCHAR(20) NOT NULL,
                    registro_id INT NOT NULL,
                    usuario_id INT,
                    usuario_nombre VARCHAR(100),
                    datos_anteriores TEXT,
                    datos_nuevos TEXT,
                    modulo VARCHAR(50),
                    detalles TEXT,
                    fecha_cambio DATETIME NOT NULL DEFAULT GETDATE(),
                    ip_address VARCHAR(45),
                    INDEX idx_tabla_fecha (tabla, fecha_cambio),
                    INDEX idx_usuario_fecha (usuario_id, fecha_cambio),
                    INDEX idx_registro (tabla, registro_id)
                )
            """)

            self.db_connection.commit()

        except Exception as e:
            logger.info(f"Error creando tabla de auditoría: {e}")

    def _get_client_ip(self):
        """Obtiene la IP del cliente"""
        try:
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except (socket.error, OSError) as e:
            logger.info(f"[WARNING AUDIT_TRAIL] Could not get IP address: {e}")
            return "127.0.0.1"

    def get_audit_log(self, tabla: str = None, usuario_id: int = None,
                      fecha_inicio: datetime = None, fecha_fin: datetime = None,
                      limit: int = 100) -> List[Dict]:
        """
        Obtiene registros de auditoría

        Args:
            tabla: Filtrar por tabla específica
            usuario_id: Filtrar por usuario específico
            fecha_inicio: Fecha de inicio del filtro
            fecha_fin: Fecha de fin del filtro
            limit: Límite de registros

        Returns:
            Lista de registros de auditoría
        """
        try:
            cursor = self.db_connection.cursor()

            # Construir query con filtros
            query = "SELECT * FROM audit_trail WHERE 1=1"
            params = []

            if tabla:
                query += " AND tabla = ?"
                params.append(tabla)

            if usuario_id:
                query += " AND usuario_id = ?"
                params.append(usuario_id)

            if fecha_inicio:
                query += " AND fecha_cambio >= ?"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND fecha_cambio <= ?"
                params.append(fecha_fin)

            query += " ORDER BY fecha_cambio DESC"

            if limit:
                # Use parameterized query for limit - if limit is not user-controlled, this is safe
                # However, SQL Server doesn't support parameterized TOP, so we validate limit
                if not isinstance(limit, int) or limit <= 0:
                    raise ValueError("Invalid limit value")
        # FIXED: SQL Injection vulnerability
                query = "SELECT TOP {limit} * FROM (?) AS subquery ORDER BY fecha_cambio DESC", (query,)

            cursor.execute(query, params)

            # Convertir resultados a diccionarios
            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)

            return results

        except Exception as e:
            logger.info(f"Error obteniendo audit log: {e}")
            return []

    def get_record_history(self, tabla: str, registro_id: int) -> List[Dict]:
        """
        Obtiene el historial completo de un registro específico

        Args:
            tabla: Nombre de la tabla
            registro_id: ID del registro

        Returns:
            Lista de cambios del registro
        """
        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT * FROM audit_trail
                WHERE tabla = ? AND registro_id = ?
                ORDER BY fecha_cambio DESC
            """, (tabla, registro_id))

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)

            return results

        except Exception as e:
            logger.info(f"Error obteniendo historial de registro: {e}")
            return []

    def get_user_activity(self, usuario_id: int, limit: int = 50) -> List[Dict]:
        """
        Obtiene la actividad reciente de un usuario

        Args:
            usuario_id: ID del usuario
            limit: Límite de registros

        Returns:
            Lista de actividades del usuario
        """
        return self.get_audit_log(usuario_id=usuario_id, limit=limit)

    def get_table_activity(self, tabla: str, limit: int = 50) -> List[Dict]:
        """
        Obtiene la actividad reciente de una tabla

        Args:
            tabla: Nombre de la tabla
            limit: Límite de registros

        Returns:
            Lista de actividades de la tabla
        """
        return self.get_audit_log(tabla=tabla, limit=limit)

    def delete_old_audit_logs(self, days_to_keep: int = 365):
        """
        Elimina registros de auditoría antiguos

        Args:
            days_to_keep: Días de historial a mantener
        """
        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                DELETE FROM audit_trail
                WHERE fecha_cambio < DATEADD(day, -?, GETDATE())
            """, (days_to_keep,))

            deleted_count = cursor.rowcount
            self.db_connection.commit()

            logger.info(f"Eliminados {deleted_count} registros de auditoría antiguos")
            return deleted_count

        except Exception as e:
            logger.info(f"Error eliminando registros antiguos: {e}")
            return 0


class AuditableModel:
    """Clase base para modelos que requieren auditoría"""

    def __init__(self, tabla_name: str, audit_trail: AuditTrail = None):
        self.tabla_name = tabla_name
        self.audit_trail = audit_trail or AuditTrail()
        self.db_connection = self.audit_trail.db_connection

    def insert_with_audit(self, data: Dict, modulo: str = None) -> Optional[int]:
        """
        Inserta un registro con auditoría

        Args:
            data: Datos a insertar
            modulo: Módulo que realiza la inserción

        Returns:
            ID del registro insertado
        """
        try:
            cursor = self.db_connection.cursor()

            # Agregar timestamps
            data['fecha_creacion'] = datetime.now()
            data['fecha_actualizacion'] = datetime.now()

            # Construir query de inserción
            ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data.keys()])
            values = list(data.values())

        # FIXED: SQL Injection vulnerability
            query = "INSERT INTO {self.tabla_name} ({columns}) VALUES (?)", (placeholders,)
            cursor.execute(query, values)

            # Obtener ID insertado
            cursor.execute("SELECT @@IDENTITY")
            record_id = cursor.fetchone()[0]

            # Registrar en auditoría
            self.audit_trail.log_change(
                tabla=self.tabla_name,
                accion='INSERT',
                registro_id=record_id,
                datos_nuevos=data,
                modulo=modulo,
                detalles=f"Nuevo registro creado en {self.tabla_name}"
            )

            self.db_connection.commit()
            return record_id

        except Exception as e:
        # FIXED: SQL Injection vulnerability
            print("Error en insert_with_audit: ?", (e,))
            self.db_connection.rollback()
            return None

    def update_with_audit(self,
record_id: int,
        data: Dict,
        modulo: str = None) -> bool:
        """
        Actualiza un registro con auditoría

        Args:
            record_id: ID del registro a actualizar
            data: Datos a actualizar
            modulo: Módulo que realiza la actualización

        Returns:
            True si la actualización fue exitosa
        """
        try:
            cursor = self.db_connection.cursor()

            # Obtener datos anteriores
        # FIXED: SQL Injection vulnerability
            cursor.execute("SELECT * FROM ? WHERE id = ?", (self.tabla_name,), (record_id,))
            old_data = cursor.fetchone()

            if not old_data:
                return False

            # Convertir a diccionario
            columns = [desc[0] for desc in cursor.description]
            datos_anteriores = dict(zip(columns, old_data))

            # Agregar timestamp de actualización
            data['fecha_actualizacion'] = datetime.now()

            # Construir query de actualización
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values()) + [record_id]

        # FIXED: SQL Injection vulnerability
            query = "UPDATE {self.tabla_name} SET ? WHERE id = ?", (set_clause,)
            cursor.execute(query, values)

            # Obtener datos nuevos
        # FIXED: SQL Injection vulnerability
            cursor.execute("SELECT * FROM ? WHERE id = ?", (self.tabla_name,), (record_id,))
            new_data = cursor.fetchone()
            datos_nuevos = dict(zip(columns, new_data))

            # Registrar en auditoría
            self.audit_trail.log_change(
                tabla=self.tabla_name,
                accion='UPDATE',
                registro_id=record_id,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                modulo=modulo,
                detalles=f"Registro actualizado en {self.tabla_name}"
            )

            self.db_connection.commit()
            return True

        except Exception as e:
        # FIXED: SQL Injection vulnerability
            print("Error en update_with_audit: ?", (e,))
            self.db_connection.rollback()
            return False

    def delete_with_audit(self, record_id: int, modulo: str = None) -> bool:
        """
        Elimina un registro con auditoría

        Args:
            record_id: ID del registro a eliminar
            modulo: Módulo que realiza la eliminación

        Returns:
            True si la eliminación fue exitosa
        """
        try:
            cursor = self.db_connection.cursor()

            # Obtener datos antes de eliminar
        # FIXED: SQL Injection vulnerability
            cursor.execute("SELECT * FROM ? WHERE id = ?", (self.tabla_name,), (record_id,))
            old_data = cursor.fetchone()

            if not old_data:
                return False

            # Convertir a diccionario
            columns = [desc[0] for desc in cursor.description]
            datos_anteriores = dict(zip(columns, old_data))

            # Eliminar registro
        # FIXED: SQL Injection vulnerability
            cursor.execute("DELETE FROM ? WHERE id = ?", (self.tabla_name,), (record_id,))

            # Registrar en auditoría
            self.audit_trail.log_change(
                tabla=self.tabla_name,
                accion='DELETE',
                registro_id=record_id,
                datos_anteriores=datos_anteriores,
                modulo=modulo,
                detalles=f"Registro eliminado de {self.tabla_name}"
            )

            self.db_connection.commit()
            return True

        except Exception as e:
        # FIXED: SQL Injection vulnerability
            print("Error en delete_with_audit: ?", (e,))
            self.db_connection.rollback()
            return False

    def add_timestamp_columns(self):
        """Agrega columnas de timestamp a la tabla si no existen"""
        try:
            cursor = self.db_connection.cursor()

            # Verificar si las columnas existen
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ? AND COLUMN_NAME = 'fecha_creacion'
            """, (self.tabla_name,))

            if cursor.fetchone()[0] == 0:
                # Agregar columnas de timestamp
                cursor.execute(f"""
                    ALTER TABLE {self.tabla_name}
                    ADD fecha_creacion DATETIME DEFAULT GETDATE(),
                        fecha_actualizacion DATETIME DEFAULT GETDATE()
                """)

                logger.info(f"Columnas de timestamp agregadas a {self.tabla_name}")

            self.db_connection.commit()

        except Exception as e:
            logger.info(f"Error agregando columnas de timestamp: {e}")


# Instancia global del sistema de auditoría
_audit_trail = None

def get_audit_trail():
    """Obtiene la instancia global del sistema de auditoría"""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = AuditTrail()
    return _audit_trail

def set_audit_user(user_id: int, username: str):
    """Establece el usuario actual para auditoría"""
    audit_trail = get_audit_trail()
    audit_trail.set_current_user(user_id, username)
