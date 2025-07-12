-- ------------------------------------------------------------------
-- canchas.sql: Creación de tablas de canchas, población inicial y evento de actualización
-- ------------------------------------------------------------------

-- 1) Activar el scheduler de eventos
SET GLOBAL event_scheduler = ON;

USE padelclub;

-- 2) Eliminar evento y tablas previas
DROP EVENT IF EXISTS actualizar_canchas;
DROP TABLE IF EXISTS canchas_dia_1;
DROP TABLE IF EXISTS canchas_dia_2;
DROP TABLE IF EXISTS canchas_dia_3;
DROP TABLE IF EXISTS canchas_dia_4;

-- 3) Crear tablas diarias de canchas (sin columna personas_jugando)
CREATE TABLE canchas_dia_1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cancha_numero TINYINT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE canchas_dia_2 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_3 LIKE canchas_dia_1;
CREATE TABLE canchas_dia_4 LIKE canchas_dia_1;

-- 4) Población inicial de las tablas (para los próximos 4 días)
--    Horarios: 16:00, 17:00, 18:00, 19:00, 20:00
-- Día 1
INSERT INTO canchas_dia_1 (cancha_numero, fecha_hora, disponible)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), ' ', h.h),
       TRUE
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '16:00:00' AS h UNION ALL SELECT '17:00:00'
      UNION ALL SELECT '18:00:00' UNION ALL SELECT '19:00:00'
      UNION ALL SELECT '20:00:00') AS h;

-- Día 2
INSERT INTO canchas_dia_2 (cancha_numero, fecha_hora, disponible)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 2 DAY), ' ', h.h),
       TRUE
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '16:00:00' AS h UNION ALL SELECT '17:00:00'
      UNION ALL SELECT '18:00:00' UNION ALL SELECT '19:00:00'
      UNION ALL SELECT '20:00:00') AS h;

-- Día 3
INSERT INTO canchas_dia_3 (cancha_numero, fecha_hora, disponible)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 3 DAY), ' ', h.h),
       TRUE
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '16:00:00' AS h UNION ALL SELECT '17:00:00'
      UNION ALL SELECT '18:00:00' UNION ALL SELECT '19:00:00'
      UNION ALL SELECT '20:00:00') AS h;

-- Día 4
INSERT INTO canchas_dia_4 (cancha_numero, fecha_hora, disponible)
SELECT c.c,
       CONCAT(DATE_ADD(CURDATE(), INTERVAL 4 DAY), ' ', h.h),
       TRUE
FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
     (SELECT '16:00:00' AS h UNION ALL SELECT '17:00:00'
      UNION ALL SELECT '18:00:00' UNION ALL SELECT '19:00:00'
      UNION ALL SELECT '20:00:00') AS h;

-- 5) Evento que repuebla cada día y actualiza disponibilidad según reservas
DELIMITER $$
CREATE EVENT actualizar_canchas
  ON SCHEDULE EVERY 1 DAY
  STARTS CONCAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), ' 00:00:00')
DO
BEGIN
    DECLARE d INT;
    DECLARE tbl_name VARCHAR(20);
    FOR d IN 1..4 DO
      SET tbl_name = CONCAT('canchas_dia_', d);
      TRUNCATE TABLE 
        @tbl_name;
      INSERT INTO 
        @tbl_name (cancha_numero, fecha_hora, disponible)
      SELECT c.c,
             CONCAT(DATE_ADD(CURDATE(), INTERVAL d DAY), ' ', h.h),
             NOT EXISTS(
               SELECT 1 FROM reservas r
                WHERE r.cancha = c.c
                  AND r.fecha_inicio = CONCAT(DATE_ADD(CURDATE(), INTERVAL d DAY), ' ', h.h)
             )
      FROM (SELECT 1 AS c UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4) AS c,
           (SELECT '16:00:00' AS h UNION ALL SELECT '17:00:00'
            UNION ALL SELECT '18:00:00' UNION ALL SELECT '19:00:00'
            UNION ALL SELECT '20:00:00') AS h;
    END FOR;
    -- Eliminar reservas vencidas
    DELETE FROM reservas WHERE fecha_fin < NOW();
END$$
DELIMITER ;

-- FIN de canchas.sql
