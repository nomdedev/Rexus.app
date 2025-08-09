"""
Script para corregir las llamadas incorrectas a registrar_evento en todos los controladores.
Convierte las llamadas que pasan el objeto usuario completo por las que pasan solo usuario_id.
"""

# Añadir el directorio raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def corregir_auditoria_controller(ruta_archivo):
    """
    import os
    import re
    import sys
        Corrige las llamadas a registrar_evento en un archivo de controlador.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_original = contenido

        # Patrón para encontrar la función PermisoAuditoria.__call__ con llamadas incorrectas
        patron_decorador = r"(def __call__\(self, accion\):.*?def wrapper\(controller, \*args, \*\*kwargs\):.*?)(\s+auditoria_model\.registrar_evento\(usuario, self\.modulo, accion\))(\s+return resultado\s+except Exception as e:\s+)(\s+auditoria_model\.registrar_evento\(usuario, self\.modulo, accion\))"

        # Reemplazo para corregir las llamadas
        def reemplazar_auditoria(match):
            inicio = match.group(1)
            primer_llamada = match.group(2)
            medio = match.group(3)
            segunda_llamada = match.group(4)

            # Generar el reemplazo correcto
            nuevo_contenido = inicio
            nuevo_contenido += "\n                    usuario_id = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)"
            nuevo_contenido += "\n                    ip = usuario.get('ip', '') if isinstance(usuario, dict) else getattr(usuario, 'ip', '')"
            nuevo_contenido += '\n                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, f"Acción {accion} exitosa", ip)'
            nuevo_contenido += medio
            nuevo_contenido += "\n                    usuario_id = usuario.get('id') if isinstance(usuario, dict) else getattr(usuario, 'id', None)"
            nuevo_contenido += "\n                    ip = usuario.get('ip', '') if isinstance(usuario, dict) else getattr(usuario, 'ip', '')"
            nuevo_contenido += '\n                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, f"Error en acción {accion}: {str(e)}", ip)'

            return nuevo_contenido

        # Aplicar corrección si se encuentra el patrón
        contenido_corregido = re.sub(
            patron_decorador, reemplazar_auditoria, contenido, flags=re.DOTALL
        )

        # Si no se aplicó la corrección con el patrón completo, buscar patrones más simples
        if contenido_corregido == contenido:
            # Buscar llamadas simples a registrar_evento con 3 parámetros
            patron_simple = (
                r"auditoria_model\.registrar_evento\(usuario, ([^,]+), ([^)]+)\)"
            )

            def reemplazar_simple(match):
                modulo = match.group(1)
                accion = match.group(2)
                return f'auditoria_model.registrar_evento(usuario.get("id") if isinstance(usuario, dict) else getattr(usuario, "id", None), {modulo}, {accion}, f"Acción {{usuario.get("usuario", "desconocido") if isinstance(usuario, dict) else getattr(usuario, "usuario", "desconocido")}}", usuario.get("ip", "") if isinstance(usuario, dict) else getattr(usuario, "ip", ""))'

            contenido_corregido = re.sub(patron_simple, reemplazar_simple, contenido)

        # Solo escribir si hubo cambios
        if contenido_corregido != contenido_original:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(contenido_corregido)
            print(f"[CHECK] Corregido: {ruta_archivo}")
            return True
        else:
            print(f"⏭️  No necesita corrección: {ruta_archivo}")
            return False

    except Exception as e:
        print(f"[ERROR] Error procesando {ruta_archivo}: {e}")
        return False


def main():
    """
    Función principal que busca y corrige todos los controladores.
    """
    print("🔧 Iniciando corrección de llamadas a registrar_evento...")

    # Buscar todos los archivos controller.py en modules/
    directorio_modules = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "modules"
    )
    archivos_corregidos = 0

    for root, dirs, files in os.walk(directorio_modules):
        for file in files:
            if file == "controller.py":
                ruta_completa = os.path.join(root, file)
                if corregir_auditoria_controller(ruta_completa):
                    archivos_corregidos += 1

    print(f"\n[CHART] Resumen:")
    print(f"   • Archivos corregidos: {archivos_corregidos}")
    print(f"[CHECK] Corrección completada")


if __name__ == "__main__":
    main()
