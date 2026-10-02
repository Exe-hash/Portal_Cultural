-- Ejecutar una vez desde phpMyAdmin o desde el cliente de MySQL/MariaDB.
-- Las tablas se crean después con: python manage.py migrate
CREATE DATABASE IF NOT EXISTS portal_cultural
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Reemplace los valores antes de usar estas sentencias en EC2:
-- CREATE USER 'portal_cultural_user'@'localhost' IDENTIFIED BY 'CONTRASENA_SEGURA';
-- GRANT ALL PRIVILEGES ON portal_cultural.* TO 'portal_cultural_user'@'localhost';
-- FLUSH PRIVILEGES;
