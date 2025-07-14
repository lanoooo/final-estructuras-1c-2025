-- Script para crear las tablas de torneos
USE padelclub;
-- Tabla de torneos
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS torneos;
CREATE TABLE IF NOT EXISTS torneos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    max_equipos INT DEFAULT 8,
    estado ENUM('abierto', 'en_curso', 'finalizado') DEFAULT 'abierto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de equipos
DROP TABLE IF EXISTS equipos;
CREATE TABLE IF NOT EXISTS equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    torneo_id INT NOT NULL,
    nombre_equipo VARCHAR(100) NOT NULL,
    jugador1 VARCHAR(100) NOT NULL,
    jugador2 VARCHAR(100) NOT NULL,
    usuario_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_per_tournament (torneo_id, usuario_id)
);

-- Tabla de partidos
DROP TABLE IF EXISTS partidos;
CREATE TABLE IF NOT EXISTS partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    torneo_id INT NOT NULL,
    equipo1_id INT NOT NULL,
    equipo2_id INT NOT NULL,
    numero_partido INT NOT NULL,
    resultado_equipo1 INT DEFAULT NULL,
    resultado_equipo2 INT DEFAULT NULL,
    estado ENUM('pendiente', 'jugado', 'cancelado') DEFAULT 'pendiente',
    fecha_partido DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (equipo1_id) REFERENCES equipos(id) ON DELETE CASCADE,
    FOREIGN KEY (equipo2_id) REFERENCES equipos(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_torneos_fecha ON torneos(fecha);
CREATE INDEX idx_torneos_estado ON torneos(estado);
CREATE INDEX idx_equipos_torneo ON equipos(torneo_id);
CREATE INDEX idx_partidos_torneo ON partidos(torneo_id);
SET FOREIGN_KEY_CHECKS = 1;