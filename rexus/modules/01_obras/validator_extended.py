#!/usr/bin/env python3
"""
VALIDADOR EXTENDIDO PARA OBRAS
=============================

Validaciones completas y robustas para el módulo obras.
Incluye validaciones de seguridad, sanitización y reglas de negocio.
"""


import logging
logger = logging.getLogger(__name__)

import re
from datetime import datetime, date
from typing import Dict, List, Tuple, Any


class ObrasValidatorExtended:
    """Validador extendido para obras con todas las reglas de negocio."""

    # Patrones para validación
    PATRON_CODIGO = re.compile(r'^OBR-\d{3,6}$')
    PATRON_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PATRON_TELEFONO = re.compile(r'^[\+]?[1-9][\d]{0,15}$')

    # Patrones de seguridad
    PATRONES_XSS = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe.*?>',
        r'<object.*?>',
        r'<embed.*?>',
        r'<link.*?>',
        r'<meta.*?>',
        r'vbscript:',
        r'data:text/html'
    ]

    PATRONES_SQL_INJECTION = [
        r"'.*?(or|and).*?'",
        r'(union|select|insert|update|delete|drop|create|alter)[\s\(]',
        r';[\s]*drop',
        r';[\s]*delete',
        r'--[\s]*',
        r'/\*.*?\*/',
        r'xp_cmdshell',
        r'sp_executesql'
    ]

    @classmethod
    def validar_obra_completa(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """
        Validación completa de una obra con todas las reglas.

        Args:
            obra_dict: Diccionario con datos de la obra

        Returns:
            Tupla (es_valida, lista_errores)
        """
        errores = []

        # Validaciones básicas
        es_valida_basica, errores_basicos = cls._validar_campos_basicos(obra_dict)
        errores.extend(errores_basicos)

        # Validaciones de formato
        es_valida_formato, errores_formato = cls._validar_formatos(obra_dict)
        errores.extend(errores_formato)

        # Validaciones de seguridad
        es_valida_seguridad, errores_seguridad = cls._validar_seguridad(obra_dict)
        errores.extend(errores_seguridad)

        # Validaciones de negocio
        es_valida_negocio, errores_negocio = cls._validar_reglas_negocio(obra_dict)
        errores.extend(errores_negocio)

        # Validaciones de integridad
        es_valida_integridad, errores_integridad = cls._validar_integridad(obra_dict)
        errores.extend(errores_integridad)

        es_valida = (es_valida_basica and es_valida_formato and
                    es_valida_seguridad and es_valida_negocio and es_valida_integridad)

        return es_valida, errores

    @classmethod
    def _validar_campos_basicos(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """Validar campos básicos requeridos."""
        errores = []

        # Campos obligatorios
        campos_obligatorios = [
            'codigo', 'nombre', 'cliente', 'responsable',
            'fecha_inicio', 'estado', 'presupuesto_inicial'
        ]

        for campo in campos_obligatorios:
            valor = obra_dict.get(campo)
            if not valor or (isinstance(valor, str) and not valor.strip()):
                errores.append(f"El campo '{campo}' es obligatorio")

        # Validar longitudes
        longitudes_maximas = {
            'codigo': 20,
            'nombre': 200,
            'descripcion': 2000,
            'cliente': 150,
            'responsable': 100,
            'ubicacion': 300,
            'tipo_construccion': 50,
            'materiales_especiales': 500,
            'observaciones': 1000,
            'contacto_cliente': 200
        }

        for campo, max_length in longitudes_maximas.items():
            valor = obra_dict.get(campo, '')
            if isinstance(valor, str) and len(valor) > max_length:
                errores.append(f"El campo '{campo}' no puede exceder {max_length} caracteres")

        # Validar longitudes mínimas
        longitudes_minimas = {
            'codigo': 5,
            'nombre': 3,
            'cliente': 2,
            'responsable': 5
        }

        for campo, min_length in longitudes_minimas.items():
            valor = obra_dict.get(campo, '')
            if isinstance(valor, str) and valor.strip() and len(valor.strip()) < min_length:
                errores.append(f"El campo '{campo}' debe tener al menos {min_length} caracteres")

        return len(errores) == 0, errores

    @classmethod
    def _validar_formatos(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """Validar formatos específicos."""
        errores = []

        # Validar código de obra
        codigo = obra_dict.get('codigo', '')
        if codigo and not cls.PATRON_CODIGO.match(codigo):
            errores.append("El código debe tener formato OBR-XXX (ej: OBR-001)")

        # Validar fechas
        fechas_a_validar = [
            'fecha_inicio', 'fecha_fin_estimada', 'fecha_contrato',
            'fecha_entrega_contractual'
        ]

        for campo_fecha in fechas_a_validar:
            fecha_str = obra_dict.get(campo_fecha)
            if fecha_str:
                try:
                    if isinstance(fecha_str, str):
                        datetime.strptime(fecha_str, '%Y-%m-%d')
                    elif not isinstance(fecha_str, (date, datetime)):
                        errores.append(f"Formato de fecha inválido en '{campo_fecha}'")
                except ValueError:
                    errores.append(f"Formato de fecha inválido en '{campo_fecha}' (usar YYYY-MM-DD)")

        # Validar números positivos
        campos_numericos_positivos = [
            'presupuesto_inicial', 'area_construccion', 'numero_pisos',
            'garantia_meses', 'seguro_obra', 'anticipo_recibido'
        ]

        for campo in campos_numericos_positivos:
            valor = obra_dict.get(campo)
            if valor is not None:
                try:
                    valor_float = float(valor)
                    if valor_float < 0:
                        errores.append(f"El campo '{campo}' debe ser un número positivo")
                except (ValueError, TypeError):
                    errores.append(f"El campo '{campo}' debe ser un número válido")

        # Validar porcentajes
        campos_porcentaje = ['porcentaje_avance', 'penalizaciones', 'bonificaciones']

        for campo in campos_porcentaje:
            valor = obra_dict.get(campo)
            if valor is not None:
                try:
                    valor_float = float(valor)
                    if valor_float < 0 or valor_float > 100:
                        errores.append(f"El campo '{campo}' debe estar entre 0 y 100%")
                except (ValueError, TypeError):
                    errores.append(f"El campo '{campo}' debe ser un número válido")

        # Validar estados válidos
        estados_validos = [
            'PLANIFICACION', 'EN_PROCESO', 'SUSPENDIDA',
            'FINALIZADA', 'CANCELADA'
        ]
        estado = obra_dict.get('estado', '').upper()
        if estado and estado not in estados_validos:
            errores.append(f"Estado inválido. Valores permitidos: {', '.join(estados_validos)}")

        # Validar niveles de riesgo
        niveles_riesgo_validos = ['BAJO', 'MEDIO', 'ALTO', 'CRITICO']
        riesgo = obra_dict.get('riesgo_nivel', '').upper()
        if riesgo and riesgo not in niveles_riesgo_validos:
            errores.append(f"Nivel de riesgo inválido. Valores permitidos: {', '.join(niveles_riesgo_validos)}")

        # Validar prioridades
        prioridades_validas = ['BAJA', 'MEDIA', 'ALTA', 'URGENTE']
        prioridad = obra_dict.get('prioridad', '').upper()
        if prioridad and prioridad not in prioridades_validas:
            errores.append(f"Prioridad inválida. Valores permitidos: {', '.join(prioridades_validas)}")

        return len(errores) == 0, errores

    @classmethod
    def _validar_seguridad(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """Validar aspectos de seguridad."""
        errores = []

        # Campos de texto a validar
        campos_texto = [
            'nombre', 'descripcion', 'cliente', 'responsable',
            'ubicacion', 'materiales_especiales', 'observaciones',
            'contacto_cliente'
        ]

        for campo in campos_texto:
            valor = obra_dict.get(campo, '')
            if isinstance(valor, str):
                # Detectar XSS
                if cls._detectar_xss(valor):
                    errores.append(f"Contenido potencialmente peligroso detectado en '{campo}'")

                # Detectar SQL Injection
                if cls._detectar_sql_injection(valor):
                    errores.append(f"Posible intento de inyección SQL en '{campo}'")

        return len(errores) == 0, errores

    @classmethod
    def _validar_reglas_negocio(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """Validar reglas específicas del negocio."""
        errores = []

        # Validar fechas lógicas
        fecha_inicio_str = obra_dict.get('fecha_inicio')
        fecha_fin_str = obra_dict.get('fecha_fin_estimada')

        if fecha_inicio_str and fecha_fin_str:
            try:
                if isinstance(fecha_inicio_str, str):
                    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                else:
                    fecha_inicio = fecha_inicio_str

                if isinstance(fecha_fin_str, str):
                    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                else:
                    fecha_fin = fecha_fin_str

                if fecha_fin <= fecha_inicio:
                    errores.append("La fecha de fin debe ser posterior a la fecha de inicio")

                # Validar duración razonable (máximo 10 años)
                duracion_dias = (fecha_fin - fecha_inicio).days
                if duracion_dias > 3650:  # 10 años
                    errores.append("La duración de la obra excede el límite máximo de 10 años")

            except ValueError:
                pass  # Errores de formato ya se manejan en _validar_formatos

        # Validar presupuesto vs anticipo
        presupuesto = obra_dict.get('presupuesto_inicial')
        anticipo = obra_dict.get('anticipo_recibido')

        if presupuesto and anticipo:
            try:
                presupuesto_float = float(presupuesto)
                anticipo_float = float(anticipo)

                if anticipo_float > presupuesto_float:
                    errores.append("El anticipo no puede ser mayor al presupuesto inicial")

                # Validar porcentaje de anticipo razonable (máximo 50%)
                porcentaje_anticipo = (anticipo_float / presupuesto_float) * 100
                if porcentaje_anticipo > 50:
                    errores.append("El anticipo no puede exceder el 50% del presupuesto")

            except (ValueError, TypeError, ZeroDivisionError):
                pass

        # Validar número de pisos razonable
        pisos = obra_dict.get('numero_pisos')
        if pisos:
            try:
                pisos_int = int(pisos)
                if pisos_int > 200:  # Límite razonable
                    errores.append("El número de pisos excede el límite razonable (200)")
            except (ValueError, TypeError):
                pass

        # Validar área de construcción razonable
        area = obra_dict.get('area_construccion')
        if area:
            try:
                area_float = float(area)
                if area_float > 1000000:  # 1 millón de m²
                    errores.append("El área de construcción excede el límite razonable (1,000,000 m²)")
            except (ValueError, TypeError):
                pass

        return len(errores) == 0, errores

    @classmethod
    def _validar_integridad(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        List[str]]:
        """Validar integridad de datos."""
        errores = []

        # Validar coherencia entre estado y porcentaje de avance
        estado = obra_dict.get('estado', '').upper()
        porcentaje_avance = obra_dict.get('porcentaje_avance')

        if estado and porcentaje_avance is not None:
            try:
                avance_float = float(porcentaje_avance)

                if estado == 'PLANIFICACION' and avance_float > 0:
                    errores.append("Una obra en planificación no debería tener avance")
                elif estado == 'FINALIZADA' and avance_float < 100:
                    errores.append("Una obra finalizada debe tener 100% de avance")
                elif estado == 'CANCELADA' and avance_float == 100:
                    errores.append("Una obra cancelada no puede tener 100% de avance")

            except (ValueError, TypeError):
                pass

        # Validar que obra finalizada tenga fecha de fin
        if estado == 'FINALIZADA':
            fecha_fin = obra_dict.get('fecha_fin_real')
            if not fecha_fin:
                errores.append("Una obra finalizada debe tener fecha de finalización real")

        return len(errores) == 0, errores

    @classmethod
    def _detectar_xss(cls, texto: str) -> bool:
        """Detectar posibles ataques XSS."""
        if not texto:
            return False

        texto_lower = texto.lower()

        for patron in cls.PATRONES_XSS:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return True

        return False

    @classmethod
    def _detectar_sql_injection(cls, texto: str) -> bool:
        """Detectar posibles inyecciones SQL."""
        if not texto:
            return False

        texto_lower = texto.lower()

        for patron in cls.PATRONES_SQL_INJECTION:
            if re.search(patron, texto_lower, re.IGNORECASE):
                return True

        return False

    @classmethod
    def sanitizar_texto(cls, texto: str) -> str:
        """
        Sanitizar texto para prevenir ataques.

        Args:
            texto: Texto a sanitizar

        Returns:
            Texto sanitizado
        """
        if not texto or not isinstance(texto, str):
            return ""

        # Remover caracteres peligrosos
        texto_limpio = texto.strip()

        # Escapar caracteres HTML
        escapes_html = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }

        for caracter, escape in escapes_html.items():
            texto_limpio = texto_limpio.replace(caracter, escape)

        # Remover caracteres de control
        texto_limpio = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto_limpio)

        return texto_limpio

    @classmethod
    def validar_y_sanitizar(cls,
obra_dict: Dict[str,
        Any]) -> Tuple[bool,
        Dict[str,
        Any],
        List[str]]:
        """
        Validar y sanitizar una obra completa.

        Args:
            obra_dict: Datos de la obra

        Returns:
            Tupla (es_valida, obra_sanitizada, errores)
        """
        # Primero sanitizar
        obra_sanitizada = {}

        # Campos de texto a sanitizar
        campos_texto = [
            'codigo', 'nombre', 'descripcion', 'cliente', 'responsable',
            'ubicacion', 'tipo_construccion', 'materiales_especiales',
            'observaciones', 'contacto_cliente'
        ]

        for campo, valor in obra_dict.items():
            if campo in campos_texto and isinstance(valor, str):
                obra_sanitizada[campo] = cls.sanitizar_texto(valor)
            else:
                obra_sanitizada[campo] = valor

        # Luego validar
        es_valida, errores = cls.validar_obra_completa(obra_sanitizada)

        return es_valida, obra_sanitizada, errores
