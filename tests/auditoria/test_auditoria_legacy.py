import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

"""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

Tests refactorizados para el módulo de auditoría.
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

Estos tests reemplazan a test_auditoria_old.py y están actualizados para usar pytest
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

y ser compatibles con la implementación actual de AuditoriaModel.
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

"""

# Imports seguros de módulos
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

try:
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

except ImportError:
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    pytest.skip("Módulo no disponible")

# from rexus.modules.auditoria.model import AuditoriaModel # Movido a sección try/except


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

from pathlib import Path

# Add project root to path
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

sys.path.append(str(ROOT_DIR))

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

from unittest.mock import MagicMock, patch

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

import pytest

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

from rexus.modules.auditoria.model import AuditoriaModel


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

@pytest.fixture
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def mock_db():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Mock de la base de datos para tests de auditoría."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db = MagicMock()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.ejecutar_query.return_value = []
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.last_query = None
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.last_params = None

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def capture_query():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.last_query = query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.last_params = params
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        return mock_db.query_result if hasattr(mock_db, 'query_result') else []

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.ejecutar_query.side_effect = capture_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    return mock_db


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

@pytest.fixture
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def auditoria_model():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Instancia de AuditoriaModel con mock de base de datos."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    return AuditoriaModel(mock_db)


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

class TestAuditoriaModelFixed:
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Tests refactorizados para AuditoriaModel."""

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_basico():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test registrar evento básico."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        usuario_id = 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        modulo = "usuarios"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        tipo_evento = "login"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        detalle = "Usuario inició sesión"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ip_origen = "192.168.1.1"

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(usuario_id, modulo, tipo_evento, detalle, ip_origen)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is True
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_query is not None
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "INSERT INTO auditorias_sistema" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params == (usuario_id, modulo, tipo_evento, detalle, ip_origen)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_argumentos_faltantes():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que falle cuando faltan argumentos requeridos."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(None, "", "", "", "")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(1, None, "login", "detalle", "ip")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_obtener_logs_con_filtro():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test obtener logs filtrados por módulo."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            (1, "2025-04-14 10:00:00", "usuarios", "login", "Usuario inició sesión", "192.168.1.1"),
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            (2, "2025-04-14 11:00:00", "usuarios", "logout", "Usuario cerró sesión", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        logs = auditoria_model.obtener_logs("usuarios")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert len(logs) == 2
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "WHERE modulo_afectado = ?" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params == ("usuarios",)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_obtener_auditorias_sin_filtros():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test obtener todas las auditorías."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            ("2025-04-14 10:00:00", "TEST_USER", "inventario", "inserción", "Item agregado", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        auditorias = auditoria_model.obtener_auditorias()

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert len(auditorias) == 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "SELECT * FROM auditorias_sistema" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params is None or mock_db.last_params == ()

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_obtener_auditorias_con_filtros():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test obtener auditorías con filtros."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            ("2025-04-14 10:00:00", "TEST_USER", "inventario", "inserción", "Item agregado", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        filtros = {"modulo_afectado": "inventario", "tipo_evento": "inserción"}
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        auditorias = auditoria_model.obtener_auditorias(filtros)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert len(auditorias) == 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "WHERE" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "modulo_afectado = ?" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "tipo_evento = ?" in mock_db.last_query

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_exportar_auditorias_excel():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test exportar auditorías a Excel."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            ("2025-04-14 10:00:00", 1, "inventario", "inserción", "Item agregado", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        with patch('pandas.DataFrame') as mock_df:
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_df_instance = MagicMock()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_df.return_value = mock_df_instance

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            resultado = auditoria_model.exportar_auditorias(formato="excel", filename="test.xlsx")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            assert "Excel" in resultado
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_df.assert_called_once()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_df_instance.to_excel.assert_called_once_with("test.xlsx", index=False)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_exportar_auditorias_pdf():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test exportar auditorías a PDF."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            ("2025-04-14 10:00:00", 1, "inventario", "inserción", "Item agregado", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        with patch('fpdf.FPDF') as mock_fpdf:
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_pdf_instance = MagicMock()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_fpdf.return_value = mock_pdf_instance

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            resultado = auditoria_model.exportar_auditorias(formato="pdf", filename="test.pdf")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            assert "PDF" in resultado
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_fpdf.assert_called_once()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            mock_pdf_instance.output.assert_called_once_with("test.pdf")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_exportar_auditorias_formato_invalido():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test exportar con formato no soportado."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        resultado = auditoria_model.exportar_auditorias(formato="xml")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "Formato no soportado" in resultado

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_exportar_auditorias_sin_datos():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test exportar cuando no hay datos."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = []

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        resultado = auditoria_model.exportar_auditorias(formato="excel")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "No hay datos" in resultado

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_error_db():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test manejo de error en base de datos."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.ejecutar_query.side_effect = Exception("Error de BD")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(1, "usuarios", "login", "test", "127.0.0.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_consultar_auditoria_con_usuario():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test consultar auditoría con filtro de usuario."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            (1, "2024-01-15 10:00:00", 1, "usuarios", "login", "Usuario inició sesión", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        resultados = auditoria_model.consultar_auditoria("2024-01-01", "2024-01-31", usuario_id=1)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert len(resultados) == 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "usuario_id = ?" in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params == ("2024-01-01", "2024-01-31", 1)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_consultar_auditoria_sin_usuario():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test consultar auditoría sin filtro de usuario."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            (1, "2024-01-15 10:00:00", 1, "usuarios", "login", "Usuario inició sesión", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        resultados = auditoria_model.consultar_auditoria("2024-01-01", "2024-01-31")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert len(resultados) == 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "usuario_id = ?" not in mock_db.last_query
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params == ("2024-01-01", "2024-01-31")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_obra():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test registrar evento específico de obras."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        usuario = {"id": 1, "nombre": "TEST_USER"}
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        detalle = "Material asociado a obra"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        ip_origen = "192.168.1.1"

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento_obra(usuario, detalle, ip_origen)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is True
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params[0] == 1  # usuario_id
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params[1] == "obras"  # modulo
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params[2] == "asociar_material_a_obra"  # tipo_evento
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params[3] == detalle
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert mock_db.last_params[4] == ip_origen

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_obra_usuario_invalido():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test registrar evento de obra con usuario inválido."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento_obra(None, "detalle", "ip")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento_obra({}, "detalle", "ip")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento_obra({"nombre": "test"}, "detalle", "ip")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is False


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

class TestAuditoriaModelExtendedMethods:
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Tests para métodos extendidos que necesitan implementarse."""

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_consultar_eventos_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que consultar_eventos no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'consultar_eventos')

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_generar_reporte_actividad_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que generar_reporte_actividad no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'generar_reporte_actividad')

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_limpiar_registros_antiguos_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que limpiar_registros_antiguos no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'limpiar_registros_antiguos')

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_eventos_lote_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que registrar_eventos_lote no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'registrar_eventos_lote')

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_verificar_integridad_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que verificar_integridad no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'verificar_integridad')

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_detectar_intentos_sospechosos_metodo_faltante():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que verifica que detectar_intentos_sospechosos no existe (necesita implementarse)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert not hasattr(auditoria_model, 'detectar_intentos_sospechosos')


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

