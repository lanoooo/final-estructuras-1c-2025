-- Usar la base de datos existente
USE padelclub;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'jugador') NOT NULL
);

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    cancha INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de emparejamientos
CREATE TABLE IF NOT EXISTS emparejamientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jugador1_id INT NOT NULL,
    jugador2_id INT DEFAULT NULL,
    fecha DATETIME NOT NULL,
    FOREIGN KEY (jugador1_id) REFERENCES usuarios(id),
    FOREIGN KEY (jugador2_id) REFERENCES usuarios(id)
);

-- Tabla de torneos
CREATE TABLE IF NOT EXISTS torneos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('singles', 'dobles') NOT NULL,
    fecha DATE NOT NULL,
    ubicacion VARCHAR(100)
);

-- Tabla de inscripciones a torneos
CREATE TABLE IF NOT EXISTS inscripciones_torneo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    torneo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 🔄 Eliminar las tablas si existen
DROP TABLE canchas;
DROP TABLE IF EXISTS canchas_dia_1;
DROP TABLE IF EXISTS canchas_dia_2;
DROP TABLE IF EXISTS canchas_dia_3;
DROP TABLE IF EXISTS canchas_dia_4;

-- 🛠 Crear estructura base para cada día (sin modo_emparejamiento)
CREATE TABLE canchas_dia_1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cancha_numero INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    personas_jugando INT NOT NULL DEFAULT 0 CHECK (personas_jugando IN (0, 1, 2, 4))
);

CREATE TABLE canchas_dia_2 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_3 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_4 LIKE canchas_dia_1;

-- 🕒 Insertar horarios en cada tabla usando CURDATE()
SET @fecha_base = CURDATE();

-- Día 1: Mañana
INSERT INTO canchas_dia_1 (cancha_numero, fecha_hora)
SELECT c.cancha, CONCAT(DATE_ADD(@fecha_base, INTERVAL 1 DAY), ' ', h.hora)
FROM
  (SELECT 1 AS cancha UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) c,
  (SELECT '12:00:00' AS hora UNION SELECT '16:00:00' UNION SELECT '17:00:00' UNION SELECT '18:00:00' UNION SELECT '19:00:00') h;

-- Día 2: Pasado mañana
INSERT INTO canchas_dia_2 (cancha_numero, fecha_hora)
SELECT c.cancha, CONCAT(DATE_ADD(@fecha_base, INTERVAL 2 DAY), ' ', h.hora)
FROM
  (SELECT 1 AS cancha UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) c,
  (SELECT '12:00:00' AS hora UNION SELECT '16:00:00' UNION SELECT '17:00:00' UNION SELECT '18:00:00' UNION SELECT '19:00:00') h;

-- Día 3
INSERT INTO canchas_dia_3 (cancha_numero, fecha_hora)
SELECT c.cancha, CONCAT(DATE_ADD(@fecha_base, INTERVAL 3 DAY), ' ', h.hora)
FROM
  (SELECT 1 AS cancha UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) c,
  (SELECT '12:00:00' AS hora UNION SELECT '16:00:00' UNION SELECT '17:00:00' UNION SELECT '18:00:00' UNION SELECT '19:00:00') h;

-- Día 4
INSERT INTO canchas_dia_4 (cancha_numero, fecha_hora)
SELECT c.cancha, CONCAT(DATE_ADD(@fecha_base, INTERVAL 4 DAY), ' ', h.hora)
FROM
  (SELECT 1 AS cancha UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) c,
  (SELECT '12:00:00' AS hora UNION SELECT '16:00:00' UNION SELECT '17:00:00' UNION SELECT '18:00:00' UNION SELECT '19:00:00') h;