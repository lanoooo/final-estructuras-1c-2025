#!/usr/bin/env python3
import os
os.system('cls')

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

from backendPRUEBA import UsuarioManager, ReservationManager

# Constantes de configuración
ADMIN_SECRET = "padel"
TIME_SLOTS = ["12:00:00", "16:00:00", "17:00:00", "18:00:00", "19:00:00"]
MAX_DAYS = 4
DATE_FORMAT = "%Y-%m-%d"

class AuthService:
    """Gestiona autenticación y registro de usuarios."""
    @staticmethod
    def login(username, password):
        gestor = UsuarioManager()
        role, uid = gestor.iniciar_sesion(username, password)
        gestor.desconectar()
        if role:
            return True, role, uid
        return False, None, None

    @staticmethod
    def register(username, password, role):
        gestor = UsuarioManager()
        success = gestor.crear_usuario(username, password, role)
        gestor.desconectar()
        return success

class App(tk.Tk):
    """Ventana principal que gestiona la navegación entre páginas."""
    def __init__(self):
        super().__init__()
        self.title("Padel Club")
        self.geometry("450x400")
        self.resizable(False, False)

        # Variables de estado
        self.current_user_id = None
        self.current_role = None

        # Contenedor de páginas
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Instanciar páginas
        self.pages = {}
        for PageClass in (LoginPage, RegisterPage, PlayerMenuPage, AdminMenuPage, ReservationPage):
            page = PageClass(parent=container, controller=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Mostrar login al inicio
        self.show_page("LoginPage")

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if not page:
            messagebox.showerror("Error", f"Página '{page_name}' no encontrada.")
            return
        page.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        # Título
        ttk.Label(self, text="Iniciar Sesión", font=(None, 18)).pack(pady=10)
        # Usuario
        ttk.Label(self, text="Usuario:").pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_var).pack(fill='x', pady=5)
        # Contraseña
        ttk.Label(self, text="Contraseña:").pack(anchor='w')
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pass_var, show='*').pack(fill='x', pady=5)
        # Botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Ingresar", width=12, command=self._login).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Registrarse", width=12,
                   command=lambda: self.controller.show_page("RegisterPage")).pack(side='left', padx=5)

    def _login(self):
        user = self.user_var.get().strip()
        pwd  = self.pass_var.get().strip()
        ok, role, uid = AuthService.login(user, pwd)
        if not ok:
            return messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        # Verificación de admin
        if role == 'admin':
            code = simpledialog.askstring("Verificación Admin", "Ingrese clave maestra:", show='*')
            if code != ADMIN_SECRET:
                return messagebox.showerror("Error", "Clave de administrador incorrecta.")
            self.controller.current_role = 'admin'
            next_page = 'AdminMenuPage'
        else:
            self.controller.current_role = 'jugador'
            next_page = 'PlayerMenuPage'
        self.controller.current_user_id = uid
        self.controller.show_page(next_page)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        ttk.Label(self, text="Registro de Usuario", font=(None, 18)).pack(pady=10)
        # Usuario
        ttk.Label(self, text="Usuario:").pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_var).pack(fill='x', pady=5)
        # Contraseña
        ttk.Label(self, text="Contraseña:").pack(anchor='w')
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pass_var, show='*').pack(fill='x', pady=5)
        # Rol
        ttk.Label(self, text="Rol:").pack(anchor='w')
        self.role_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.role_var,
                     values=('jugador','admin'), state='readonly').pack(fill='x', pady=5)
        # Clave admin
        ttk.Label(self, text="Clave maestra admin:").pack(anchor='w')
        self.admin_key_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.admin_key_var, show='*').pack(fill='x', pady=5)
        # Botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Crear", width=12, command=self._register).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", width=12,
                   command=lambda: self.controller.show_page('LoginPage')).pack(side='left', padx=5)

    def _register(self):
        user = self.user_var.get().strip()
        pwd  = self.pass_var.get().strip()
        role = self.role_var.get().strip()
        key  = self.admin_key_var.get().strip()
        # Validaciones
        if not user or not pwd or not role:
            return messagebox.showerror("Error", "Completa todos los campos obligatorios.")
        if role == 'admin' and key != ADMIN_SECRET:
            return messagebox.showerror("Error", "Clave de administrador inválida.")
        success = AuthService.register(user, pwd, role)
        if success:
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.controller.show_page('LoginPage')
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario.")

class PlayerMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Menú Jugador", font=(None, 18)).pack(pady=10)
        # Opciones
        ttk.Button(self, text="Reservar cancha", width=20,
                   command=lambda: controller.show_page('ReservationPage')).pack(pady=5)
        ttk.Button(self, text="Ver partidos abiertos", width=20,
                   command=lambda: messagebox.showinfo("Info", "Función pendiente")).pack(pady=5)
        ttk.Button(self, text="Torneos", width=20,
                   command=lambda: messagebox.showinfo("Info", "Función pendiente")).pack(pady=5)
        ttk.Button(self, text="Cerrar sesión", width=20,
                   command=lambda: controller.show_page('LoginPage')).pack(pady=15)

class AdminMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Menú Administrador", font=(None, 18)).pack(pady=10)
        ttk.Button(self, text="Ver reservas", width=20,
                   command=lambda: controller.show_page('ReservationPage')).pack(pady=5)
        ttk.Button(self, text="Administrar canchas", width=20,
                   command=lambda: messagebox.showinfo("Info", "Función pendiente")).pack(pady=5)
        ttk.Button(self, text="Ver usuarios", width=20,
                   command=lambda: messagebox.showinfo("Info", "Función pendiente")).pack(pady=5)
        ttk.Button(self, text="Cerrar sesión", width=20,
                   command=lambda: controller.show_page('LoginPage')).pack(pady=15)

class ReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        ttk.Label(self, text="Reservar Cancha", font=(None, 18)).pack(pady=10)
        # Día
        day_frame = ttk.Frame(self)
        day_frame.pack(pady=5)
        ttk.Label(day_frame, text="Día:").pack(side='left')
        self.day_var = tk.StringVar()
        days = [(datetime.today() + timedelta(days=i)).strftime(DATE_FORMAT)
                for i in range(1, MAX_DAYS+1)]
        ttk.Combobox(day_frame, values=days, textvariable=self.day_var,
                     state='readonly', width=15).pack(side='left', padx=5)
        # Hora
        time_frame = ttk.Frame(self)
        time_frame.pack(pady=5)
        ttk.Label(time_frame, text="Hora:").pack(side='left')
        self.time_var = tk.StringVar()
        ttk.Combobox(time_frame, values=TIME_SLOTS, textvariable=self.time_var,
                     state='readonly', width=15).pack(side='left', padx=24)
        # Botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Confirmar", width=12,
                   command=self._confirm).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Volver", width=12,
                   command=self._back_to_menu).pack(side='left', padx=5)

    def _confirm(self):
        fecha = self.day_var.get()
        hora  = self.time_var.get()
        uid   = self.controller.current_user_id
        if not fecha or not hora:
            return messagebox.showerror("Error", "Selecciona día y hora.")
        ok, msg = ReservationManager().reservar(uid, fecha, hora)
        (messagebox.showinfo if ok else messagebox.showerror)("Reserva", msg)
        if ok:
            self._back_to_menu()

    def _back_to_menu(self):
        role = self.controller.current_role
        if role == 'admin':
            self.controller.show_page('AdminMenuPage')
        else:
            self.controller.show_page('PlayerMenuPage')

if __name__ == '__main__':
    App().mainloop()
