# SECURITY REQUIREMENTS - REXUS.APP

## CRITICAL SECURITY RULE: DATABASE SCHEMA MANAGEMENT

### ❌ NEVER CREATE TABLES FROM APPLICATION CODE

**SECURITY RISK**: Creating tables from application code is a **GRAVE SECURITY VULNERABILITY** that can lead to:
- SQL injection attacks
- Schema manipulation attacks
- Data integrity issues
- Privilege escalation
- Database corruption

### ✅ CORRECT APPROACH

1. **ALL DATABASE TABLES MUST BE CREATED MANUALLY** before application deployment
2. **USE DEDICATED SQL SCRIPTS** for schema creation and migrations
3. **APPLICATION CODE MUST ONLY ACCESS EXISTING TABLES** - never create them
4. **SEPARATE SCHEMA MANAGEMENT** from application runtime code

### 🔧 IMPLEMENTATION RULES

#### For Developers:
- Remove all `_crear_tablas_si_no_existen()` methods from models
- Remove all `CREATE TABLE` statements from application code
- Use only `SELECT`, `INSERT`, `UPDATE`, `DELETE` with parameterized queries
- Verify table existence only - never create tables if they don't exist

#### For Database Administrators:
- Create all required tables using dedicated SQL scripts
- Grant appropriate permissions to application users
- Use migrations scripts for schema changes
- Document all table schemas in SQL files

### 📋 AFFECTED FILES (TO BE CLEANED)

Files that currently have table creation code that must be removed:
- `src/modules/herrajes/model.py` - Remove `_crear_tablas_si_no_existen()`
- `src/modules/inventario/model.py` - Remove `_crear_tablas_si_no_existen()`
- `src/modules/mantenimiento/model.py` - Remove table creation code
- `src/modules/administracion/recursos_humanos/model.py` - Remove table creation code
- `src/modules/administracion/contabilidad/model.py` - Remove table creation code
- `src/core/audit_trail.py` - Remove `_create_audit_table_if_not_exists()`

### 🛠️ REPLACEMENT STRATEGY

Instead of creating tables from code:

```python
# ❌ WRONG - SECURITY RISK
def _crear_tablas_si_no_existen(self):
    cursor.execute("CREATE TABLE IF NOT EXISTS...")

# ✅ CORRECT - SECURITY COMPLIANT
def _verificar_tablas(self):
    """Verifica que las tablas requeridas existan (solo verificación)"""
    cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (tabla,))
    if not cursor.fetchone():
        raise RuntimeError(f"Required table '{tabla}' does not exist. Please create it manually.")
```

### 🚨 IMMEDIATE ACTIONS REQUIRED

1. **Remove all table creation code** from application
2. **Create SQL migration scripts** for required tables
3. **Update documentation** to reflect manual table creation requirement
4. **Test application** with pre-created tables only

**DATE**: 2025-01-17
**PRIORITY**: CRITICAL
**STATUS**: IN PROGRESS

---

**Remember**: Security is not negotiable. Tables must be created manually by database administrators, not by application code.