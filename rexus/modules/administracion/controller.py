"""
Controlador de Administración

Controlador principal para el módulo de administración
Integra los submódulos de contabilidad y recursos humanos
Maneja la comunicación entre modelos y vistas
Integrado con el sistema de seguridad global
"""

import json
import os
from datetime import datetime

from PyQt6.QtCore import QObject, QTimer, pyqtSlot

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("administracion.controller")
except ImportError:
    class DummyLogger:
        def info(self, msg): logger.debug(f"[INFO] {msg}")
        def warning(self, msg): logger.warning(f"[WARNING] {msg}")
        def error(self, msg): logger.error(f"[ERROR] {msg}")
        def debug(self, msg): logger.debug(f"[DEBUG] {msg}")
    logger = DummyLogger()


from rexus.core.security import get_security_manager

# Importar submódulos
from .contabilidad import ContabilidadModel, ContabilidadController
from .recursos_humanos import RecursosHumanosModel, RecursosHumanosController

class AdministracionController(QObject):
    """Controlador principal del módulo de administración."""

    def __init__(self,
model=None,
        view=None,
        db_connection=None,
        usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.security_manager = get_security_manager()

        # Obtener usuario y rol actual del sistema de seguridad
        self.usuario_actual = (
            self.security_manager.get_current_user()
            if self.security_manager
            else "SISTEMA"
        )
        self.rol_actual = (
            self.security_manager.get_current_role()
            if self.security_manager
            else "ADMIN"
        )

        # Configurar el modelo con la conexión
        if self.model and self.db_connection:
            self.model.db_connection = self.db_connection
            self.model.usuario_actual = self.usuario_actual

        # Inicializar submódulos
        self.inicializar_submodulos()

        # Conectar señales
        self.conectar_senales()

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if not self.view:
            return

        # Señales principales
        self.view.crear_departamento_signal.connect(self.crear_departamento)
        self.view.crear_empleado_signal.connect(self.crear_empleado)
        self.view.crear_asiento_signal.connect(self.crear_asiento_contable)
        self.view.crear_recibo_signal.connect(self.crear_recibo)
        self.view.imprimir_recibo_signal.connect(self.imprimir_recibo)
        self.view.generar_reporte_signal.connect(self.generar_reporte)
        self.view.actualizar_datos_signal.connect(self.actualizar_datos)

        # Timer para actualización automática
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(30000)  # Actualizar cada 30 segundos

    def inicializar_submodulos(self):
        """Inicializa los submódulos de contabilidad y recursos humanos."""
        try:
            # Inicializar submódulo de contabilidad
            self.contabilidad_model = ContabilidadModel(self.db_connection)
            self.contabilidad_controller = ContabilidadController(
                model=self.contabilidad_model,
                view=self.view,
                db_connection=self.db_connection
            )

            # Inicializar submódulo de recursos humanos
            self.recursos_humanos_model = RecursosHumanosModel(self.db_connection)
            self.recursos_humanos_controller = RecursosHumanosController(
                model=self.recursos_humanos_model,
                view=self.view,
                db_connection=self.db_connection
            )

            # Conectar señales entre submódulos
            self.conectar_senales_submodulos()

            logger.info("[ADMINISTRACIÓN] Submódulos inicializados correctamente")

        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error inicializando submódulos: {e}")

    def conectar_senales_submodulos(self):
        """Conecta las señales entre los submódulos."""
        try:
            # Conectar señales del submódulo de contabilidad
            if self.contabilidad_controller:
                self.contabilidad_controller.estadisticas_actualizadas.connect(
                    self.actualizar_estadisticas_generales
                )
                self.contabilidad_controller.reporte_generado.connect(
                    self.manejar_reporte_generado
                )

            # Conectar señales del submódulo de recursos humanos
            if self.recursos_humanos_controller:
                self.recursos_humanos_controller.nomina_calculada.connect(
                    self.manejar_nomina_calculada
                )
                self.recursos_humanos_controller.empleado_agregado.connect(
                    self.manejar_empleado_agregado
                )

        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error conectando señales de submódulos: {e}")

    def actualizar_estadisticas_generales(self, estadisticas):
        """Actualiza las estadísticas generales con datos de los submódulos."""
        try:
            if self.view:
                self.view.actualizar_estadisticas_generales(estadisticas)
        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error actualizando estadísticas generales: {e}")

    def manejar_reporte_generado(self, archivo_reporte):
        """Maneja la generación de reportes de los submódulos."""
        try:
            if self.view:
                self.view.mostrar_mensaje("Reporte", f"Reporte generado: {archivo_reporte}", "info")
        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error manejando reporte: {e}")

    def manejar_nomina_calculada(self, nomina_data):
        """Maneja el cálculo de nómina del submódulo de RRHH."""
        try:
            if self.view:
                self.view.mostrar_mensaje("Nómina", f"Nómina calculada para {len(nomina_data)} empleados", "info")
        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error manejando nómina: {e}")

    def manejar_empleado_agregado(self, empleado_data):
        """Maneja la adición de empleados del submódulo de RRHH."""
        try:
            # Actualizar estadísticas y datos relacionados
            self.actualizar_datos()
        except Exception as e:
            logger.error(f"[ERROR ADMINISTRACIÓN] Error manejando empleado agregado: {e}")

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        try:
            self.actualizar_datos()
            if self.view:
                self.view.actualizar_status("[CHECK] Datos cargados exitosamente")
        except Exception as e:
            logger.debug(f"Error cargando datos iniciales: {e}")
            if self.view:
                self.view.actualizar_status(f"[ERROR] Error cargando datos: {str(e)}")

    @pyqtSlot()
    def actualizar_datos(self):
        """Actualiza todos los datos de la interfaz."""
        try:
            if not self.model or not self.view:
                return

            # Actualizar dashboard
            self.actualizar_dashboard()

            # Actualizar tablas
            self.actualizar_libro_contable()
            self.actualizar_recibos()
            self.actualizar_pagos_obra()
            self.actualizar_materiales()
            self.actualizar_departamentos()
            self.actualizar_empleados()
            self.actualizar_auditoria()

            if self.view:
                self.view.actualizar_status("🔄 Datos actualizados")

        except Exception as e:
            logger.debug(f"Error actualizando datos: {e}")
            if self.view:
                self.view.actualizar_status(f"[ERROR] Error actualizando: {str(e)}")

    def actualizar_dashboard(self):
        """Actualiza el dashboard con resumen de datos."""
        try:
            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_dashboard")
                return

            # Obtener resumen contable
            resumen = self.model.obtener_resumen_contable()

            if resumen and self.view:
                self.view.actualizar_dashboard({"resumen": resumen})

        except Exception as e:
            logger.debug(f"Error actualizando dashboard: {e}")

    def actualizar_libro_contable(self):
        """Actualiza la tabla del libro contable."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_libro_contable")
                return

            # Obtener fechas de filtro
            fecha_desde = self.view.libro_fecha_desde.date().toPython()
            fecha_hasta = self.view.libro_fecha_hasta.date().toPython()

            # Obtener tipo de filtro
            tipo_filtro = self.view.libro_tipo_combo.currentText()
            tipo_asiento = None if tipo_filtro == "Todos" else tipo_filtro

            # Obtener asientos
            asientos = self.model.obtener_libro_contable(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                tipo_asiento=tipo_asiento,
            )

            # Actualizar tabla
            self.view.actualizar_tabla_libro(asientos)

        except Exception as e:
            logger.debug(f"Error actualizando libro contable: {e}")

    def actualizar_recibos(self):
        """Actualiza la tabla de recibos."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_recibos")
                return

            # Obtener fechas de filtro
            fecha_desde = self.view.recibos_fecha_desde.date().toPython()
            fecha_hasta = self.view.recibos_fecha_hasta.date().toPython()

            # Obtener tipo de filtro
            tipo_filtro = self.view.recibos_tipo_combo.currentText()
            tipo_recibo = None if tipo_filtro == "Todos" else tipo_filtro

            # Obtener recibos
            recibos = self.model.obtener_recibos(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                tipo_recibo=tipo_recibo,
            )

            # Actualizar tabla
            self.view.actualizar_tabla_recibos(recibos)

        except Exception as e:
            logger.debug(f"Error actualizando recibos: {e}")

    def actualizar_pagos_obra(self):
        """Actualiza la tabla de pagos por obra."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_pagos_obra")
                return

            # Obtener filtros
            categoria_filtro = self.view.pagos_categoria_combo.currentText()
            categoria = None if categoria_filtro == "Todas" else categoria_filtro

            # Obtener pagos
            pagos = self.model.obtener_pagos_obra(categoria=categoria)

            # Actualizar tabla (método a implementar en la vista)
            # self.view.actualizar_tabla_pagos_obra(pagos)

        except Exception as e:
            logger.debug(f"Error actualizando pagos por obra: {e}")

    def actualizar_materiales(self):
        """Actualiza la tabla de materiales."""
        try:
            if not self.view:
                return

            # Obtener filtros
            estado_filtro = self.view.materiales_estado_combo.currentText()
            estado = None if estado_filtro == "Todos" else estado_filtro

            # Obtener materiales (método a implementar en el modelo)
            # materiales = self.model.obtener_pagos_materiales(estado_pago=estado)

            # Actualizar tabla (método a implementar en la vista)
            # self.view.actualizar_tabla_materiales(materiales)

        except Exception as e:
            logger.debug(f"Error actualizando materiales: {e}")

    def actualizar_departamentos(self):
        """Actualiza la tabla de departamentos."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_departamentos")
                return

            # Obtener departamentos
            self.model.obtener_departamentos()

            # Actualizar tabla (método a implementar en la vista)
            # self.view.actualizar_tabla_departamentos(departamentos)

        except Exception as e:
            logger.debug(f"Error actualizando departamentos: {e}")

    def actualizar_empleados(self):
        """Actualiza la tabla de empleados."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_empleados")
                return

            # Obtener filtros
            departamento_filtro = self.view.empleados_departamento_combo.currentText()
            departamento_id = (
                None
                if departamento_filtro == "Todos los departamentos"
                else departamento_filtro
            )

            # Obtener empleados
            empleados = self.model.obtener_empleados(departamento_id=departamento_id)

            # Actualizar tabla (método a implementar en la vista)
            # self.view.actualizar_tabla_empleados(empleados)

        except Exception as e:
            logger.debug(f"Error actualizando empleados: {e}")

    def actualizar_auditoria(self):
        """Actualiza la tabla de auditoría."""
        try:
            if not self.view:
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en actualizar_auditoria")
                return

            # Obtener filtros
            tabla_filtro = self.view.auditoria_tabla_combo.currentText()
            tabla = None if tabla_filtro == "Todas" else tabla_filtro

            usuario_filtro = self.view.auditoria_usuario_combo.currentText()
            usuario = None if usuario_filtro == "Todos" else usuario_filtro

            # Obtener auditoría
            auditoria = self.model.obtener_auditoria(tabla=tabla, usuario=usuario)

            # Actualizar tabla (método a implementar en la vista)
            # self.view.actualizar_tabla_auditoria(auditoria)

        except Exception as e:
            logger.debug(f"Error actualizando auditoría: {e}")

    # MÉTODOS PARA CREAR REGISTROS
    @pyqtSlot(dict)
    def crear_departamento(self, datos):
        """Crea un nuevo departamento."""
        try:
            if not self.verificar_permisos("crear_departamento"):
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en crear_departamento")
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "Modelo no disponible", "error"
                    )
                return

            departamento_id = self.model.crear_departamento(
                codigo=datos["codigo"],
                nombre=datos["nombre"],
                descripcion=datos.get("descripcion", ""),
                responsable=datos.get("responsable", ""),
                presupuesto_mensual=datos.get("presupuesto_mensual", 0),
            )

            if departamento_id:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Éxito",
                        f"Departamento '{datos['nombre']}' creado exitosamente",
                        "info",
                    )
                self.actualizar_departamentos()
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudo crear el departamento", "error"
                    )

        except Exception as e:
            logger.debug(f"Error creando departamento: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error creando departamento: {str(e)}", "error"
                )

    @pyqtSlot(dict)
    def crear_empleado(self, datos):
        """Crea un nuevo empleado."""
        try:
            if not self.verificar_permisos("crear_empleado"):
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en crear_empleado")
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "Modelo no disponible", "error"
                    )
                return

            empleado_id = self.model.crear_empleado(
                codigo=datos["codigo"],
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                documento=datos["documento"],
                email=datos.get("email", ""),
                telefono=datos.get("telefono", ""),
                departamento_id=datos.get("departamento_id"),
                cargo=datos.get("cargo", ""),
                salario=datos.get("salario", 0),
                fecha_ingreso=datos.get("fecha_ingreso"),
            )

            if empleado_id:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Éxito",
                        f"Empleado '{datos['nombre']} {datos['apellido']}' creado exitosamente",
                        "info",
                    )
                self.actualizar_empleados()
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudo crear el empleado", "error"
                    )

        except Exception as e:
            logger.debug(f"Error creando empleado: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error creando empleado: {str(e)}", "error"
                )

    @pyqtSlot(dict)
    def crear_asiento_contable(self, datos):
        """Crea un nuevo asiento contable."""
        try:
            if not self.verificar_permisos("crear_asiento"):
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en crear_asiento_contable")
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "Modelo no disponible", "error"
                    )
                return

            asiento_id = self.model.crear_asiento_contable(
                fecha_asiento=datos["fecha_asiento"],
                tipo_asiento=datos["tipo_asiento"],
                concepto=datos["concepto"],
                referencia=datos.get("referencia", ""),
                obra_id=datos.get("obra_id"),
                proveedor_id=datos.get("proveedor_id"),
                empleado_id=datos.get("empleado_id"),
                departamento_id=datos.get("departamento_id"),
                cuenta_contable=datos.get("cuenta_contable", ""),
                debe=datos.get("debe", 0),
                haber=datos.get("haber", 0),
                observaciones=datos.get("observaciones", ""),
            )

            if asiento_id:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Éxito", f"Asiento contable creado exitosamente", "info"
                    )
                self.actualizar_libro_contable()
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudo crear el asiento contable", "error"
                    )

        except Exception as e:
            logger.debug(f"Error creando asiento contable: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error creando asiento: {str(e)}", "error"
                )

    @pyqtSlot(dict)
    def crear_recibo(self, datos):
        """Crea un nuevo recibo."""
        try:
            if not self.verificar_permisos("crear_recibo"):
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en crear_recibo")
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "Modelo no disponible", "error"
                    )
                return

            recibo_id = self.model.crear_recibo(
                fecha_emision=datos["fecha_emision"],
                tipo_recibo=datos["tipo_recibo"],
                concepto=datos["concepto"],
                beneficiario=datos["beneficiario"],
                monto=datos["monto"],
                obra_id=datos.get("obra_id"),
                proveedor_id=datos.get("proveedor_id"),
                empleado_id=datos.get("empleado_id"),
                moneda=datos.get("moneda", "ARS"),
                metodo_pago=datos.get("metodo_pago", "EFECTIVO"),
                numero_comprobante=datos.get("numero_comprobante", ""),
                observaciones=datos.get("observaciones", ""),
            )

            if recibo_id:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Éxito", f"Recibo creado exitosamente", "info"
                    )
                self.actualizar_recibos()
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudo crear el recibo", "error"
                    )

        except Exception as e:
            logger.debug(f"Error creando recibo: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error creando recibo: {str(e)}", "error"
                )

    @pyqtSlot(int)
    def imprimir_recibo(self, recibo_id):
        """Imprime un recibo y lo marca como impreso."""
        try:
            if not self.verificar_permisos("imprimir_recibo"):
                return

            if not self.model:
                logger.info("[ERROR] self.model es None en imprimir_recibo")
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "Modelo no disponible", "error"
                    )
                return

            # Generar PDF del recibo
            archivo_pdf = self.generar_pdf_recibo(recibo_id)

            if archivo_pdf:
                # Marcar como impreso
                if self.model.marcar_recibo_impreso(recibo_id, archivo_pdf):
                    if self.view:
                        self.view.mostrar_mensaje(
                            "Éxito",
                            f"Recibo impreso y guardado como: {archivo_pdf}",
                            "info",
                        )
                    self.actualizar_recibos()
                else:
                    if self.view:
                        self.view.mostrar_mensaje(
                            "Error", "No se pudo marcar el recibo como impreso", "error"
                        )
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudo generar el archivo PDF", "error"
                    )

        except Exception as e:
            logger.debug(f"Error imprimiendo recibo: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error imprimiendo recibo: {str(e)}", "error"
                )

    def generar_pdf_recibo(self, recibo_id):
        """Genera un archivo PDF del recibo."""
        try:
            if not self.model:
                logger.info("[ERROR] self.model es None en generar_pdf_recibo")
                return None

            # Obtener datos del recibo
            recibos = self.model.obtener_recibos()
            recibo = None

            for r in recibos:
                if r["id"] == recibo_id:
                    recibo = r
                    break

            if not recibo:
                return None

            # Crear directorio para recibos si no existe
            recibos_dir = os.path.join(os.getcwd(), "recibos")
            if not os.path.exists(recibos_dir):
                os.makedirs(recibos_dir)

            # Nombre del archivo
            archivo_pdf = os.path.join(
                recibos_dir, f"recibo_{recibo['numero_recibo']}.pdf"
            )

            # Aquí se implementaría la generación del PDF
            # Por ahora, crear un archivo placeholder
            with open(archivo_pdf, "w") as f:
                f.write(f"Recibo: {recibo['numero_recibo']}\n")
                f.write(f"Fecha: {recibo['fecha_emision']}\n")
                f.write(f"Concepto: {recibo['concepto']}\n")
                f.write(f"Beneficiario: {recibo['beneficiario']}\n")
                f.write(f"Monto: ${recibo['monto']:,.2f}\n")

            return archivo_pdf

        except Exception as e:
            logger.debug(f"Error generando PDF: {e}")
            return None

    @pyqtSlot(dict)
    def generar_reporte(self, parametros):
        """Genera un reporte según los parámetros especificados."""
        try:
            if not self.verificar_permisos("generar_reporte"):
                return

            tipo_reporte = parametros.get("tipo")
            formato = parametros.get("formato", "PDF")
            fecha_desde = parametros.get("fecha_desde")
            fecha_hasta = parametros.get("fecha_hasta")

            # Generar datos del reporte según el tipo
            datos_reporte = self.obtener_datos_reporte(
                tipo_reporte, fecha_desde, fecha_hasta
            )

            if datos_reporte:
                # Generar archivo del reporte
                archivo_reporte = self.generar_archivo_reporte(
                    datos_reporte, tipo_reporte, formato
                )

                if archivo_reporte:
                    if self.view:
                        self.view.mostrar_mensaje(
                            "Éxito", f"Reporte generado: {archivo_reporte}", "info"
                        )
                else:
                    if self.view:
                        self.view.mostrar_mensaje(
                            "Error",
                            "No se pudo generar el archivo del reporte",
                            "error",
                        )
            else:
                if self.view:
                    self.view.mostrar_mensaje(
                        "Error", "No se pudieron obtener los datos del reporte", "error"
                    )

        except Exception as e:
            logger.debug(f"Error generando reporte: {e}")
            if self.view:
                self.view.mostrar_mensaje(
                    "Error", f"Error generando reporte: {str(e)}", "error"
                )

    def obtener_datos_reporte(self, tipo_reporte, fecha_desde, fecha_hasta):
        """Obtiene los datos para el reporte especificado."""
        try:
            if not self.model:
                logger.info("[ERROR] self.model es None en obtener_datos_reporte")
                return None

            if tipo_reporte == "libro_contable":
                return self.model.obtener_libro_contable(fecha_desde, fecha_hasta)
            elif tipo_reporte == "recibos":
                return self.model.obtener_recibos(fecha_desde, fecha_hasta)
            elif tipo_reporte == "pagos_obra":
                return self.model.obtener_pagos_obra(
                    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
                )
            elif tipo_reporte == "departamentos":
                return self.model.obtener_departamentos()
            elif tipo_reporte == "empleados":
                return self.model.obtener_empleados()
            elif tipo_reporte == "auditoria":
                return self.model.obtener_auditoria(
                    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
                )
            elif tipo_reporte == "resumen_ejecutivo":
                return self.model.obtener_resumen_contable(fecha_desde, fecha_hasta)
            else:
                return None

        except Exception as e:
            logger.debug(f"Error obteniendo datos del reporte: {e}")
            return None

    def generar_archivo_reporte(self, datos, tipo_reporte, formato):
        """Genera el archivo del reporte en el formato especificado."""
        try:
            # Crear directorio para reportes si no existe
            reportes_dir = os.path.join(os.getcwd(), "reportes")
            if not os.path.exists(reportes_dir):
                os.makedirs(reportes_dir)

            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = os.path.join(
                reportes_dir, f"reporte_{tipo_reporte}_{timestamp}.{formato.lower()}"
            )

            # Generar archivo según el formato
            if formato == "PDF":
                return self.generar_pdf_reporte(datos, archivo, tipo_reporte)
            elif formato == "Excel":
                return self.generar_excel_reporte(datos, archivo, tipo_reporte)
            elif formato == "CSV":
                return self.generar_csv_reporte(datos, archivo, tipo_reporte)
            else:
                return None

        except Exception as e:
            logger.debug(f"Error generando archivo del reporte: {e}")
            return None

    def generar_pdf_reporte(self, datos, archivo, tipo_reporte):
        """Genera un reporte en formato PDF."""
        try:
            # Placeholder para generación de PDF
            with open(archivo, "w") as f:
                f.write(f"Reporte de {tipo_reporte}\n")
                f.write(f"Generado el: {datetime.now()}\n")
                f.write(f"Datos: {json.dumps(datos, indent=2, default=str)}\n")

            return archivo

        except Exception as e:
            logger.debug(f"Error generando PDF: {e}")
            return None

    def generar_excel_reporte(self, datos, archivo, tipo_reporte):
        """Genera un reporte en formato Excel."""
        try:
            # Placeholder para generación de Excel
            archivo_txt = archivo.replace(".xlsx", ".txt")
            with open(archivo_txt, "w") as f:
                f.write(f"Reporte de {tipo_reporte} (Excel)\n")
                f.write(f"Generado el: {datetime.now()}\n")
                f.write(f"Datos: {json.dumps(datos, indent=2, default=str)}\n")

            return archivo_txt

        except Exception as e:
            logger.debug(f"Error generando Excel: {e}")
            return None

    def generar_csv_reporte(self, datos, archivo, tipo_reporte):
        """Genera un reporte en formato CSV."""
        try:
            # Placeholder para generación de CSV
            archivo_csv = archivo.replace(".csv", ".txt")
            with open(archivo_csv, "w") as f:
                f.write(f"Reporte de {tipo_reporte} (CSV)\n")
                f.write(f"Generado el: {datetime.now()}\n")
                f.write(f"Datos: {json.dumps(datos, indent=2, default=str)}\n")

            return archivo_csv

        except Exception as e:
            logger.debug(f"Error generando CSV: {e}")
            return None

    def verificar_permisos(self, accion):
        """Verifica si el usuario actual tiene permisos para la acción."""
        try:
            # Implementar lógica de permisos según el rol
            permisos_admin = [
                "crear_departamento",
                "crear_empleado",
                "crear_asiento",
                "crear_recibo",
                "imprimir_recibo",
                "generar_reporte",
                "exportar_datos",
            ]

            permisos_supervisor = [
                "crear_asiento",
                "crear_recibo",
                "imprimir_recibo",
                "generar_reporte",
            ]

            permisos_usuario = ["crear_recibo", "imprimir_recibo"]

            if self.rol_actual == "ADMIN":
                return accion in permisos_admin
            elif self.rol_actual == "SUPERVISOR":
                return accion in permisos_supervisor
            elif self.rol_actual == "USUARIO":
                return accion in permisos_usuario
            else:
                return False

        except Exception as e:
            logger.debug(f"Error verificando permisos: {e}")
            return False

    def establecer_usuario(self, usuario, rol):
        """Establece el usuario y rol actual."""
        self.usuario_actual = usuario
        self.rol_actual = rol

        if self.model:
            self.model.usuario_actual = usuario

        if self.view:
            self.view.current_user = usuario
            self.view.current_role = rol

    def obtener_estadisticas_departamento(self, departamento_id):
        """Obtiene estadísticas de un departamento específico."""
        try:
            if not self.model:
                logger.info("[ERROR] self.model es None en obtener_estadisticas_departamento")
                return None
            return self.model.obtener_estadisticas_departamento(departamento_id)
        except Exception as e:
            logger.debug(f"Error obteniendo estadísticas de departamento: {e}")
            return None

    def exportar_datos(self, tipo_datos, formato="JSON"):
        """
        Exporta datos del sistema en diferentes formatos.
        """
        try:
            if not self.verificar_permisos("exportar_datos"):
                return None
            if not self.model:
                logger.info("[ERROR] self.model es None en exportar_datos")
                return None
            # Obtener datos según el tipo
            if tipo_datos == "completo":
                datos = {
                    "libro_contable": self.model.obtener_libro_contable(limite=None),
                    "recibos": self.model.obtener_recibos(limite=None),
                    "departamentos": self.model.obtener_departamentos(),
                    "empleados": self.model.obtener_empleados(),
                    "auditoria": self.model.obtener_auditoria(limite=None),
                }
            elif tipo_datos == "libro_contable":
                datos = self.model.obtener_libro_contable(limite=None)
            elif tipo_datos == "recibos":
                datos = self.model.obtener_recibos(limite=None)
            else:
                return None

            # Crear archivo de exportación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"exportacion_{tipo_datos}_{timestamp}.{formato.lower()}"

            with open(archivo, "w", encoding="utf-8") as f:
                if formato == "JSON":
                    json.dump(datos,
f,
                        indent=2,
                        ensure_ascii=False,
                        default=str)
                else:
                    f.write(str(datos))

            return archivo

        except Exception as e:
            logger.debug(f"Error exportando datos: {e}")
            return None