class TestAuditoriaModelSeguridadDatos:
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Tests para validar el manejo seguro de datos sensibles."""

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_registrar_evento_con_datos_sensibles():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test que datos sensibles no se filtran actualmente (necesita mejora)."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        detalle_con_password = "Usuario cambió password de '123456' a 'newpass'"

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            1, "usuarios", "cambio_password", detalle_con_password, "192.168.1.1"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        )

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is True
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        # TODO: Implementar sanitización de datos sensibles
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        # Por ahora, el test pasa pero indica que se necesita sanitización
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert "123456" in str(mock_db.last_params)  # Esto debería cambiar cuando se implemente sanitización

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    def test_manejo_caracteres_unicode():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        """Test manejo de caracteres Unicode."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        detalle_unicode = "Usuario añadió ítem con descripción: Niño"

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        result = auditoria_model.registrar_evento(
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

            1, "inventario", "inserción", detalle_unicode, "192.168.1.1"
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        )

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert result is True
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        assert detalle_unicode in str(mock_db.last_params)


# Tests independientes (no en clase)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def test_registrar_evento_independiente():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Test independiente para registrar evento."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    model = AuditoriaModel(mock_db)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    result = model.registrar_evento(1, "test", "accion", "detalle", "127.0.0.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert result is True


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def test_flujo_completo_auditoria():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Test de flujo completo: registrar y consultar."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    model = AuditoriaModel(mock_db)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # Registrar evento
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    result = model.registrar_evento(1, "usuarios", "login", "Usuario inició sesión", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert result is True

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # Configurar resultado mock para consulta
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.query_result = [
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

        (1, "2025-04-14 10:00:00", 1, "usuarios", "login", "Usuario inició sesión", "192.168.1.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    ]

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # Consultar logs
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    logs = model.obtener_logs("usuarios")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert len(logs) == 1
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert logs[0][3] == "usuarios"  # módulo
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert logs[0][4] == "login"     # tipo_evento


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def test_error_conexion_db():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Test que verifica manejo de errores de conexión."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db_error = MagicMock()
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db_error.ejecutar_query.side_effect = Exception("Conexión perdida")

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    model = AuditoriaModel(mock_db_error)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    result = model.registrar_evento(1, "test", "accion", "detalle", "127.0.0.1")
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert result is False


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

def test_validacion_parametros_obtener_auditorias():
    pass

import sys
import pytest
from pathlib import Path

    pass

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    """Test validación de parámetros en obtener_auditorias."""
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    model = AuditoriaModel(mock_db)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    mock_db.query_result = []

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # Test con filtros válidos
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    filtros_validos = {"modulo_afectado": "usuarios", "tipo_evento": "login"}
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    result = model.obtener_auditorias(filtros_validos)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert isinstance(result, list)

import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # Test con filtros inválidos (deberían ser ignorados)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    filtros_invalidos = {"campo_inexistente": "valor", "otro_campo": "otro_valor"}
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    result = model.obtener_auditorias(filtros_invalidos)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert isinstance(result, list)
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    # El query no debería tener WHERE ya que los filtros son inválidos
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    assert "WHERE" not in mock_db.last_query


import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

if __name__ == "__main__":
import sys
import pytest
from pathlib import Path

import sys
import sys
import pytest
from pathlib import Path

import pytest
import sys
import pytest
from pathlib import Path

from pathlib import Path

import sys
import pytest
from pathlib import Path

    pytest.main([__file__, "-v"])
