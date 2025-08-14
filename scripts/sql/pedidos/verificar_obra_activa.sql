-- Verificar si una obra está activa
SELECT COUNT(*) FROM obras WHERE id = ? AND activo = 1