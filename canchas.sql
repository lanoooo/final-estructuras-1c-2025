-- ------------------------------------------------------------------
-- script.sql: Creación de tablas de canchas y evento de actualización
-- ------------------------------------------------------------------

-- 1) Activar el scheduler de eventos
SET GLOBAL event_scheduler = ON;

USE padelclub;

-- 2) Eliminar tablas y evento previos
DROP EVENT IF EXISTS actualizar_canchas;
DROP TABLE IF EXISTS canchas_dia_1;
DROP TABLE IF EXISTS canchas_dia_2;
DROP TABLE IF EXISTS canchas_dia_3;
DROP TABLE IF EXISTS canchas_dia_4;

-- 3) Crear tablas para días 1–4, con DEFAULT 0 en personas_jugando
CREATE TABLE canchas_dia_1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cancha_numero TINYINT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    personas_jugando TINYINT NOT NULL DEFAULT 0
        CHECK (personas_jugando IN (0,1,2,4))
);
CREATE TABLE canchas_dia_2 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_3 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_4 LIKE canchas_dia_1;

-- 4) Población inicial de las 5 franjas horarias para cada cancha

-- Día 1
TRUNCATE TABLE canchas_dia_1;
INSERT INTO canchas_dia_1 (cancha_numero, fecha_hora)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), ' ', h.h)
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
      UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
      UNION ALL SELECT '19:00:00') AS h;

-- Día 2
TRUNCATE TABLE canchas_dia_2;
INSERT INTO canchas_dia_2 (cancha_numero, fecha_hora)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 2 DAY), ' ', h.h)
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
      UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
      UNION ALL SELECT '19:00:00') AS h;

-- Día 3
TRUNCATE TABLE canchas_dia_3;
INSERT INTO canchas_dia_3 (cancha_numero, fecha_hora)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 3 DAY), ' ', h.h)
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
      UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
      UNION ALL SELECT '19:00:00') AS h;

-- Día 4
TRUNCATE TABLE canchas_dia_4;
INSERT INTO canchas_dia_4 (cancha_numero, fecha_hora)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 4 DAY), ' ', h.h)
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
      UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
      UNION ALL SELECT '19:00:00') AS h;

-- 5) Crear evento que repuebla las tablas a diario a las 00:00
DELIMITER $$
CREATE EVENT actualizar_canchas
  ON SCHEDULE EVERY 1 DAY
  STARTS CONCAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), ' 00:00:00')
DO
BEGIN
    -- Día 1
    TRUNCATE TABLE canchas_dia_1;
    INSERT INTO canchas_dia_1 (cancha_numero, fecha_hora)
    SELECT c.c, CONCAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), ' ', h.h)
    FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
         (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
          UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
          UNION ALL SELECT '19:00:00') AS h;

    -- Día 2
    TRUNCATE TABLE canchas_dia_2;
    INSERT INTO canchas_dia_2 (cancha_numero, fecha_hora)
    SELECT c.c, CONCAT(DATE_ADD(CURDATE(), INTERVAL 2 DAY), ' ', h.h)
    FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
         (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
          UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
          UNION ALL SELECT '19:00:00') AS h;

    -- Día 3
    TRUNCATE TABLE canchas_dia_3;
    INSERT INTO canchas_dia_3 (cancha_numero, fecha_hora)
    SELECT c.c, CONCAT(DATE_ADD(CURDATE(), INTERVAL 3 DAY), ' ', h.h)
    FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
         (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
          UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
          UNION ALL SELECT '19:00:00') AS h;

    -- Día 4
    TRUNCATE TABLE canchas_dia_4;
    INSERT INTO canchas_dia_4 (cancha_numero, fecha_hora)
    SELECT c.c, CONCAT(DATE_ADD(CURDATE(), INTERVAL 4 DAY), ' ', h.h)
    FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
         (SELECT '12:00:00' AS h UNION ALL SELECT '16:00:00'
          UNION ALL SELECT '17:00:00' UNION ALL SELECT '18:00:00'
          UNION ALL SELECT '19:00:00') AS h;
END$$
DELIMITER ;
