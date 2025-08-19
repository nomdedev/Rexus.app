UPDATE herrajes_obra
SET cantidad_pedida = cantidad_pedida + ?
WHERE herraje_id = ? AND obra_id = ?;