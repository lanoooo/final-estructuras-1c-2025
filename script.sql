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
