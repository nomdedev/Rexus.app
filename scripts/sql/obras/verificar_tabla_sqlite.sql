-- Verifica si una tabla existe en SQLite
SELECT name FROM sqlite_master WHERE type='table' AND name=?