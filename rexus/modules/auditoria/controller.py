"""
Controlador de Auditoría

Maneja la lógica entre el modelo y la vista de auditoría.
"""

import csv
import os
from datetime import datetime

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from rexus.core.auth_manager import auth_required, admin_required, manager_required


class AuditoriaController(QObject):
    """Controlador para el módulo de auditoría."""

    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializa el controlador de auditoría.

        Args:
            model: Modelo de auditoría
            view: Vista de auditoría
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

        if self.view:
            self._conectar_senales()
            self._cargar_datos_iniciales()

    def _conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if not self.view:
            return

        # Conectar señales de la vista
        self.view.filtrar_solicitud.connect(self.filtrar_registros)
        self.view.exportar_solicitud.connect(self.exportar_datos)
        self.view.limpiar_solicitud.connect(self.limpiar_registros_antiguos)

    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        if not self.model or not self.view:
            return

        try:
            # Cargar registros recientes
            registros = self.model.obtener_registros(limite=100)
            self.view.actualizar_registros(registros)

            # Cargar estadísticas
            estadisticas = self.model.obtener_estadisticas()
            self.view.actualizar_estadisticas(estadisticas)

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error cargando datos iniciales: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    f"Error cargando datos de auditoría: {e}", tipo="error"
                )

    def filtrar_registros(self, filtros):
        """
        Filtra los registros según los criterios especificados.

        Args:
            filtros (dict): Diccionario con los filtros aplicar
        """
        if not self.model or not self.view:
            return

        try:
            # Extraer filtros
            fecha_inicio = filtros.get("fecha_inicio")
            fecha_fin = filtros.get("fecha_fin")
            usuario = filtros.get("usuario", "")
            modulo = filtros.get("modulo", "")
            criticidad = filtros.get("criticidad", "")

            # Obtener registros filtrados
            registros = self.model.obtener_registros(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                usuario=usuario,
                modulo=modulo,
                nivel_criticidad=criticidad,
                limite=1000,
            )

            # Actualizar vista
            self.view.actualizar_registros(registros)

            # Registrar la búsqueda
            self.registrar_accion(
                accion="CONSULTA_AUDITORIA",
                descripcion=f"Filtros aplicados: {len(registros)} registros encontrados",
            )

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error filtrando registros: {e}")
            self.view.mostrar_mensaje(f"Error aplicando filtros: {e}", tipo="error")

    def exportar_datos(self, formato="csv"):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('exportar_datos'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """
        Exporta los datos de auditoría a un archivo.

        Args:
            formato (str): Formato de exportación (csv, excel)
        """
        if not self.model or not self.view:
            return

        try:
            # Solicitar ubicación del archivo
            if formato.lower() == "csv":
                archivo, _ = QFileDialog.getSaveFileName(
                    self.view,
                    "Exportar Auditoría",
                    f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "Archivos CSV (*.csv)",
                )
            else:
                archivo, _ = QFileDialog.getSaveFileName(
                    self.view,
                    "Exportar Auditoría",
                    f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "Archivos Excel (*.xlsx)",
                )

            if not archivo:
                return

            # Obtener todos los registros visibles actualmente
            registros = self.model.obtener_registros(limite=10000)

            if formato.lower() == "csv":
                self._exportar_csv(registros, archivo)
            else:
                self._exportar_excel(registros, archivo)

            # Registrar la exportación
            self.registrar_accion(
                accion="EXPORTAR_AUDITORIA",
                descripcion=f"Exportados {len(registros)} registros a {formato.upper()}",
                nivel_criticidad="MEDIA",
            )

            self.view.mostrar_mensaje(
                f"Datos exportados exitosamente a:\n{archivo}", tipo="success"
            )

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error exportando: {e}")
            self.view.mostrar_mensaje(f"Error exportando datos: {e}", tipo="error")

    def _exportar_csv(self, registros, archivo):
        """Exporta registros a formato CSV."""
        with open(archivo, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Escribir encabezados
            headers = [
                "ID",
                "Fecha/Hora",
                "Usuario",
                "Módulo",
                "Acción",
                "Descripción",
                "Tabla Afectada",
                "Registro ID",
                "Criticidad",
                "Resultado",
            ]
            writer.writerow(headers)

            # Escribir datos
            for registro in registros:
                row = [
                    registro.get("id", ""),
                    registro.get("fecha_hora", ""),
                    registro.get("usuario", ""),
                    registro.get("modulo", ""),
                    registro.get("accion", ""),
                    registro.get("descripcion", ""),
                    registro.get("tabla_afectada", ""),
                    registro.get("registro_id", ""),
                    registro.get("nivel_criticidad", ""),
                    registro.get("resultado", ""),
                ]
                writer.writerow(row)

    def _exportar_excel(self, registros, archivo):
        """Exporta registros a formato Excel."""
        try:
            import pandas as pd

            # Convertir registros a DataFrame
            df = pd.DataFrame(registros)

            # Seleccionar y renombrar columnas
            columnas_deseadas = {
                "id": "ID",
                "fecha_hora": "Fecha/Hora",
                "usuario": "Usuario",
                "modulo": "Módulo",
                "accion": "Acción",
                "descripcion": "Descripción",
                "tabla_afectada": "Tabla Afectada",
                "registro_id": "Registro ID",
                "nivel_criticidad": "Criticidad",
                "resultado": "Resultado",
            }

            df_export = df[list(columnas_deseadas.keys())].rename(
                columns=columnas_deseadas
            )

            # Exportar a Excel
            df_export.to_excel(archivo, index=False, engine="openpyxl")

        except ImportError:
            raise Exception("pandas y openpyxl son requeridos para exportar a Excel")

    def limpiar_registros_antiguos(self, dias):
        """
        Limpia registros de auditoría antiguos.

        Args:
            dias (int): Días de antigüedad para eliminar
        """
        if not self.model:
            return

        try:
            # Confirmar acción crítica
            reply = QMessageBox.question(
                self.view,
                "Confirmar Limpieza Crítica",
                f"¿Está seguro de eliminar registros anteriores a {dias} días?\n\n"
                "Esta acción NO se puede deshacer.\n"
                "Los registros críticos se conservarán.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Realizar limpieza
            success = self.model.limpiar_registros_antiguos(dias)

            if success:
                self.view.mostrar_mensaje(
                    f"Limpieza completada. Registros anteriores a {dias} días eliminados.",
                    tipo="success",
                )

                # Recargar datos
                self._cargar_datos_iniciales()

            else:
                self.view.mostrar_mensaje(
                    "Error realizando la limpieza de registros.", tipo="error"
                )

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error limpiando registros: {e}")
            self.view.mostrar_mensaje(f"Error limpiando registros: {e}", tipo="error")

    def registrar_accion(
        self,
        accion,
        descripcion="",
        tabla_afectada="",
        registro_id="",
        valores_anteriores=None,
        valores_nuevos=None,
        nivel_criticidad="MEDIA",
        resultado="EXITOSO",
    ):
        """
        Registra una acción en el sistema de auditoría.

        Args:
            accion (str): Tipo de acción realizada
            descripcion (str): Descripción detallada
            tabla_afectada (str): Tabla de BD afectada
            registro_id (str): ID del registro afectado
            valores_anteriores (dict): Valores antes del cambio
            valores_nuevos (dict): Valores después del cambio
            nivel_criticidad (str): Nivel de criticidad
            resultado (str): Resultado de la operación
        """
        if not self.model:
            return False

        try:
            return self.model.registrar_accion(
                usuario=self.usuario_actual,
                modulo="AUDITORÍA",
                accion=accion,
                descripcion=descripcion,
                tabla_afectada=tabla_afectada,
                registro_id=registro_id,
                valores_anteriores=valores_anteriores,
                valores_nuevos=valores_nuevos,
                nivel_criticidad=nivel_criticidad,
                resultado=resultado,
            )
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error registrando acción: {e}")
            return False

    def actualizar_estadisticas(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza las estadísticas mostradas en la vista."""
        if not self.model or not self.view:
            return

        try:
            estadisticas = self.model.obtener_estadisticas()
            self.view.actualizar_estadisticas(estadisticas)
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error actualizando estadísticas: {e}")

    def buscar_por_tabla(self, tabla, registro_id=None):
        """
        Busca registros de auditoría por tabla específica.

        Args:
            tabla (str): Nombre de la tabla
            registro_id (str): ID específico del registro (opcional)

        Returns:
            List: Lista de registros encontrados
        """
        if not self.model:
            return []

        try:
            registros = self.model.obtener_registros(limite=1000)

            # Filtrar por tabla
            registros_filtrados = [
                r
                for r in registros
                if r.get("tabla_afectada", "").lower() == tabla.lower()
            ]

            # Filtrar por registro_id si se especifica
            if registro_id:
                registros_filtrados = [
                    r
                    for r in registros_filtrados
                    if r.get("registro_id") == str(registro_id)
                ]

            return registros_filtrados

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error buscando por tabla: {e}")
            return []

    def obtener_resumen_usuario(self, usuario, dias=30):
        """
        Obtiene un resumen de actividad de un usuario específico.

        Args:
            usuario (str): Nombre del usuario
            dias (int): Días hacia atrás para analizar

        Returns:
            dict: Resumen de actividad del usuario
        """
        if not self.model:
            return {}

        try:
            import datetime

            fecha_inicio = datetime.date.today() - datetime.timedelta(days=dias)

            registros = self.model.obtener_registros(
                fecha_inicio=fecha_inicio, usuario=usuario, limite=1000
            )

            # Analizar registros
            total_acciones = len(registros)
            modulos_usados = list(set(r.get("modulo", "") for r in registros))
            acciones_por_dia = {}

            for registro in registros:
                fecha = registro.get("fecha_hora")
                if isinstance(fecha, datetime.datetime):
                    dia = fecha.date()
                    acciones_por_dia[dia] = acciones_por_dia.get(dia, 0) + 1

            return {
                "usuario": usuario,
                "total_acciones": total_acciones,
                "modulos_usados": modulos_usados,
                "acciones_por_dia": acciones_por_dia,
                "periodo_dias": dias,
            }

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error obteniendo resumen usuario: {e}")
            return {}
