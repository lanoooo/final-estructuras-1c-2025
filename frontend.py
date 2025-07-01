#!/usr/bin/env python3
import os
os.system('cls')

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

from backendPRUEBA import UsuarioManager, ReservationManager

# Constantes
ADMIN_SECRET = "padel"
MAX_DAYS     = 4
DATE_FORMAT  = "%Y-%m-%d"

class AuthService:
    @staticmethod
    def login(username, password):
        um = UsuarioManager()
        role, uid = um.iniciar_sesion(username, password)
        um.desconectar()
        return (True, role, uid) if role else (False, None, None)

    @staticmethod
    def register(username, password, role):
        um = UsuarioManager()
        ok = um.crear_usuario(username, password, role)
        um.desconectar()
        return ok

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Padel Club")
        self.geometry("480x480")
        self.resizable(False, False)

        self.current_user_id = None
        self.current_role    = None

        container = ttk.Frame(self)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Instanciar páginas
        self.pages = {}
        for PageClass in (LoginPage, RegisterPage, PlayerMenuPage, AdminMenuPage, ReservationPage):
            page = PageClass(container, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky='nsew')

        self.show_page('LoginPage')

    def show_page(self, name):
        if name == 'ReservationPage':
            self.pages[name].refresh_slots()
        self.pages[name].tkraise()

# ---------------------- LoginPage ----------------------
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Iniciar Sesión", font=(None,18)).pack(pady=10)
        ttk.Label(self, text="Usuario:").pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_var).pack(fill='x', pady=5)
        ttk.Label(self, text="Contraseña:").pack(anchor='w')
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pass_var, show='*').pack(fill='x', pady=5)

        frm = ttk.Frame(self); frm.pack(pady=15)
        ttk.Button(frm, text="Ingresar", width=12, command=self._login).pack(side='left', padx=5)
        ttk.Button(frm, text="Registrarse", width=12,
                   command=lambda: controller.show_page('RegisterPage')).pack(side='left', padx=5)

    def _login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()
        ok, role, uid = AuthService.login(u, p)
        if not ok:
            return messagebox.showerror("Error","Credenciales inválidas")
        if role == 'admin':
            code = simpledialog.askstring("Admin","Clave maestra:",show='*')
            if code != ADMIN_SECRET:
                return messagebox.showerror("Error","Clave admin incorrecta")
        self.controller.current_role    = role
        self.controller.current_user_id = uid
        next_page = 'AdminMenuPage' if role=='admin' else 'PlayerMenuPage'
        self.controller.show_page(next_page)

# ---------------------- RegisterPage ----------------------
class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Registro", font=(None,18)).pack(pady=10)
        ttk.Label(self, text="Usuario:").pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_var).pack(fill='x', pady=5)
        ttk.Label(self, text="Contraseña:").pack(anchor='w')
        self.pass_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pass_var, show='*').pack(fill='x', pady=5)
        ttk.Label(self, text="Rol:").pack(anchor='w')
        self.role_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.role_var,
                     values=('jugador','admin'), state='readonly').pack(fill='x', pady=5)
        ttk.Label(self, text="Clave admin:").pack(anchor='w')
        self.key_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.key_var, show='*').pack(fill='x', pady=5)

        frm = ttk.Frame(self); frm.pack(pady=15)
        ttk.Button(frm, text="Crear", width=12, command=self._register).pack(side='left', padx=5)
        ttk.Button(frm, text="Cancelar", width=12,
                   command=lambda: controller.show_page('LoginPage')).pack(side='left', padx=5)

    def _register(self):
        u,p,r,k = [v.get().strip() for v in
                   (self.user_var,self.pass_var,self.role_var,self.key_var)]
        if not u or not p or not r:
            return messagebox.showerror("Error","Completa campos obligatorios")
        if r=='admin' and k!=ADMIN_SECRET:
            return messagebox.showerror("Error","Clave admin inválida")
        if AuthService.register(u,p,r):
            messagebox.showinfo("Éxito","Usuario registrado")
            self.controller.show_page('LoginPage')
        else:
            messagebox.showerror("Error","Registro fallido")

