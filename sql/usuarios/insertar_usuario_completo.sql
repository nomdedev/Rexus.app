INSERT INTO usuarios 
(usuario, password_hash, nombre_completo, email, telefono, rol, estado)
VALUES (:usuario, :password_hash, :nombre_completo, :email, :telefono, :rol, :estado)