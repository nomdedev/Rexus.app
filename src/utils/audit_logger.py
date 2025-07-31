"""
Audit Logger - Rexus.app
Comprehensive audit logging system for security and compliance.
"""

import logging
import json
import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import os
from pathlib import Path

class AuditEventType(Enum):
    """Types of audit events."""
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_UPDATED = "PRODUCT_UPDATED"
    PRODUCT_DELETED = "PRODUCT_DELETED"
    STOCK_UPDATED = "STOCK_UPDATED"
    
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_COMPLETED = "ORDER_COMPLETED"
    
    OBRA_CREATED = "OBRA_CREATED"
    OBRA_UPDATED = "OBRA_UPDATED"
    OBRA_COMPLETED = "OBRA_COMPLETED"
    
    DATABASE_QUERY = "DATABASE_QUERY"
    DATABASE_ERROR = "DATABASE_ERROR"
    
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"

class AuditSeverity(Enum):
    """Severity levels for audit events."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AuditLogger:
    """
    Comprehensive audit logging system.
    """
    
    def __init__(self, log_directory: str = None, db_connection=None):
        """
        Initialize audit logger.
        
        Args:
            log_directory: Directory for audit log files
            db_connection: Database connection for storing audit records
        """
        self.db_connection = db_connection
        
        # Set up log directory
        if log_directory is None:
            project_root = Path(__file__).parent.parent.parent
            log_directory = project_root / "logs" / "audit"
        
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Set up file logger
        self.logger = logging.getLogger('rexus_audit')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not self.logger.handlers:
            # File handler for all audit events
            log_file = self.log_directory / f"audit_{datetime.date.today().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Security events handler (separate file for critical events)
            security_log_file = self.log_directory / f"security_{datetime.date.today().strftime('%Y%m%d')}.log"
            security_handler = logging.FileHandler(security_log_file, encoding='utf-8')
            security_handler.setLevel(logging.WARNING)
            
            # JSON formatter for structured logging
            json_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
            )
            file_handler.setFormatter(json_formatter)
            security_handler.setFormatter(json_formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            
            # Create security logger
            self.security_logger = logging.getLogger('rexus_security')
            self.security_logger.setLevel(logging.WARNING)
            self.security_logger.addHandler(security_handler)
        
        self.logger.info('"audit_system_initialized": "Audit logging system started"')
    
    def log_event(self, event_type: AuditEventType, severity: AuditSeverity,
                  user_id: Optional[int] = None, username: Optional[str] = None,
                  ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                  module: Optional[str] = None, action: Optional[str] = None,
                  resource_type: Optional[str] = None, resource_id: Optional[int] = None,
                  old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                  additional_data: Optional[Dict] = None, error_message: Optional[str] = None):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            severity: Severity level
            user_id: ID of the user performing the action
            username: Username of the user
            ip_address: IP address of the request
            user_agent: User agent string
            module: Module where event occurred
            action: Specific action performed
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            old_values: Previous values (for updates)
            new_values: New values (for updates)
            additional_data: Additional event data
            error_message: Error message (for error events)
        """
        audit_record = {
            "event_id": self._generate_event_id(),
            "event_type": event_type.value,
            "severity": severity.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "module": module,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "old_values": old_values,
            "new_values": new_values,
            "additional_data": additional_data,
            "error_message": error_message
        }
        
        # Remove None values
        audit_record = {k: v for k, v in audit_record.items() if v is not None}
        
        # Log to file
        log_message = json.dumps(audit_record, ensure_ascii=False)
        
        if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            self.security_logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log to database if available
        if self.db_connection:
            self._log_to_database(audit_record)
    
    def log_user_login(self, username: str, user_id: int, ip_address: str, 
                      user_agent: str = None, success: bool = True):
        """Log user login event."""
        event_type = AuditEventType.USER_LOGIN if success else AuditEventType.USER_LOGIN_FAILED
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        
        self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id if success else None,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            module="authentication",
            action="login"
        )
    
    def log_user_logout(self, username: str, user_id: int, ip_address: str):
        """Log user logout event."""
        self.log_event(
            event_type=AuditEventType.USER_LOGOUT,
            severity=AuditSeverity.LOW,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            module="authentication",
            action="logout"
        )
    
    def log_data_modification(self, event_type: AuditEventType, user_id: int, 
                             username: str, module: str, resource_type: str,
                             resource_id: int, old_values: Dict = None, 
                             new_values: Dict = None, ip_address: str = None):
        """Log data modification events."""
        self.log_event(
            event_type=event_type,
            severity=AuditSeverity.MEDIUM,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            module=module,
            action=event_type.value.lower(),
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values
        )
    
    def log_security_violation(self, violation_type: str, username: str = None,
                              ip_address: str = None, details: Dict = None):
        """Log security violation."""
        self.log_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            severity=AuditSeverity.HIGH,
            username=username,
            ip_address=ip_address,
            module="security",
            action=violation_type,
            additional_data=details
        )
    
    def log_database_query(self, query: str, user_id: int = None, 
                          username: str = None, execution_time: float = None,
                          rows_affected: int = None, error: str = None):
        """Log database query execution."""
        event_type = AuditEventType.DATABASE_ERROR if error else AuditEventType.DATABASE_QUERY
        severity = AuditSeverity.HIGH if error else AuditSeverity.LOW
        
        additional_data = {
            "query": query[:500],  # Truncate long queries
            "execution_time": execution_time,
            "rows_affected": rows_affected
        }
        
        self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            username=username,
            module="database",
            action="query_execution",
            additional_data=additional_data,
            error_message=error
        )
    
    def log_system_error(self, error_message: str, module: str, 
                        user_id: int = None, username: str = None,
                        stack_trace: str = None):
        """Log system error."""
        additional_data = {"stack_trace": stack_trace} if stack_trace else None
        
        self.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            severity=AuditSeverity.HIGH,
            user_id=user_id,
            username=username,
            module=module,
            action="system_error",
            additional_data=additional_data,
            error_message=error_message
        )
    
    def get_audit_logs(self, start_date: datetime.date = None, 
                      end_date: datetime.date = None,
                      event_type: AuditEventType = None,
                      username: str = None,
                      severity: AuditSeverity = None,
                      limit: int = 100) -> List[Dict]:
        """
        Retrieve audit logs with filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            event_type: Filter by event type
            username: Filter by username
            severity: Filter by severity
            limit: Maximum number of records to return
            
        Returns:
            List of audit log records
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Build query with filters
            query = """
            SELECT event_id, event_type, severity, timestamp, user_id, username,
                   ip_address, module, action, resource_type, resource_id,
                   old_values, new_values, additional_data, error_message
            FROM auditoria
            WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND DATE(timestamp) >= ?"
                params.append(start_date.strftime('%Y-%m-%d'))
            
            if end_date:
                query += " AND DATE(timestamp) <= ?"
                params.append(end_date.strftime('%Y-%m-%d'))
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            
            if username:
                query += " AND username = ?"
                params.append(username)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            self.logger.error(f'"audit_query_error": "{str(e)}"')
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """
        Clean up old audit log files.
        
        Args:
            days_to_keep: Number of days to keep log files
        """
        try:
            cutoff_date = datetime.date.today() - datetime.timedelta(days=days_to_keep)
            
            for log_file in self.log_directory.glob("*.log"):
                # Extract date from filename
                try:
                    date_str = log_file.stem.split('_')[1]
                    file_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        self.logger.info(f'"log_cleanup": "Deleted old log file {log_file.name}"')
                        
                except (IndexError, ValueError):
                    # Skip files that don't match expected naming pattern
                    continue
                    
        except Exception as e:
            self.logger.error(f'"log_cleanup_error": "{str(e)}"')
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _log_to_database(self, audit_record: Dict[str, Any]):
        """Log audit record to database."""
        try:
            from src.utils.sql_loader import load_sql
            
            cursor = self.db_connection.cursor()
            sql_insert = load_sql("auditoria", "insert_audit_log")
            
            cursor.execute(sql_insert, (
                audit_record.get('user_id'),
                audit_record.get('module'),
                audit_record.get('action'),
                audit_record.get('resource_type'),
                audit_record.get('resource_id'),
                json.dumps(audit_record.get('old_values')) if audit_record.get('old_values') else None,
                json.dumps(audit_record.get('new_values')) if audit_record.get('new_values') else None,
                audit_record.get('ip_address'),
                audit_record.get('user_agent')
            ))
            
            self.db_connection.commit()
            
        except Exception as e:
            # Don't raise exception to avoid breaking main application flow
            self.logger.error(f'"database_audit_error": "{str(e)}"')

# Global audit logger instance
audit_logger = AuditLogger()

def log_audit_event(event_type: AuditEventType, severity: AuditSeverity, **kwargs):
    """
    Convenience function for logging audit events.
    
    Args:
        event_type: Type of audit event
        severity: Severity level
        **kwargs: Additional event data
    """
    audit_logger.log_event(event_type, severity, **kwargs)