DELETE FROM herrajes_obra 
WHERE herraje_id = (SELECT id FROM herrajes WHERE codigo = @codigo)
