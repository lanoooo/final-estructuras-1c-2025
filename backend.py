import pymysql
import hashlib

# Configuración de conexión
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "padelclub"

class UsuarioManager:
    def __init__(self):
        self.db = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.cursor = self.db.cursor()

    def hash_password(self, plain_text):
        return hashlib.sha256(plain_text.encode('utf-8')).hexdigest()

    def usuario_existe(self, nombre_usuario):
        self.cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (nombre_usuario,))
        return self.cursor.fetchone() is not None

    def crear_usuario(self, nombre_usuario, clave, rol):
        if rol == "admin":
            clave_admin = input("Clave secreta para administradores: ")
            if clave_admin != "padel":
                print("❌ Clave incorrecta. Registro cancelado.")
                return False

        clave_segura = self.hash_password(clave)
        sql = "INSERT INTO usuarios (usuario, contraseña, tipo) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(sql, (nombre_usuario, clave_segura, rol))
            self.db.commit()
            print("✅ Usuario creado con éxito.")
            return True
        except Exception as e:
            print(f"Error al registrar: {e}")
            self.db.rollback()
            return False

    def iniciar_sesion(self, nombre_usuario, clave):
        if not self.usuario_existe(nombre_usuario):
            print("❌ El nombre de usuario no existe.")
            return None

        clave_segura = self.hash_password(clave)
        consulta = "SELECT tipo FROM usuarios WHERE usuario = %s AND contraseña = %s"
        self.cursor.execute(consulta, (nombre_usuario, clave_segura))
        resultado = self.cursor.fetchone()

        if resultado:
            print(f"✅ Bienvenido {nombre_usuario}. Rol: {resultado[0]}")
            return resultado[0]
        else:
            print("❌ Contraseña incorrecta.")
            return None

    def desconectar(self):
        self.cursor.close()
        self.db.close()

def mostrar_menu():
    gestor = UsuarioManager()

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Elegí una opción: ")

        if opcion == "1":
            while True:
                while True:
                    usuario = input("Nuevo nombre de usuario: ")
                    if usuario.strip() == "":
                        print("❌ El nombre de usuario no puede estar vacío.")
                        continue
                    if gestor.usuario_existe(usuario):
                        print("⚠️ Ya existe un usuario con ese nombre. Elegí otro.")
                        continue
                    break

                contraseña = input("Contraseña: ")
                tipo = input("Tipo de cuenta (admin/jugador): ")
                if tipo in ["admin", "jugador"]:
                    exito = gestor.crear_usuario(usuario, contraseña, tipo)
                    if exito:
                        break
                else:
                    print("❌ Tipo inválido. Solo se permite 'admin' o 'jugador'.")

        elif opcion == "2":
            usuario = input("Usuario: ")
            if usuario.strip() == "":
                print("❌ El nombre de usuario no puede estar vacío.")
                continue
            contraseña = input("Contraseña: ")
            tipo = gestor.iniciar_sesion(usuario, contraseña)
            if tipo == "admin":
                print("🔐 Accediendo a funciones de administrador...")
            elif tipo == "jugador":
                print("🎾 Accediendo a funciones de jugador...")

        elif opcion == "3":
            print("👋 Cerrando sistema. Hasta pronto.")
            gestor.desconectar()
            break

        else:
            print("❌ Opción no válida.")

if __name__ == "__main__":
    mostrar_menu()
