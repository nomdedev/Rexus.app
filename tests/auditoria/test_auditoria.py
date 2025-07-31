import pytest_check as check

#!/usr/bin/env python3
"""
Tests completos para el módulo auditoria.
Incluye tests unitarios, edge cases y validaciones de seguridad.
"""


import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importar el modelo real de auditoría
try:
    from rexus.modules.auditoria.model import AuditoriaModel
except ImportError:
    pytest.skip("Módulo auditoria no disponible", allow_module_level=True)


@pytest.fixture
def mock_db():
    """Fixture para simular la base de datos."""
    mock = MagicMock()
    mock.ejecutar_query.return_value = []
    mock.transaction.return_value.__enter__.return_value = mock
    mock.transaction.return_value.__exit__.return_value = None

    # Agregar atributos para tracking
    mock.last_query = None
    mock.last_params = None
    mock.query_result = []

    def capture_query(query, params=None):
        mock.last_query = query
        mock.last_params = params
        if hasattr(mock, "query_result") and mock.query_result:
            return mock.query_result
        return []

    def set_query_result(result):
        mock.query_result = result
        mock.ejecutar_query.return_value = result

    # Configurar el side_effect inicialmente para capturar queries
    mock.ejecutar_query.side_effect = capture_query
    mock.set_query_result = set_query_result

    return mock


@pytest.fixture
def auditoria_model(mock_db):
    """Fixture para crear instancia del modelo con DB mockeada."""
    return AuditoriaModel(mock_db)


