USE padelclub;

-- Si hay restricciones de FK que impiden el DROP, desactívalas temporalmente:
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS inscripciones_torneo;
DROP TABLE IF EXISTS torneos;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS reservas;

-- Vuelve a activar las comprobaciones de FK:
SET FOREIGN_KEY_CHECKS = 1;