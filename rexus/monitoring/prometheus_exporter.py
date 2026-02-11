"""
Prometheus Exporter - Exportador de Métricas

Expone métricas en formato Prometheus para ser scrapeadas.
"""

import logging
from typing import Dict, Any
from .metrics_manager import MetricsManager

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """
    Exportador de métricas en formato Prometheus.

    Convierte las métricas internas al formato de texto que
    Prometheus espera scrapeando el endpoint /metrics.
    """

    def __init__(self, metrics_manager: MetricsManager = None):
        """
        Inicializa el exportador.

        Args:
            metrics_manager: Gestor de métricas (opcional)
        """
        self.metrics_manager = metrics_manager or MetricsManager

    def export_metrics(self) -> str:
        """
        Exporta todas las métricas en formato Prometheus.

        Returns:
            String con métricas en formato Prometheus
        """
        lines = []

        # HELP y TYPE para cada métrica
        lines.extend(self._format_help("Counters"))
        lines.extend(self._format_counters())

        lines.extend(self._format_help("Gauges"))
        lines.extend(self._format_gauges())

        lines.extend(self._format_help("Histograms"))
        lines.extend(self._format_histograms())

        lines.extend(self._format_help("Summaries"))
        lines.extend(self._format_summaries())

        return '\n'.join(lines) + '\n'

    def _format_help(self, metric_type: str) -> list:
        """Agrega HELP y TYPE para métricas."""
        return [
            f"# HELP rexus_{metric_type.lower()}_custom Métricas personalizadas de {metric_type}",
            f"# TYPE rexus_{metric_type.lower()}_custom gauge"
        ]

    def _format_counters(self) -> list:
        """Formatea contadores."""
        lines = []
        counters = self.metrics_manager.get_all_metrics()['counters']

        for key, value in counters.items():
            # Extraer nombre y labels del key
            name, labels = self._parse_key(key)
            prometheus_name = f"rexus_counter_{name}"

            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{prometheus_name}{{{label_str}}} {value}")
            else:
                lines.append(f'{prometheus_name} {value}')

        return lines

    def _format_gauges(self) -> list:
        """Formatea gauges."""
        lines = []
        gauges = self.metrics_manager.get_all_metrics()['gauges']

        for key, value in gauges.items():
            name, labels = self._parse_key(key)
            prometheus_name = f"rexus_gauge_{name}"

            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{prometheus_name}{{{label_str}}} {value}')
            else:
                lines.append(f'{prometheus_name} {value}')

        return lines

    def _format_histograms(self) -> list:
        """Formatea histogramas con buckets."""
        lines = []
        histograms = self.metrics_manager.get_all_metrics()['histograms']

        for key, values in histograms.items():
            if not values:
                continue

            name, labels = self._parse_key(key)
            prometheus_name = f"rexus_histogram_{name}"

            # Calcular buckets
            sorted_values = sorted([v['value'] for v in values])
            count = len(sorted_values)
            sum_value = sum(sorted_values)

            # Buckets estándar de Prometheus
            buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

            label_str = ','.join(f'{k}="{v}"' for k, v in labels.items()) if labels else ''

            # Agregar cada bucket
            for bucket in buckets:
                bucket_count = sum(1 for v in sorted_values if v <= bucket)
                if labels:
                    lines.append(f'{prometheus_name}_bucket{{le="{bucket}",{label_str}}} {bucket_count}')
                else:
                    lines.append(f'{prometheus_name}_bucket{{le="{bucket}"}} {bucket_count}')

            # Bucket +Inf (todos los valores)
            if labels:
                lines.append(f'{prometheus_name}_bucket{{le="+Inf",{label_str}}} {count}')
            else:
                lines.append(f'{prometheus_name}_bucket{{le="+Inf"}} {count}')

            # Sum y count
            if labels:
                lines.append(f'{prometheus_name}_sum{{{label_str}}} {sum_value}')
                lines.append(f'{prometheus_name}_count{{{label_str}}} {count}')
            else:
                lines.append(f'{prometheus_name}_sum {sum_value}')
                lines.append(f'{prometheus_name}_count {count}')

        return lines

    def _format_summaries(self) -> list:
        """Formatea summaries con cuantiles."""
        lines = []
        summaries = self.metrics_manager.get_all_metrics()['summaries']

        for key, values in summaries.items():
            if not values:
                continue

            name, labels = self._parse_key(key)
            prometheus_name = f"rexus_summary_{name}"

            sorted_values = sorted([v['value'] for v in values])
            count = len(sorted_values)
            sum_value = sum(sorted_values)

            # Cuantiles estándar
            quantiles = [0.5, 0.9, 0.95, 0.99]

            label_str = ','.join(f'{k}="{v}"' for k, v in labels.items()) if labels else ''

            # Agregar cada cuantil
            for quantile in quantiles:
                idx = int(quantile * count)
                value = sorted_values[idx] if idx < count else sorted_values[-1]
                if labels:
                    lines.append(f'{prometheus_name}{{quantile="{quantile}",{label_str}}} {value}')
                else:
                    lines.append(f'{prometheus_name}{{quantile="{quantile}"}} {value}')

            # Sum y count
            if labels:
                lines.append(f'{prometheus_name}_sum{{{label_str}}} {sum_value}')
                lines.append(f'{prometheus_name}_count{{{label_str}}} {count}')
            else:
                lines.append(f'{prometheus_name}_sum {sum_value}')
                lines.append(f'{prometheus_name}_count {count}')

        return lines

    def _parse_key(self, key: str) -> tuple:
        """
        Parsea una key en nombre y labels.

        Args:
            key: Key en formato "nombre{label1="valor1",label2="valor2"}

        Returns:
            (nombre, dict_labels)
        """
        if '{' not in key:
            return key, {}

        # Separar nombre y labels
        name_part, labels_part = key.split('{', 1)
        labels_part = labels_part.rstrip('}')

        # Parsear labels
        labels = {}
        for label_pair in labels_part.split(','):
            if '=' in label_pair:
                label_name, label_value = label_pair.split('=', 1)
                labels[label_name.strip()] = label_value.strip().strip('"')

        return name_part, labels


def create_metrics_endpoint(app=None, route: str = '/metrics'):
    """
    Crea un endpoint Flask para exponer métricas.

    Args:
        app: Aplicación Flask (opcional)
        route: Ruta del endpoint (default: /metrics)

    Returns:
        Función del endpoint
    """
    def metrics_endpoint():
        """Endpoint para métricas Prometheus."""
        try:
            exporter = PrometheusExporter()
            metrics = exporter.export_metrics()
            return metrics, 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'}
        except Exception as e:
            logger.error(f"Error exportando métricas: {e}")
            return "# Error exportando métricas\n", 500, {'Content-Type': 'text/plain'}

    if app:
        app.route(route)(metrics_endpoint)

    return metrics_endpoint
