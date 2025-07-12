#!/usr/bin/env python3
"""
Backend unificado para el sistema de reservas del Padel Club
"""

import pymysql
import hashlib
from datetime import datetime, timedelta

# Configuración de conexión
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'padelclub'
}

class UsuarioManager:
    def __init__(self):
        self.db = pymysql.connect(**DB_CONFIG)
        self.cursor = self.db.cursor()

    def hash_password(self, plain_text):
        return hashlib.sha256(plain_text.encode('utf-8')).hexdigest()

    def crear_usuario(self, nombre_usuario, clave, rol):
        clave_segura = self.hash_password(clave)
        sql = "INSERT INTO usuarios (usuario, contraseña, tipo) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(sql, (nombre_usuario, clave_segura, rol))
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def iniciar_sesion(self, nombre_usuario, clave):
        clave_segura = self.hash_password(clave)
        consulta = "SELECT tipo, id FROM usuarios WHERE usuario = %s AND contraseña = %s"
        self.cursor.execute(consulta, (nombre_usuario, clave_segura))
        resultado = self.cursor.fetchone()
        if resultado:
            return resultado  # (rol, usuario_id)
        return None, None

    def desconectar(self):
        if self.db:
            self.db.close()

class ReservationManager:
    """Gestiona disponibilidad y reservas de canchas."""
    MAX_DAYS = 4
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self):
        self.db = pymysql.connect(**DB_CONFIG)
        self.cursor = self.db.cursor()

    def get_available_slots(self, fecha_str):
        """Devuelve las franjas horarias con al menos una cancha libre."""
        hoy = datetime.today().date()
        fecha = datetime.strptime(fecha_str, self.DATE_FORMAT).date()
        offset = (fecha - hoy).days
        if offset < 1 or offset > self.MAX_DAYS:
            return []
        
        tabla = f"canchas_dia_{offset}"
        query = (
            f"SELECT DISTINCT DATE_FORMAT(fecha_hora, '%H:%i:%s') AS hora "
            f"FROM {tabla} WHERE disponible = 1 "
            f"ORDER BY hora"
        )
        self.cursor.execute(query)
        return [r[0] for r in self.cursor.fetchall()]

    def reservar(self, usuario_id: int, fecha_str: str, hora_str: str):
        """Reserva la primera cancha libre (1–4) en la franja indicada."""
        hoy = datetime.today().date()
        fecha = datetime.strptime(fecha_str, self.DATE_FORMAT).date()
        offset = (fecha - hoy).days
        if offset < 1 or offset > self.MAX_DAYS:
            return False, "Fecha fuera de rango"
        
        tabla = f"canchas_dia_{offset}"
        fecha_hora = f"{fecha_str} {hora_str}"

        try:
            # 1) Seleccionar la primera cancha libre
            self.cursor.execute(
                f"SELECT cancha_numero FROM {tabla} "
                f"WHERE fecha_hora = %s AND disponible = 1 "
                f"ORDER BY cancha_numero LIMIT 1",
                (fecha_hora,)
            )
            fila = self.cursor.fetchone()
            if not fila:
                return False, "No hay canchas disponibles en ese horario"
            cancha = fila[0]

            # 2) Marcarla como ocupada
            self.cursor.execute(
                f"UPDATE {tabla} SET disponible = 0 "
                f"WHERE fecha_hora = %s AND cancha_numero = %s",
                (fecha_hora, cancha)
            )

            # 3) Insertar la reserva
            fin_dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
            self.cursor.execute(
                "INSERT INTO reservas (usuario_id, cancha, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s)",
                (usuario_id, cancha, fecha_hora, fin_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )

            self.db.commit()
            return True, f"Reservada cancha {cancha} para {fecha_str} a las {hora_str}"

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def get_reservations(self):
        """Devuelve todas las reservas con día, hora, cancha y usuario."""
        sql = (
            "SELECT "
            "DATE_FORMAT(r.fecha_inicio, %s) AS dia, "
            "DATE_FORMAT(r.fecha_inicio, %s) AS hora, "
            "r.cancha, u.usuario "
            "FROM reservas r "
            "JOIN usuarios u ON r.usuario_id = u.id "
            "ORDER BY r.fecha_inicio"
        )
        self.cursor.execute(sql, ('%Y-%m-%d', '%H:%i:%s'))
        return self.cursor.fetchall()

    def get_reservations_with_ids(self, user_id: int | None = None, is_admin: bool = False):
        """Devuelve reservas con IDs para poder eliminarlas"""
        if is_admin:
            sql = (
                "SELECT "
                "r.id, "
                "DATE_FORMAT(r.fecha_inicio, %s) AS dia, "
                "DATE_FORMAT(r.fecha_inicio, %s) AS hora, "
                "r.cancha, u.usuario "
                "FROM reservas r "
                "JOIN usuarios u ON r.usuario_id = u.id "
                "WHERE r.fecha_inicio >= NOW() "
                "ORDER BY r.fecha_inicio"
            )
            self.cursor.execute(sql, ('%Y-%m-%d', '%H:%i:%s'))
        else:
            sql = (
                "SELECT "
                "r.id, "
                "DATE_FORMAT(r.fecha_inicio, %s) AS dia, "
                "DATE_FORMAT(r.fecha_inicio, %s) AS hora, "
                "r.cancha, u.usuario "
                "FROM reservas r "
                "JOIN usuarios u ON r.usuario_id = u.id "
                "WHERE r.usuario_id = %s AND r.fecha_inicio >= NOW() "
                "ORDER BY r.fecha_inicio"
            )
            self.cursor.execute(sql, ('%Y-%m-%d', '%H:%i:%s', user_id))
        
        return self.cursor.fetchall()

    def delete_reservation(self, reservation_id: int, user_id: int, is_admin: bool = False):
        """Elimina una reserva específica"""
        try:
            # Verificar que la reserva existe y pertenece al usuario (o es admin)
            if is_admin:
                self.cursor.execute(
                    "SELECT r.id, r.cancha, r.fecha_inicio, u.usuario "
                    "FROM reservas r JOIN usuarios u ON r.usuario_id = u.id "
                    "WHERE r.id = %s", (reservation_id,)
                )
            else:
                self.cursor.execute(
                    "SELECT r.id, r.cancha, r.fecha_inicio, u.usuario "
                    "FROM reservas r JOIN usuarios u ON r.usuario_id = u.id "
                    "WHERE r.id = %s AND r.usuario_id = %s", 
                    (reservation_id, user_id)
                )
            
            reservation = self.cursor.fetchone()
            if not reservation:
                return False, "Reserva no encontrada o no tiene permisos para eliminarla"
            
            res_id, cancha, fecha_inicio, usuario = reservation
            
            # Verificar que la reserva es futura
            if fecha_inicio < datetime.now():
                return False, "No se pueden cancelar reservas pasadas"
            
            # Calcular qué tabla de canchas usar basado en la fecha
            hoy = datetime.today().date()
            fecha_reserva = fecha_inicio.date()
            offset = (fecha_reserva - hoy).days
            
            if 1 <= offset <= 4:
                tabla_cancha = f"canchas_dia_{offset}"
                fecha_hora_str = fecha_inicio.strftime("%Y-%m-%d %H:%M:%S")
                
                # Liberar la cancha
                self.cursor.execute(
                    f"UPDATE {tabla_cancha} SET disponible = 1 "
                    f"WHERE fecha_hora = %s AND cancha_numero = %s",
                    (fecha_hora_str, cancha)
                )
            
            # Eliminar la reserva
            self.cursor.execute("DELETE FROM reservas WHERE id = %s", (reservation_id,))
            
            self.db.commit()
            return True, f"Reserva de {usuario} para el {fecha_reserva} cancelada exitosamente"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al cancelar reserva: {str(e)}"
        
    def desconectar(self):
        if self.db:
            self.db.close()

class TournamentManager:
    """Gestiona torneos de padel."""
    
    def __init__(self):
        self.db = pymysql.connect(**DB_CONFIG)
        self.cursor = self.db.cursor()
    
    def get_available_saturdays(self):
        """Devuelve los próximos 4 sábados que estén a más de 7 días de hoy."""
        from datetime import datetime, timedelta
        
        today = datetime.today().date()
        
        # Encontrar el próximo sábado (weekday 5 = sábado)
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:  # Si hoy es sábado
            days_until_saturday = 7
        
        next_saturday = today + timedelta(days=days_until_saturday)
        
        # Si el próximo sábado está a menos de 7 días, tomar el siguiente
        if (next_saturday - today).days <= 7:
            next_saturday += timedelta(days=7)
        
        # Generar 4 sábados consecutivos
        saturdays = []
        for i in range(4):
            saturday = next_saturday + timedelta(days=i*7)
            saturdays.append(saturday.strftime("%Y-%m-%d"))
        
        return saturdays
    
    def create_tournament(self, name, date, max_teams=8):
        """Crear un nuevo torneo."""
        try:
            sql = "INSERT INTO torneos (nombre, fecha, max_equipos, estado) VALUES (%s, %s, %s, 'abierto')"
            self.cursor.execute(sql, (name, date, max_teams))
            tournament_id = self.cursor.lastrowid
            self.db.commit()
            return True, tournament_id
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def get_active_tournament(self):
        """Obtener el torneo activo (abierto para inscripciones)."""
        sql = "SELECT id, nombre, fecha, max_equipos FROM torneos WHERE estado = 'abierto' ORDER BY fecha LIMIT 1"
        self.cursor.execute(sql)
        return self.cursor.fetchone()
    
    def register_team(self, tournament_id, team_name, player1, player2, user_id):
        """Registrar un equipo en el torneo."""
        try:
            # Verificar que el torneo existe y está abierto
            sql = "SELECT max_equipos FROM torneos WHERE id = %s AND estado = 'abierto'"
            self.cursor.execute(sql, (tournament_id,))
            result = self.cursor.fetchone()
            if not result:
                return False, "Torneo no encontrado o cerrado"
            
            max_teams = result[0]
            
            # Contar equipos actuales
            sql = "SELECT COUNT(*) FROM equipos WHERE torneo_id = %s"
            self.cursor.execute(sql, (tournament_id,))
            result = self.cursor.fetchone()
            current_teams = result[0] if result else 0
            
            if current_teams >= max_teams:
                return False, "Torneo completo"
            
            # Verificar que el usuario no tenga ya un equipo registrado
            sql = "SELECT id FROM equipos WHERE torneo_id = %s AND usuario_id = %s"
            self.cursor.execute(sql, (tournament_id, user_id))
            if self.cursor.fetchone():
                return False, "Ya tienes un equipo registrado en este torneo"
            
            # Registrar el equipo
            sql = "INSERT INTO equipos (torneo_id, nombre_equipo, jugador1, jugador2, usuario_id) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, (tournament_id, team_name, player1, player2, user_id))
            self.db.commit()
            
            return True, "Equipo registrado exitosamente"
            
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def get_tournament_teams(self, tournament_id):
        """Obtener todos los equipos de un torneo."""
        sql = """
        SELECT e.id, e.nombre_equipo, e.jugador1, e.jugador2, u.usuario 
        FROM equipos e 
        JOIN usuarios u ON e.usuario_id = u.id 
        WHERE e.torneo_id = %s 
        ORDER BY e.id
        """
        self.cursor.execute(sql, (tournament_id,))
        return self.cursor.fetchall()
    
    def generate_fixture(self, tournament_id):
        """Generar fixture de partidos para el torneo."""
        try:
            teams = self.get_tournament_teams(tournament_id)
            if len(teams) < 2:
                return False, "Se necesitan al menos 2 equipos"
            
            # Limpiar partidos existentes
            self.cursor.execute("DELETE FROM partidos WHERE torneo_id = %s", (tournament_id,))
            
            # Generar partidos (todos contra todos)
            match_number = 1
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    team1_id = teams[i][0]
                    team2_id = teams[j][0]
                    
                    sql = """
                    INSERT INTO partidos (torneo_id, equipo1_id, equipo2_id, numero_partido, estado) 
                    VALUES (%s, %s, %s, %s, 'pendiente')
                    """
                    self.cursor.execute(sql, (tournament_id, team1_id, team2_id, match_number))
                    match_number += 1
            
            # Cambiar estado del torneo a 'en_curso'
            self.cursor.execute("UPDATE torneos SET estado = 'en_curso' WHERE id = %s", (tournament_id,))
            
            self.db.commit()
            return True, f"Fixture generado con {match_number - 1} partidos"
            
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def get_tournament_matches(self, tournament_id):
        """Obtener todos los partidos de un torneo."""
        sql = """
        SELECT p.id, p.numero_partido, 
               e1.nombre_equipo as equipo1, e2.nombre_equipo as equipo2,
               p.resultado_equipo1, p.resultado_equipo2, p.estado
        FROM partidos p
        JOIN equipos e1 ON p.equipo1_id = e1.id
        JOIN equipos e2 ON p.equipo2_id = e2.id
        WHERE p.torneo_id = %s
        ORDER BY p.numero_partido
        """
        self.cursor.execute(sql, (tournament_id,))
        return self.cursor.fetchall()
    
    def get_all_tournaments(self):
        """Obtener todos los torneos."""
        sql = "SELECT id, nombre, fecha, estado, max_equipos FROM torneos ORDER BY fecha DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def delete_tournament(self, tournament_id):
        try:
            # Eliminar partidos asociados
            self.cursor.execute("DELETE FROM partidos WHERE torneo_id = %s", (tournament_id,))
            # Eliminar equipos asociados
            self.cursor.execute("DELETE FROM equipos WHERE torneo_id = %s", (tournament_id,))
            # Eliminar el torneo
            self.cursor.execute("DELETE FROM torneos WHERE id = %s", (tournament_id,))
            self.db.commit()
            return True, "Torneo eliminado correctamente"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
    
    def desconectar(self):
        if self.db:
            self.db.close()
