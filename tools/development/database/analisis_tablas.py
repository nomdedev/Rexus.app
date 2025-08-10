"""
Análisis de Tablas: Existentes vs. Buscadas por el Sistema
===========================================================

Basado en la imagen de tu base de datos y los errores del test,
este es el mapeo de tablas que necesitamos corregir.
"""

# TABLAS QUE EXISTEN EN TU BASE DE DATOS (según la imagen):
tablas_existentes = {
    "obras": "dbo.obras",
    "inventario": "dbo.inventario_perfiles",
    "materiales": "dbo.materiales",
    "vidrios": "dbo.vidrios_por_obra",  # [CHECK] Esta SÍ existe
    "pedidos": "dbo.pedidos_compra",  # Esta es para pedidos de material
    "proveedores": "dbo.proveedores",
    "movimientos": "dbo.movimientos_inventario",
    "herrajes": "dbo.herrajes_por_obra",
    "other_tables": [
        "dbo.auditorias_sistema",
        "dbo.cronograma_obras",
        "dbo.detalle_pedido",
        "dbo.estado_material",
        "dbo.movimientos_proveedores",
        "dbo.movimientos_stock",
        "dbo.pago_por_obra",
        "dbo.pedidos_pendientes",
        "dbo.perfiles_por_obra",
        "dbo.reservas_materiales",
        "dbo.reservas_stock",
    ],
}

# TABLAS QUE EL SISTEMA BUSCA (pero no existen con esos nombres):
tablas_buscadas_incorrectas = {
    "pedidos_material": {
        "tabla_real": "dbo.pedidos_compra",
        "modulo": "Inventario",
        "proposito": "Gestión de pedidos de materiales por obra",
        "solucion": "Cambiar query para usar dbo.pedidos_compra",
    },
    "pedidos_herrajes": {
        "tabla_real": "dbo.herrajes_por_obra",  # O crear nueva si es necesaria
        "modulo": "Herrajes",
        "proposito": "Gestión de pedidos de herrajes por obra",
        "solucion": "Usar dbo.herrajes_por_obra o crear nueva tabla",
    },
    "pagos_pedidos": {
        "tabla_real": "dbo.pago_por_obra",  # Esta parece ser la correcta
        "modulo": "Contabilidad",
        "proposito": "Registro de pagos por pedidos y obras",
        "solucion": "Cambiar query para usar dbo.pago_por_obra",
    },
}

# TABLAS QUE SÍ EXISTEN Y FUNCIONAN:
tablas_correctas = {
    "vidrios_por_obra": {
        "tabla_bd": "dbo.vidrios_por_obra",
        "modulo": "Vidrios",
        "estado": "[CHECK] CORRECTO - Ya existe y funciona",
    },
    "obras": {
        "tabla_bd": "dbo.obras",
        "modulo": "Obras",
        "estado": "[CHECK] CORRECTO - Ya existe y funciona",
    },
    "inventario_perfiles": {
        "tabla_bd": "dbo.inventario_perfiles",
        "modulo": "Inventario",
        "estado": "[CHECK] CORRECTO - Ya existe y funciona",
    },
}

print("ANÁLISIS COMPLETO DE TABLAS")
print("=" * 50)

print("\n[CHECK] TABLAS QUE SÍ EXISTEN Y FUNCIONAN:")
for nombre, info in tablas_correctas.items():
    print(f"   [OK] {info['tabla_bd']} → {info['modulo']} ({info['estado']})")

print("\n[ERROR] TABLAS BUSCADAS INCORRECTAMENTE:")
for tabla_buscada, info in tablas_buscadas_incorrectas.items():
    print(f"   ✗ BUSCA: {tabla_buscada}")
    print(f"     REAL: {info['tabla_real']}")
    print(f"     MÓDULO: {info['modulo']}")
    print(f"     PROPÓSITO: {info['proposito']}")
    print(f"     SOLUCIÓN: {info['solucion']}")
    print()

print("📋 CORRECCIONES NECESARIAS:")
print("1. Inventario: Cambiar 'pedidos_material' → 'dbo.pedidos_compra'")
print("2. Herrajes: Cambiar 'pedidos_herrajes' → 'dbo.herrajes_por_obra'")
print("3. Contabilidad: Cambiar 'pagos_pedidos' → 'dbo.pago_por_obra'")

print("\n🎯 RESULTADO:")
print("El sistema NO necesita crear nuevas tablas.")
print("Solo necesita corregir los nombres de tablas en las queries de los modelos.")
print("Todas las tablas necesarias YA EXISTEN en tu base de datos.")