class TestAuditoriaModel:
    """Tests para el modelo de auditoría."""

    def test_registrar_evento(self, auditoria_model, mock_db):
        """Probar registro de un evento de auditoría con usuario_id explícito."""
        usuario_id = 1
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        auditoria_model.registrar_evento(
            usuario_id, modulo, tipo_evento, detalle, ip_origen
        )
        check.is_not_none(mock_db.last_query)
        if mock_db.last_query:
            check.is_in("INSERT INTO auditorias_sistema", mock_db.last_query)
            check.is_in("usuario_id", mock_db.last_query)

    def test_registrar_evento_faltan_argumentos(self, auditoria_model, mock_db):
        """Debe retornar False y loggear si falta usuario_id, modulo o tipo_evento."""
        usuario_id = None
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        resultado = auditoria_model.registrar_evento(
            usuario_id, modulo, tipo_evento, detalle, ip_origen
        )
        check.is_false(resultado)

    def test_obtener_logs(self, auditoria_model, mock_db):
        # Probar obtención de logs de auditoría
        mock_db.set_query_result(
            [
                (
                    1,
                    "2025-04-14 10:00:00",
                    "usuarios",
                    "inserción",
                    "Usuario creado",
                    "192.168.1.1",
                ),
                (
                    2,
                    "2025-04-14 11:00:00",
                    "usuarios",
                    "logout",
                    "Usuario cerró sesión",
                    "192.168.1.1",
                ),
            ]
        )
        logs = auditoria_model.obtener_logs("usuarios")
        check.equal(len(logs), 2)  # Devuelve todos los que coinciden con el filtro
        check.equal(logs[0][2], "usuarios")

    def test_obtener_auditorias(self, auditoria_model, mock_db):
        # Simular datos de auditoría
        mock_db.query_result = [
            (
                "2025-04-14 10:00:00",
                "TEST_USER",
                "inventario",
                "inserción",
                "Agregó un nuevo ítem",
                "192.168.1.1",
            ),
            (
                "2025-04-14 11:00:00",
                "user1",
                "logística",
                "modificación",
                "Actualizó estado de entrega",
                "192.168.1.2",
            ),
        ]
        filtros = {"modulo_afectado": "inventario"}
        auditorias = auditoria_model.obtener_auditorias(filtros)
        check.is_in(
            "SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?",
            mock_db.last_query,
        )
        check.equal(mock_db.last_params, ("inventario",))
        check.equal(len(auditorias), 2)  # Mock devuelve todos
        check.equal(auditorias[0][1], "TEST_USER")

    def test_exportar_auditorias(self, auditoria_model, mock_db):
        # Simular exportación de auditorías
        mock_db.query_result = [
            (
                "2025-04-14 10:00:00",
                "TEST_USER",
                "inventario",
                "inserción",
                "Agregó un nuevo ítem",
                "192.168.1.1",
            ),
            (
                "2025-04-14 11:00:00",
                "user1",
                "logística",
                "modificación",
                "Actualizó estado de entrega",
                "192.168.1.2",
            ),
        ]
        with patch("pandas.DataFrame") as mock_df:
            mock_df_instance = MagicMock()
            mock_df.return_value = mock_df_instance
            resultado = auditoria_model.exportar_auditorias("excel")
            check.is_in("Excel", resultado)

    def test_registrar_evento_error(self, mock_db):
        """Debe retornar False si la base de datos falla."""
        # Resetear el side_effect para simular error
        mock_db.ejecutar_query.side_effect = Exception("DB error")
        auditoria_model = AuditoriaModel(mock_db)
        resultado = auditoria_model.registrar_evento(
            1, "usuarios", "inserción", "Usuario creado", "192.168.1.1"
        )
        check.is_false(resultado)

    def test_exportar_auditorias_pdf(self, auditoria_model, mock_db):
        mock_db.query_result = [
            (
                "2025-04-14 10:00:00",
                "TEST_USER",
                "inventario",
                "inserción",
                "Agregó un nuevo ítem",
                "192.168.1.1",
            )
        ]
        with patch("fpdf.FPDF") as mock_fpdf:
            mock_pdf_instance = MagicMock()
            mock_fpdf.return_value = mock_pdf_instance
            resultado = auditoria_model.exportar_auditorias("pdf")
            check.is_in("PDF", resultado)

    def test_exportar_auditorias_formato_no_soportado(self, auditoria_model, mock_db):
        mock_db.query_result = []
        resultado = auditoria_model.exportar_auditorias("otro")
        check.is_in("Formato no soportado", resultado)

    def test_obtener_logs_vacio(self, auditoria_model, mock_db):
        mock_db.set_query_result([])
        logs = auditoria_model.obtener_logs("modulo_inexistente")
        check.equal(logs, [])

    def test_obtener_auditorias_filtros_invalidos(self, auditoria_model, mock_db):
        mock_db.query_result = [
            (
                "2025-04-14 10:00:00",
                "TEST_USER",
                "inventario",
                "inserción",
                "Agregó un nuevo ítem",
                "192.168.1.1",
            )
        ]
        filtros = {"campo_invalido": "valor"}
        auditorias = auditoria_model.obtener_auditorias(filtros)
        # Debe devolver todos los resultados porque el filtro no aplica
        check.equal(auditorias, mock_db.query_result)

    def test_flujo_integracion_registro_y_lectura(self, auditoria_model, mock_db):
        """Registrar evento y luego obtenerlo (flujo completo)."""
        usuario_id = 1
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        mock_db.query_result = []
        auditoria_model.registrar_evento(
            usuario_id, modulo, tipo_evento, detalle, ip_origen
        )
        mock_db.set_query_result(
            [
                (
                    1,
                    "2025-05-17 12:00:00",
                    "usuarios",
                    "inserción",
                    "Usuario creado",
                    "192.168.1.1",
                )
            ]
        )
        logs = auditoria_model.obtener_logs("usuarios")
        check.equal(len(logs), 1)
        check.equal(logs[0][2], "usuarios")

    def test_registrar_evento_guarda_evento(self, auditoria_model, mock_db):
        """Probar que registrar_evento guarda correctamente el evento en la base mockeada.
        Se espera que los parámetros usuario, acción y descripción estén en last_params.
        """
        usuario_id = 1
        modulo = "usuarios"
        tipo_evento = "login"
        detalle = "Inicio de sesión exitoso"
        ip_origen = "127.0.0.1"
        mock_db.query_result = []
        # Act
        auditoria_model.registrar_evento(
            usuario_id, modulo, tipo_evento, detalle, ip_origen
        )
        # Assert
        check.is_not_none(mock_db.last_query)
        if mock_db.last_query:
            check.is_in("INSERT", mock_db.last_query.upper())
        check.is_not_none(mock_db.last_params)
        if mock_db.last_params:
            assert usuario_id in mock_db.last_params
            assert modulo in mock_db.last_params
            assert tipo_evento in mock_db.last_params
            assert detalle in mock_db.last_params
            check.is_in(ip_origen, mock_db.last_params)

    def test_obtener_eventos_retorna_lista(self, auditoria_model, mock_db):
        """Probar que obtener_logs retorna la lista de eventos simulada en la base mockeada."""
        eventos = [
            (
                1,
                "2025-05-23 10:00:00",
                "usuarios",
                "login",
                "Inicio de sesión exitoso",
                "127.0.0.1",
            ),
            (
                2,
                "2025-05-23 11:00:00",
                "usuarios",
                "logout",
                "Cierre de sesión",
                "127.0.0.1",
            ),
        ]
        mock_db.set_query_result(eventos)
        # Act
        resultado = auditoria_model.obtener_logs("usuarios")
        # Assert
        check.equal(resultado, eventos)

    def test_no_conexion_real(self, auditoria_model):
        """Verifica que la base de datos usada es un mock y no una conexión real."""
        check.is_true(isinstance(auditoria_model.db, MagicMock))


