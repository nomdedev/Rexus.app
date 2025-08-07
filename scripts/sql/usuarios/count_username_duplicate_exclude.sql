SELECT COUNT(*) FROM usuarios 
WHERE LOWER(username) = ? AND id != ?