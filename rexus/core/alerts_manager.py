"""
Sistema de Alertas - Rexus.app
Gestiona alertas y notificaciones para eventos críticos

Características:
- Reglas de alertas configurables
- Canales múltiples: email, Slack, webhook
- Escalación de alertas
- Supresión temporal
- Historial de alertas
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Niveles de severidad de alertas."""
    CRITICAL = "critical"
    HIGH = "high"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class AlertStatus(Enum):
    """Estados de una alerta."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Representa una alerta."""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    source: str
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None

    def to_dict(self) -> dict:
        """Convierte la alerta a diccionario."""
        d = asdict(self)
        d['severity'] = self.severity.value
        d['status'] = self.status.value
        d['created_at'] = self.created_at.isoformat()
        d['updated_at'] = self.updated_at.isoformat()
        if self.acknowledged_at:
            d['acknowledged_at'] = self.acknowledged_at.isoformat()
        if self.resolved_at:
            d['resolved_at'] = self.resolved_at.isoformat()
        return d


@dataclass
class AlertRule:
    """Regla de alerta."""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: Callable[[dict], bool]
    duration_seconds: int = 0  # 0 = alerta inmediata
    enabled: bool = True
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None


class NotificationChannel:
    """Canal de notificación base."""

    def send(self, alert: Alert) -> bool:
        """Envía una notificación sobre la alerta."""
        raise NotImplementedError

    def test(self) -> bool:
        """Prueba la conexión del canal."""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Canal de notificación por email."""

    def __init__(self,
                 smtp_host: str,
                 smtp_port: int,
                 username: str,
                 password: str,
                 from_address: str,
                 to_addresses: List[str],
                 use_tls: bool = True):
        """
        Inicializa el canal de email.

        Args:
            smtp_host: Servidor SMTP
            smtp_port: Puerto SMTP
            username: Usuario de autenticación
            password: Contraseña
            from_address: Dirección de origen
            to_addresses: Lista de destinatarios
            use_tls: Si usar TLS
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.to_addresses = to_addresses
        self.use_tls = use_tls

    def send(self, alert: Alert) -> bool:
        """Envía una alerta por email."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"
            msg['From'] = self.from_address
            msg['To'] = ', '.join(self.to_addresses)

            # Crear contenido HTML
            html = self._format_alert_html(alert)
            html_part = MIMEText(html, 'html')
            msg.attach(html_part)

            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email enviado para alerta {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email para alerta {alert.id}: {e}")
            return False

    def test(self) -> bool:
        """Prueba la conexión SMTP."""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
            return True
        except Exception as e:
            logger.error(f"Error probando conexión SMTP: {e}")
            return False

    def _format_alert_html(self, alert: Alert) -> str:
        """Formatea la alerta como HTML."""
        severity_colors = {
            AlertSeverity.CRITICAL: "#d32f2f",
            AlertSeverity.HIGH: "#f57c00",
            AlertSeverity.WARNING: "#fbc02d",
            AlertSeverity.INFO: "#1976d2",
            AlertSeverity.DEBUG: "#757575"
        }

        color = severity_colors.get(alert.severity, "#757575")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 4px solid {color};
                    padding: 15px;
                    background-color: #f5f5f5;
                    margin: 10px 0;
                }}
                .alert-title {{
                    color: {color};
                    font-size: 18px;
                    font-weight: bold;
                    margin: 0 0 10px 0;
                }}
                .alert-message {{ margin: 10px 0; }}
                .alert-meta {{ font-size: 12px; color: #666; }}
                .label {{
                    display: inline-block;
                    background: #e0e0e0;
                    padding: 2px 8px;
                    margin: 2px;
                    border-radius: 3px;
                    font-size: 11px;
                }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="alert-title">{alert.name}</div>
                <div class="alert-message">{alert.message}</div>
                <div class="alert-meta">
                    <strong>Severidad:</strong> {alert.severity.value.upper()}<br>
                    <strong>Origen:</strong> {alert.source}<br>
                    <strong>Fecha:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
        """

        if alert.labels:
            html += "<div><strong>Labels:</strong><br>"
            for key, value in alert.labels.items():
                html += f'<span class="label">{key}: {value}</span>'
            html += "</div>"

        html += """
            </div>
        </body>
        </html>
        """

        return html