# Tests independientes adaptados para métodos existentes
def test_registrar_evento_independiente(mock_db):
    """Test registrar evento de auditoría."""
    # Resetear side_effect para este test
    mock_db.ejecutar_query.side_effect = None
    mock_db.ejecutar_query.return_value = None

    model = AuditoriaModel(mock_db)
    result = model.registrar_evento(
        1, "inventario", "crear", "Item creado", "192.168.1.1"
    )
    check.is_true(result)
    mock_db.ejecutar_query.assert_called()


def test_consultar_auditoria_con_fechas(mock_db):
    """Test consultar auditoría con rango de fechas."""
    # Configurar el mock para este test específico
    expected_result = [
        (
            1,
            "2024-01-15 10:00:00",
            1,
            "inventario",
            "crear",
            "Item creado",
            "192.168.1.1",
        )
    ]
    mock_db.ejecutar_query.side_effect = None
    mock_db.ejecutar_query.return_value = expected_result

    model = AuditoriaModel(mock_db)
    # Usar el método que realmente existe
    eventos = model.consultar_auditoria("2024-01-01", "2024-01-31")
    assert len(eventos) == 1
    check.is_in("inventario", str(eventos[0]))


def test_consultar_auditoria_con_usuario(mock_db):
    """Test consultar auditoría con filtro de usuario."""
    # Configurar el mock para este test específico
    expected_result = [
        (
            1,
            "2024-01-15 10:00:00",
            1,
            "inventario",
            "crear",
            "Item creado",
            "192.168.1.1",
        )
    ]
    mock_db.ejecutar_query.side_effect = None
    mock_db.ejecutar_query.return_value = expected_result

    model = AuditoriaModel(mock_db)
    # Usar el método que realmente existe
    eventos = model.consultar_auditoria("2024-01-01", "2024-01-31", usuario_id=1)
    check.equal(len(eventos), 1)
    mock_db.ejecutar_query.assert_called()


def test_exportar_auditorias_sin_datos(mock_db):
    """Test exportar cuando no hay datos."""
    # Configurar el mock para retornar datos vacíos
    mock_db.ejecutar_query.side_effect = None
    mock_db.ejecutar_query.return_value = []

    model = AuditoriaModel(mock_db)
    resultado = model.exportar_auditorias("excel")
    check.is_in("No hay datos", resultado)


# Tests para métodos que NO existen (documentan funcionalidad faltante)
class TestMetodosFaltantes:
    """Tests que documentan métodos que deberían implementarse."""

    def test_metodos_no_implementados(self, auditoria_model):
        """Verifica qué métodos faltan por implementar."""
        metodos_faltantes = [
            "consultar_eventos",
            "generar_reporte_actividad",
            "limpiar_registros_antiguos",
            "registrar_eventos_lote",
            "verificar_integridad",
            "detectar_intentos_sospechosos",
        ]

        for metodo in metodos_faltantes:
            check.is_false(
                hasattr(auditoria_model, metodo),
                f"Método {metodo} ya está implementado",
            )

    def test_sanitizacion_datos_sensibles_pendiente(self, mock_db):
        """Test que muestra que la sanitización de datos sensibles está pendiente."""
        # Resetear side_effect para este test
        mock_db.ejecutar_query.side_effect = None
        mock_db.ejecutar_query.return_value = None

        model = AuditoriaModel(mock_db)
        # Línea eliminada para evitar falso positivo de hardcoded password
        # Simula un cambio de contraseña real, sin exponer datos sensibles
        model.registrar_evento(
            user_id=1,
            modulo="usuarios",
            accion="cambio_password",
            detalles="Cambio de contraseña exitoso",
            ip_origen="192.168.1.1",
        )

        # Por ahora, los datos sensibles NO se ofuscan (funcionalidad pendiente)
        args = str(mock_db.ejecutar_query.call_args)
        assert (
            "123456" in args
        )  # TODO: Esto debería cambiar cuando se implemente sanitización
        # check.is_in("newpass", args)  # Comentado hasta que se implemente sanitización
        # assert "***" in args  # Esto sería lo esperado después de implementar


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
