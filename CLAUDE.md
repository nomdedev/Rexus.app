# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py  # Main entry point (from rexus/main/main.py)
python rexus/main/main.py  # Alternative direct run
```

### Testing
```bash
pytest  # Uses config from config/environments/pytest.ini
python -m pytest tests/  # Run all tests
python -m pytest tests/modules/obras/  # Run specific module tests
PYTHONPATH=. python scripts/test/test_logistica_ascii.py  # Run specific test script
```

### Code Quality
```bash
python -m black .  # Code formatting
python -m isort .  # Import sorting
python -m flake8  # Linting
python -m mypy .  # Type checking
python -m bandit -r rexus/  # Security scanning
```

### Database Operations
```bash
python tools/development/database/diagnostico_db.py  # Database diagnostics
python scripts/database/execute_database_migration.py  # Database migrations
python tools/development/testing/verificar_tablas_bd.py  # Verify database tables
```

## Architecture

Rexus.app is a PyQt6-based desktop application following strict **MVC (Model-View-Controller)** architecture:

### Core Structure
- **Entry Point**: `rexus/main/main.py` → `rexus.main.app.main()`
- **Main App**: `rexus/main/app.py` contains the PyQt6 application and module manager
- **Modules**: Business logic modules in `rexus/modules/` (inventario, obras, usuarios, etc.)
- **Core**: System services in `rexus/core/` (auth, database, security, logging)
- **Utils**: Shared utilities in `rexus/utils/`

### Database Architecture
The application uses **3 separate databases**:
1. **users**: Authentication, permissions, and user management ONLY
2. **inventario**: All business data (products, works, orders, materials, etc.)
3. **auditoria**: Audit trails and critical event logging

**CRITICAL**: Never mix business data in 'users' or user data in 'inventario'.

### MVC Pattern Rules
**Model** (`model.py`):
- Database connections and CRUD operations
- Business logic and data validation
- SQL queries and data processing
- NO PyQt6 imports, NO UI components

**View** (`view.py`):
- PyQt6 widgets, layouts, and UI components
- User interaction handling
- Data presentation and formatting
- NO direct database access, NO SQL queries

**Controller** (`controller.py`):
- Coordinates between Model and View
- Application flow and state management
- Input validation and error handling
- Lightweight - delegates heavy work to Model

### Module Structure
Each business module follows this pattern:
```
rexus/modules/{module_name}/
├── __init__.py
├── model.py      # Data layer
├── view.py       # UI layer
├── controller.py # Logic coordinator
└── {sub_modules}/# Optional sub-modules
```

### Security Implementation
- **SQL Injection Prevention**: All queries use parameterized statements
- **Authentication**: Login through `rexus.core.login_dialog.LoginDialog`
- **Authorization**: Role-based access control via `rexus.core.rbac_system`
- **Audit Trail**: All operations logged to auditoria database
- **Password Security**: bcrypt hashing for user passwords

### Key Components
- **Module Manager**: `rexus.core.module_manager` handles dynamic module loading
- **Database**: `rexus.core.database` provides connection management for all 3 databases
- **Authentication**: `rexus.core.auth_manager` handles login/logout flows
- **Theme System**: `rexus.ui.styles` and QSS files in `resources/qss/`

### SQL Scripts Organization
- **Business Queries**: `scripts/sql/{module_name}/` contains module-specific SQL
- **Common Queries**: `scripts/sql/common/` for shared operations
- **Database Setup**: `scripts/database/` for schema creation and migrations

### Testing Strategy
- **Module Tests**: `tests/{module_name}/` for unit and integration tests
- **Security Tests**: Focused on SQL injection, XSS, and auth vulnerabilities
- **UI Tests**: PyQt6 interaction testing with pytest-qt
- **Mock Database**: `tests/mock_db.py` for isolated testing

### Development Tools
- **Maintenance**: `tools/development/maintenance/` for code analysis and cleanup
- **Security**: `tools/development/security/` for vulnerability scanning
- **Database**: `tools/development/database/` for schema validation and migration

## Important Notes

### Code Quality Standards
- All models must be free of PyQt6 imports
- All views must avoid direct SQL execution
- Controllers should remain lightweight coordinators
- Use parameterized queries exclusively
- Follow Python type hints throughout

### Database Connection Patterns
```python
# Correct: Use appropriate database for context
from rexus.core.database import get_users_connection  # For auth
from rexus.core.database import get_inventario_connection  # For business data
from rexus.core.database import get_auditoria_connection  # For logging
```

### Security Practices
- Never hardcode credentials
- Always validate user input
- Use prepared statements for SQL
- Log security events to auditoria database
- Implement proper error handling without information leakage

### File Organization
- Production code in `rexus/` package structure
- Development tools in `tools/`
- Tests in `tests/` mirroring source structure
- Documentation in `docs/` with comprehensive guides
- SQL scripts in `scripts/sql/` organized by module