class SlackChannel(NotificationChannel):
    """Canal de notificación por Slack."""

    def __init__(self, webhook_url: str, channel: str = None, username: str = "Rexus Alerts"):
        """
        Inicializa el canal de Slack.

        Args:
            webhook_url: URL del webhook de Slack
            channel: Canal destino (opcional, usa el del webhook)
            username: Nombre del bot
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username

    def send(self, alert: Alert) -> bool:
        """Envía una alerta a Slack."""
        try:
            # Colores por severidad
            severity_colors = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.WARNING: "warning",
                AlertSeverity.INFO: "good",
                AlertSeverity.DEBUG: "#757575"
            }

            color = severity_colors.get(alert.severity, "#757575")

            payload = {
                "username": self.username,
                "attachments": [
                    {
                        "color": color,
                        "title": f"[{alert.severity.value.upper()}] {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Severidad", "value": alert.severity.value.upper(), "short": True},
                            {"title": "Origen", "value": alert.source, "short": True},
                            {"title": "Fecha", "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S'), "short": True},
                            {"title": "Estado", "value": alert.status.value, "short": True}
                        ]
                    }
                ]
            }

            if self.channel:
                payload["channel"] = self.channel

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Slack notification enviada para alerta {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Error enviando Slack notification para alerta {alert.id}: {e}")
            return False

    def test(self) -> bool:
        """Prueba el webhook de Slack."""
        try:
            payload = {
                "text": "Test message from Rexus AlertManager",
                "username": self.username
            }

            if self.channel:
                payload["channel"] = self.channel

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Error probando webhook de Slack: {e}")
            return False


class WebhookChannel(NotificationChannel):
    """Canal de notificación por webhook genérico."""

    def __init__(self, url: str, headers: Dict[str, str] = None):
        """
        Inicializa el canal de webhook.

        Args:
            url: URL del webhook
            headers: Headers adicionales
        """
        self.url = url
        self.headers = headers or {}

    def send(self, alert: Alert) -> bool:
        """Envía una alerta por webhook."""
        try:
            payload = alert.to_dict()

            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"Webhook notification enviada para alerta {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Error enviando webhook notification para alerta {alert.id}: {e}")
            return False

    def test(self) -> bool:
        """Prueba el webhook."""
        try:
            payload = {"test": True, "message": "Test from Rexus AlertManager"}

            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Error probando webhook: {e}")
            return False


class AlertManager:
    """
    Gestor principal de alertas.

    Evalúa reglas, envía notificaciones y gestiona el estado de alertas.
    """

    def __init__(self, storage_path: str = None):
        """
        Inicializa el AlertManager.

        Args:
            storage_path: Ruta para almacenamiento de historial
        """
        self.storage_path = storage_path or os.getenv("ALERTS_STORAGE_PATH", "./data/alerts.json")
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.channels: List[NotificationChannel] = []

        # Cargar historial
        self._load_history()

        # Cargar canales desde configuración
        self._load_channels()

    def _load_history(self):
        """Carga el historial de alertas desde disco."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                for alert_data in data.get('history', []):
                    alert = Alert(
                        id=alert_data['id'],
                        name=alert_data['name'],
                        severity=AlertSeverity(alert_data['severity']),
                        status=AlertStatus(alert_data['status']),
                        message=alert_data['message'],
                        source=alert_data['source'],
                        created_at=datetime.fromisoformat(alert_data['created_at']),
                        updated_at=datetime.fromisoformat(alert_data['updated_at']),
                        acknowledged_at=datetime.fromisoformat(alert_data['acknowledged_at']) if alert_data.get('acknowledged_at') else None,
                        acknowledged_by=alert_data.get('acknowledged_by'),
                        resolved_at=datetime.fromisoformat(alert_data['resolved_at']) if alert_data.get('resolved_at') else None,
                        labels=alert_data.get('labels'),
                        annotations=alert_data.get('annotations')
                    )
                    self.alert_history.append(alert)

                logger.info(f"Cargadas {len(self.alert_history)} alertas del historial")

            except Exception as e:
                logger.error(f"Error cargando historial de alertas: {e}")

    def _save_history(self):
        """Guarda el historial de alertas a disco."""
        try:
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

            data = {
                'history': [alert.to_dict() for alert in self.alert_history]
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error guardando historial de alertas: {e}")

    def _load_channels(self):
        """Carga canales de notificación desde configuración."""
        # Email
        if os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true":
            self.channels.append(EmailChannel(
                smtp_host=os.getenv("ALERT_SMTP_HOST", "localhost"),
                smtp_port=int(os.getenv("ALERT_SMTP_PORT", "587")),
                username=os.getenv("ALERT_SMTP_USERNAME", ""),
                password=os.getenv("ALERT_SMTP_PASSWORD", ""),
                from_address=os.getenv("ALERT_EMAIL_FROM", "alerts@rexus.app"),
                to_addresses=os.getenv("ALERT_EMAIL_TO", "").split(","),
                use_tls=os.getenv("ALERT_SMTP_TLS", "true").lower() == "true"
            ))

        # Slack
        slack_webhook = os.getenv("ALERT_SLACK_WEBHOOK")
        if slack_webhook:
            self.channels.append(SlackChannel(
                webhook_url=slack_webhook,
                channel=os.getenv("ALERT_SLACK_CHANNEL"),
                username=os.getenv("ALERT_SLACK_USERNAME", "Rexus Alerts")
            ))

        # Webhook genérico
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if webhook_url:
            self.channels.append(WebhookChannel(
                url=webhook_url
            ))

    def add_rule(self, rule: AlertRule):
        """Agrega una regla de alerta."""
        self.rules[rule.id] = rule
        logger.info(f"Regla de alerta agregada: {rule.name}")

    def remove_rule(self, rule_id: str):
        """Elimina una regla de alerta."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Regla de alerta eliminada: {rule_id}")

    def evaluate_rules(self, context: dict) -> List[Alert]:
        """
        Evalúa todas las reglas contra el contexto proporcionado.

        Args:
            context: Diccionario con datos a evaluar

        Returns:
            Lista de alertas generadas
        """
        new_alerts = []

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            try:
                if rule.condition(context):
                    # Verificar si ya existe una alerta activa para esta regla
                    existing_key = f"{rule_id}_{context.get('entity_id', 'default')}"

                    if existing_key not in self.active_alerts:
                        alert = Alert(
                            id=f"{rule_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            name=rule.name,
                            severity=rule.severity,
                            status=AlertStatus.ACTIVE,
                            message=rule.description,
                            source=context.get('source', 'unknown'),
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            labels=rule.labels or {},
                            annotations=rule.annotations or {}
                        )

                        self.active_alerts[existing_key] = alert
                        self.alert_history.append(alert)
                        new_alerts.append(alert)

                        # Enviar notificaciones
                        self._notify(alert)

            except Exception as e:
                logger.error(f"Error evaluando regla {rule_id}: {e}")

        # Guardar historial si hay nuevas alertas
        if new_alerts:
            self._save_history()

        return new_alerts

    def _notify(self, alert: Alert):
        """Envía notificaciones para una alerta."""
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                logger.error(f"Error enviando notificación por canal: {e}")

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """
        Reconoce una alerta.

        Args:
            alert_id: ID de la alerta
            user: Usuario que reconoce

        Returns:
            True si se reconoció exitosamente
        """
        for key, alert in self.active_alerts.items():
            if alert.id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = user
                alert.updated_at = datetime.now()

                self._save_history()
                logger.info(f"Alerta {alert_id} reconocida por {user}")
                return True

        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resuelve una alerta.

        Args:
            alert_id: ID de la alerta

        Returns:
            True si se resolvió exitosamente
        """
        for key, alert in list(self.active_alerts.items()):
            if alert.id == alert_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                alert.updated_at = datetime.now()

                # Remover de alertas activas
                del self.active_alerts[key]

                self._save_history()
                logger.info(f"Alerta {alert_id} resuelta")
                return True

        return False

    def get_active_alerts(self) -> List[Alert]:
        """Retorna todas las alertas activas."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Retorna el historial de alertas."""
        return self.alert_history[-limit:]

    def test_channels(self) -> Dict[str, bool]:
        """Prueba todos los canales de notificación."""
        results = {}

        for i, channel in enumerate(self.channels):
            channel_name = channel.__class__.__name__
            results[channel_name] = channel.test()

        return results


# Instancia global
_alert_manager_instance = None


def get_alert_manager() -> AlertManager:
    """Obtiene la instancia singleton del AlertManager."""
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager()

        # Agregar reglas por defecto
        _setup_default_rules(_alert_manager_instance)

    return _alert_manager_instance


def _setup_default_rules(manager: AlertManager):
    """Configura reglas de alerta por defecto."""

    # Regla: Stock bajo
    manager.add_rule(AlertRule(
        id="stock_low",
        name="Stock Bajo",
        description="El stock de un producto está por debajo del mínimo",
        severity=AlertSeverity.HIGH,
        condition=lambda ctx: ctx.get('stock', 0) < ctx.get('stock_min', 10)
    ))

    # Regla: Backup fallido
    manager.add_rule(AlertRule(
        id="backup_failed",
        name="Backup Fallido",
        description="El último backup falló",
        severity=AlertSeverity.CRITICAL,
        condition=lambda ctx: ctx.get('backup_status') == 'failed'
    ))

    # Regla: Login fallidos múltiples
    manager.add_rule(AlertRule(
        id="multiple_failed_logins",
        name="Múltiples Logins Fallidos",
        description="Se detectaron múltiples intentos de login fallidos",
        severity=AlertSeverity.WARNING,
        condition=lambda ctx: ctx.get('failed_login_count', 0) >= 3
    ))

    # Regla: Base de datos desconectada
    manager.add_rule(AlertRule(
        id="database_disconnected",
        name="Base de Datos Desconectada",
        description="No se puede conectar a la base de datos",
        severity=AlertSeverity.CRITICAL,
        condition=lambda ctx: ctx.get('db_connected') is False
    ))


# Funciones de conveniencia
def trigger_alert(name: str,
                 severity: AlertSeverity,
                 message: str,
                 source: str = "manual",
                 labels: Dict = None) -> Optional[Alert]:
    """
    Dispara una alerta manualmente.

    Args:
        name: Nombre de la alerta
        severity: Severidad
        message: Mensaje
        source: Origen
        labels: Labels adicionales

    Returns:
        Alerta creada o None
    """
    manager = get_alert_manager()

    alert = Alert(
        id=f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name=name,
        severity=severity,
        status=AlertStatus.ACTIVE,
        message=message,
        source=source,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        labels=labels or {}
    )

    manager.active_alerts[alert.id] = alert
    manager.alert_history.append(alert)
    manager._notify(alert)
    manager._save_history()

    return alert


def evaluate_context(context: dict) -> List[Alert]:
    """
    Evalúa el contexto contra las reglas de alerta.

    Args:
        context: Diccionario con datos a evaluar

    Returns:
        Lista de alertas generadas
    """
    return get_alert_manager().evaluate_rules(context)
