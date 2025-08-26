-- select_2.sql
-- Extracted from: rexus\core\audit_trail.py
-- Line: 159

SELECT TOP {limit} * FROM (?) AS subquery ORDER BY fecha_cambio DESC