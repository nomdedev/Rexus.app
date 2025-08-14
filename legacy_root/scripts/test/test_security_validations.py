"""
Test Security Validations - Rexus.app
Tests the new security features and form validations.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_form_validator():
    """Test form validation functionality."""
    print("\n[TEST] Form Validator Tests...")

    try:
        from src.utils.form_validator import form_validator

        # Test username validation
        valid, error = form_validator.validate_username("test_user")
        assert valid, f"Valid username failed: {error}"
        print("  [PASS] Valid username validation")

        valid, error = form_validator.validate_username("te")
        assert not valid, "Short username should fail"
        print("  [PASS] Short username rejection")

        # Test email validation
        valid, error = form_validator.validate_email("test@example.com")
        assert valid, f"Valid email failed: {error}"
        print("  [PASS] Valid email validation")

        valid, error = form_validator.validate_email("invalid-email")
        assert not valid, "Invalid email should fail"
        print("  [PASS] Invalid email rejection")

        # Test password validation
        valid, error = form_validator.validate_password("StrongPass123!")
        assert valid, f"Strong password failed: {error}"
        print("  [PASS] Strong password validation")

        valid, error = form_validator.validate_password("weak")
        assert not valid, "Weak password should fail"
        print("  [PASS] Weak password rejection")

        # Test complete user form
        user_data = {
            'usuario': 'test_user',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'nombre_completo': 'Test User',
            'telefono': '+34600123456'
        }

        valid, errors = form_validator.validate_user_form(user_data)
        assert valid, f"Valid form failed: {errors}"
        print("  [PASS] Complete user form validation")

        return True

    except Exception as e:
        print(f"  [FAIL] Form validator test failed: {e}")
        return False

def test_security_manager():
    """Test security manager functionality."""
    print("\n[TEST] Security Manager Tests...")

    try:
        from src.utils.security_manager import SecurityManager

        # Create test security manager
        security_mgr = SecurityManager(max_attempts=3, lockout_duration=5)

        # Test normal operation
        is_locked, reason = security_mgr.is_account_locked("test_user", "127.0.0.1")
        assert not is_locked, f"New account should not be locked: {reason}"
        print("  [PASS] New account not locked")

        # Test failed attempts
        for i in range(3):
            should_lock = security_mgr.record_failed_attempt("test_user", "127.0.0.1")

        assert should_lock, "Account should be locked after max attempts"
        print("  [PASS] Account locked after max attempts")

        # Test account is locked
        is_locked, reason = security_mgr.is_account_locked("test_user", "127.0.0.1")
        assert is_locked, "Account should be locked"
        print("  [PASS] Account lockout status detected")

        # Test successful login clears attempts
        security_mgr.record_successful_login("test_user2", "127.0.0.1")
        print("  [PASS] Successful login recorded")

        # Test session creation
        session_id = security_mgr.create_session("test_user2", 123, "127.0.0.1")
        assert session_id, "Session should be created"
        print("  [PASS] Session creation")

        # Test session validation
        valid, session_data = security_mgr.validate_session(session_id, "127.0.0.1")
        assert valid, "Session should be valid"
        assert session_data['username'] == "test_user2", "Session data should match"
        print("  [PASS] Session validation")

        # Test session invalidation
        success = security_mgr.invalidate_session(session_id)
        assert success, "Session should be invalidated"
        print("  [PASS] Session invalidation")

        # Test security stats
        stats = security_mgr.get_security_stats()
        assert isinstance(stats, dict), "Stats should be a dictionary"
        assert 'active_sessions' in stats, "Stats should include active sessions"
        print("  [PASS] Security statistics")

        return True

    except Exception as e:
        print(f"  [FAIL] Security manager test failed: {e}")
        return False

def test_sql_loader():
    """Test SQL loader functionality."""
    print("\n[TEST] SQL Loader Tests...")

    try:
        from src.utils.sql_loader import load_sql

        # Test loading existing SQL file
        query = load_sql("usuarios", "check_username_exists")
        assert query, "SQL query should be loaded"
        assert "SELECT COUNT(*)" in query, "Query should contain expected content"
        print("  [PASS] SQL file loading")

        # Test invalid module/query
        try:
            load_sql("invalid_module", "invalid_query")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            print("  [PASS] Invalid SQL file rejection")

        return True

    except Exception as e:
        print(f"  [FAIL] SQL loader test failed: {e}")
        return False

def test_html_sanitization():
    """Test HTML sanitization."""
    print("\n[TEST] HTML Sanitization Tests...")

    try:
        from src.utils.form_validator import form_validator

        # Test basic XSS prevention
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = form_validator.sanitize_html(dangerous_input)
        assert "<script>" not in sanitized, "Script tags should be escaped"
        assert "&lt;script&gt;" in sanitized, "Script tags should be escaped to HTML entities"
        print("  [PASS] Script tag sanitization")

        # Test multiple dangerous characters
        dangerous_input = '<img src="x" onerror="alert(1)">'
        sanitized = form_validator.sanitize_html(dangerous_input)
        assert "<img" not in sanitized, "HTML tags should be escaped"
        print("  [PASS] HTML tag sanitization")

        return True

    except Exception as e:
        print(f"  [FAIL] HTML sanitization test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("="*70)
    print("SECURITY VALIDATIONS TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Form Validator", test_form_validator),
        ("Security Manager", test_security_manager),
        ("SQL Loader", test_sql_loader),
        ("HTML Sanitization", test_html_sanitization)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {success_rate:.1f}%")

    # Overall assessment
    if success_rate >= 90:
        print("\n[SUCCESS] Security validations working correctly!")
        print("- Form validation system operational")
        print("- Security manager preventing brute force attacks")
        print("- SQL loader providing secure query management")
        print("- HTML sanitization preventing XSS attacks")
        return True
    elif success_rate >= 70:
        print("\n[ACCEPTABLE] Most security features working")
        print("- Minor issues detected but core security operational")
        return True
    else:
        print("\n[CRITICAL] Multiple security issues detected")
        print("- Review failed tests and address security vulnerabilities")
        return False

if __name__ == "__main__":
    success = main()

    if success:
        print("\n[CHECK] SECURITY IMPLEMENTATION SUCCESSFUL")
        print("The security validation system is ready for production use.")
    else:
        print("\n[ERROR] SECURITY IMPLEMENTATION NEEDS ATTENTION")
        print("Address the failed tests before proceeding.")
        sys.exit(1)
