import pymysql
import hashlib
from datetime import datetime, timedelta

# Configuración de conexión
db_config = {
    'host':     '127.0.0.1',
    'port':     3306,
    'user':     'root',
    'password': '1234',
    'database': 'padelclub'
}

class UsuarioManager:
    def __init__(self):
        self.db = pymysql.connect(**db_config)
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
        self.db.close()

class ReservationManager:
    """Gestiona disponibilidad y reservas de canchas."""
    MAX_DAYS    = 4
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self):
        self.gestor = UsuarioManager()

    def get_available_slots(self, fecha_str):
        """Devuelve las franjas horarias con al menos una cancha libre."""
        hoy   = datetime.today().date()
        fecha = datetime.strptime(fecha_str, self.DATE_FORMAT).date()
        offset = (fecha - hoy).days
        if offset < 1 or offset > self.MAX_DAYS:
            return []
        tabla = f"canchas_dia_{offset}"
        cur = self.gestor.cursor
        query = (
            f"SELECT DISTINCT DATE_FORMAT(fecha_hora, '%H:%i:%s') AS hora "
            f"FROM {tabla} WHERE disponible = 1 "
            f"ORDER BY hora"
        )
        cur.execute(query)
        return [r[0] for r in cur.fetchall()]

    def reservar(self, usuario_id: int, fecha_str: str, hora_str: str):
        """Reserva la primera cancha libre (1–4) en la franja indicada."""
        hoy   = datetime.today().date()
        fecha = datetime.strptime(fecha_str, self.DATE_FORMAT).date()
        offset = (fecha - hoy).days
        if offset < 1 or offset > self.MAX_DAYS:
            return False, "Fecha fuera de rango"
        tabla = f"canchas_dia_{offset}"
        fecha_hora = f"{fecha_str} {hora_str}"
        cur = self.gestor.cursor

        try:
            # 1) Seleccionar la primera cancha libre
            cur.execute(
                f"SELECT cancha_numero FROM {tabla} "
                f"WHERE fecha_hora = %s AND disponible = 1 "
                f"ORDER BY cancha_numero LIMIT 1",
                (fecha_hora,)
            )
            fila = cur.fetchone()
            if not fila:
                return False, "No hay canchas disponibles en ese horario"
            cancha = fila[0]

            # 2) Marcarla como ocupada
            cur.execute(
                f"UPDATE {tabla} SET disponible = 0 "
                f"WHERE fecha_hora = %s AND cancha_numero = %s",
                (fecha_hora, cancha)
            )

            # 3) Insertar la reserva
            fin_dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
            cur.execute(
                "INSERT INTO reservas (usuario_id, cancha, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s)",
                (usuario_id, cancha, fecha_hora, fin_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )

            self.gestor.db.commit()
            return True, f"Reservada cancha {cancha} para {fecha_str} a las {hora_str}"

        except Exception as e:
            self.gestor.db.rollback()
            return False, str(e)

        finally:
            self.gestor.desconectar()

    def get_reservations(self):
        """Devuelve todas las reservas con día, hora, cancha y usuario."""
        um = self.gestor
        cur = um.cursor
        sql = (
            "SELECT "
              "DATE_FORMAT(r.fecha_inicio, '%Y-%m-%d') AS dia, "
              "DATE_FORMAT(r.fecha_inicio, '%H:%i:%s') AS hora, "
              "r.cancha, u.usuario "
            "FROM reservas r "
            "JOIN usuarios u ON r.usuario_id = u.id "
            "ORDER BY r.fecha_inicio"
        )
        cur.execute(sql)
        rows = cur.fetchall()
        um.desconectar()
        return rows