# ---------------------- PlayerMenuPage ----------------------
class PlayerMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Menú Jugador", font=(None,18)).pack(pady=10)
        ttk.Button(self, text="Reservar cancha", width=20,
                   command=lambda: controller.show_page('ReservationPage')).pack(pady=5)
        ttk.Button(self, text="Ver mis reservas", width=20,
                   command=lambda: messagebox.showinfo("Info","Pendiente")).pack(pady=5)
        ttk.Button(self, text="Torneos", width=20,
                   command=lambda: messagebox.showinfo("Info","Pendiente")).pack(pady=5)
        ttk.Button(self, text="Cerrar sesión", width=20,
                   command=lambda: controller.show_page('LoginPage')).pack(pady=15)

# ---------------------- AdminMenuPage ----------------------
class AdminMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Menú Administrador", font=(None,18)).pack(pady=10)
        ttk.Button(self, text="Ver Reservas", width=20,
                   command=self._show_reservas).pack(pady=5)
        ttk.Button(self, text="Administrar canchas", width=20,
                   command=lambda: messagebox.showinfo("Info","Pendiente")).pack(pady=5)
        ttk.Button(self, text="Ver usuarios", width=20,
                   command=lambda: messagebox.showinfo("Info","Pendiente")).pack(pady=5)
        ttk.Button(self, text="Cerrar sesión", width=20,
                   command=lambda: controller.show_page('LoginPage')).pack(pady=15)

    def _show_reservas(self):
        rows = ReservationManager().get_reservations()
        win = tk.Toplevel(self)
        win.title("Reservas Actuales")
        cols = ("Día","Hora","Cancha","Usuario")
        tree = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)
        for dia,hora,cancha,usr in rows:
            tree.insert('', 'end', values=(dia,hora,cancha,usr))
        sb = ttk.Scrollbar(win, orient='vertical', command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side='right', fill='y')

# ---------------------- ReservationPage ----------------------
class ReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Reservar Cancha", font=(None,18)).pack(pady=10)

        # Día
        frm = ttk.Frame(self); frm.pack(pady=5)
        ttk.Label(frm, text="Día:").pack(side='left')
        self.day_var = tk.StringVar()
        days = [(datetime.today()+timedelta(days=i)).strftime(DATE_FORMAT)
                for i in range(1,MAX_DAYS+1)]
        self.cb_day = ttk.Combobox(frm, values=days, textvariable=self.day_var,
                                   state='readonly', width=15)
        self.cb_day.pack(side='left', padx=5)
        self.cb_day.bind('<<ComboboxSelected>>', lambda e: self.refresh_slots())

        # Hora
        frm2 = ttk.Frame(self); frm2.pack(pady=5)
        ttk.Label(frm2, text="Hora:").pack(side='left')
        self.time_var = tk.StringVar()
        self.cb_time = ttk.Combobox(frm2, values=[], textvariable=self.time_var,
                                    state='readonly', width=15)
        self.cb_time.pack(side='left', padx=5)

        self.msg = ttk.Label(self, text="", foreground='red')
        self.msg.pack(pady=5)

        # Botones
        fbtn = ttk.Frame(self); fbtn.pack(pady=15)
        ttk.Button(fbtn, text="Confirmar", width=12, command=self._confirm).pack(side='left', padx=5)
        ttk.Button(fbtn, text="Volver", width=12,
                   command=lambda: self.controller.show_page(
                       'AdminMenuPage' if self.controller.current_role=='admin'
                       else 'PlayerMenuPage'
                   )).pack(side='left', padx=5)

    def refresh_slots(self):
        fecha = self.day_var.get()
        slots = ReservationManager().get_available_slots(fecha) if fecha else []
        self.cb_time['values'] = slots
        self.time_var.set('')
        self.msg.config(text="No hay canchas disponibles." if not slots else "")

    def _confirm(self):
        fecha = self.day_var.get()
        hora  = self.time_var.get()
        uid   = self.controller.current_user_id
        if not fecha or not hora:
            return messagebox.showerror("Error","Selecciona día y hora.")
        ok,msg = ReservationManager().reservar(uid, fecha, hora)
        (messagebox.showinfo if ok else messagebox.showerror)("Reserva", msg)
        if ok:
            self.refresh_slots()

if __name__ == '__main__':
    App().mainloop()
