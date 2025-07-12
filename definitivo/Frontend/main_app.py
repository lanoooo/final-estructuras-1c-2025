#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

# Configurar rutas para importar desde Frontend hacia Backend (carpetas hermanas)
current_dir = os.path.dirname(os.path.abspath(__file__))  # Frontend/
parent_dir = os.path.dirname(current_dir)                # Directorio raíz del proyecto
backend_dir = os.path.join(parent_dir, 'Backend')       # Backend/
sys.path.insert(0, backend_dir)

print(f"Directorio actual: {current_dir}")
print(f"Directorio padre: {parent_dir}")
print(f"Directorio backend: {backend_dir}")

# Intentar importar PIL para manejo de imágenes
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL no disponible. Instale con: pip install Pillow")

# Importar el backend
try:
    from padel_backend import UsuarioManager, ReservationManager, TournamentManager  # type: ignore
    print("✓ Backend importado correctamente")
except ImportError as e:
    print(f"Error: No se pudo importar el backend: {e}")
    print(f"Backend existe: {os.path.exists(backend_dir)}")
    if os.path.exists(backend_dir):
        print(f"Archivos en backend: {os.listdir(backend_dir)}")
    sys.exit(1)

# Constantes
ADMIN_SECRET = "padel"
MAX_DAYS = 4
DATE_FORMAT = "%Y-%m-%d"

# Colores del tema oscuro
COLORS = {
    'bg_primary': '#0a0a0a',
    'bg_secondary': '#1a1a1a',
    'bg_tertiary': '#2a2a2a',
    'text_primary': '#ffffff',
    'text_secondary': '#cccccc',
    'accent': '#4a9eff',
    'success': '#4caf50',
    'error': '#f44336',
    'warning': '#ff9800',
    'button_bg': '#d4d4d4'
}

class ModernStyle:
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure('Modern.TFrame', 
                       background=COLORS['bg_primary'],
                       borderwidth=0)
        
        style.configure('Card.TFrame',
                       background=COLORS['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # Label styles
        style.configure('Title.TLabel',
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_primary'],
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Modern.TLabel',
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_primary'],
                       font=('Segoe UI', 11))
        
        style.configure('Card.TLabel',
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       font=('Segoe UI', 11))
        
        # Button styles
        style.configure('Modern.TButton',
                       background=COLORS['button_bg'],
                       foreground='black',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TButton',
                 background=[('active', '#c0c0c0'),
                           ('pressed', '#a0a0a0')])
        
        style.configure('Secondary.TButton',
                       background=COLORS['bg_tertiary'],
                       foreground=COLORS['text_primary'],
                       font=('Segoe UI', 11),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Danger.TButton',
                       background=COLORS['error'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Success.TButton',
                       background=COLORS['success'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        # Entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=COLORS['bg_tertiary'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       insertcolor=COLORS['text_primary'],
                       font=('Segoe UI', 11))
        
        # Combobox styles
        style.configure('Modern.TCombobox',
                       fieldbackground=COLORS['bg_tertiary'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       font=('Segoe UI', 11))
        
        # Treeview styles
        style.configure('Modern.Treeview',
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_secondary'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Modern.Treeview.Heading',
                       background=COLORS['bg_tertiary'],
                       foreground=COLORS['text_primary'],
                       font=('Segoe UI', 11, 'bold'))

class AuthService:
    @staticmethod
    def login(username, password):
        try:
            um = UsuarioManager()
            role, uid = um.iniciar_sesion(username, password)
            um.desconectar()
            return (True, role, uid) if role else (False, None, None)
        except Exception as e:
            print(f"Error en login: {e}")
            return (False, None, None)

    @staticmethod
    def register(username, password, role):
        try:
            um = UsuarioManager()
            ok = um.crear_usuario(username, password, role)
            um.desconectar()
            return ok
        except Exception as e:
            print(f"Error en registro: {e}")
            return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Padel Club - Sistema de Reservas")
        self.geometry("1400x900")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_primary'])
        
        ModernStyle.configure_styles()
        
        self.current_user_id = None
        self.current_role = None
        self.current_username = None
        
        self.create_main_container()
        self.create_pages()
        self.show_page('LoginPage')
        self.center_window()

    def create_main_container(self):
        self.container = ttk.Frame(self, style='Modern.TFrame')
        self.container.pack(fill='both', expand=True, padx=50, pady=50)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def create_pages(self):
        self.pages = {}
        page_classes = [LoginPage, RegisterPage, PlayerMenuPage, AdminMenuPage, 
                       ReservationPage, ViewReservationsPage, TournamentPage, 
                       TournamentRegistrationPage, TournamentManagementPage, AdminUsersPage]
        
        for PageClass in page_classes:
            page = PageClass(self.container, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky='nsew')

    def show_page(self, name):
        if name == 'ReservationPage':
            self.pages[name].refresh_slots()
        elif name == 'ViewReservationsPage':
            self.pages[name].refresh_reservations()
        elif name == 'TournamentRegistrationPage':
            self.pages[name].refresh_tournament_info()
        elif name == 'TournamentManagementPage':
            self.pages[name].refresh_tournament_data()
        self.pages[name].tkraise()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        main_container = ttk.Frame(self, style='Modern.TFrame')
        main_container.pack(fill='both', expand=True, padx=50, pady=50)
        
        content_frame = ttk.Frame(main_container, style='Modern.TFrame')
        content_frame.pack(fill='both', expand=True)
        
        # Frame para la imagen (lado izquierdo)
        image_frame = ttk.Frame(content_frame, style='Modern.TFrame')
        image_frame.pack(side='left', padx=(0, 60), fill='both', expand=True)
        
        # Cargar imagen desde assets (desde Frontend hacia assets)
        image_loaded = False
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))  # Frontend/
            parent_dir = os.path.dirname(current_dir)                # Directorio raíz
            image_path = os.path.join(parent_dir, 'assets', 'padel_court.png')  # assets/padel_court.png
            
            print(f"Buscando imagen en: {image_path}")
            print(f"Archivo existe: {os.path.exists(image_path)}")
            print(f"PIL disponible: {PIL_AVAILABLE}")
            
            if PIL_AVAILABLE and os.path.exists(image_path):
                from PIL import Image, ImageTk
                image = Image.open(image_path)
                image = image.resize((700, 500), Image.Resampling.LANCZOS)
                self.court_photo = ImageTk.PhotoImage(image)
                
                image_label = tk.Label(image_frame, image=self.court_photo, 
                              bg=COLORS['bg_primary'])
                image_label.pack(expand=True)
                image_loaded = True
                print("✓ Imagen cargada exitosamente")
            else:
                print("✗ No se pudo cargar la imagen")
                
        except Exception as e:
            print(f"Error cargando imagen: {e}")
        
        # Si no se pudo cargar la imagen, mostrar placeholder
        if not image_loaded:
            placeholder_label = ttk.Label(image_frame, text="🎾\n\nCANCHA\nDE PADEL\n\n🎾", 
                                    style='Modern.TLabel', 
                                    font=('Segoe UI', 20, 'bold'),
                                    justify='center')
            placeholder_label.pack(expand=True)
        
        # Frame para el formulario (lado derecho)
        form_frame = ttk.Frame(content_frame, style='Modern.TFrame')
        form_frame.pack(side='right', fill='both', expand=True)
        
        # Título
        ttk.Label(form_frame, text="PADEL CLUB", 
                 style='Title.TLabel').pack(pady=(20, 40))
        
        # Campo usuario
        ttk.Label(form_frame, text="Usuario", 
                 style='Modern.TLabel').pack(anchor='w', pady=(0, 8))
        self.user_var = tk.StringVar()
        user_entry = ttk.Entry(form_frame, textvariable=self.user_var, 
                          style='Modern.TEntry')
        user_entry.pack(fill='x', pady=(0, 20), ipady=10)
        
        # Campo contraseña
        ttk.Label(form_frame, text="Contraseña", 
                 style='Modern.TLabel').pack(anchor='w', pady=(0, 8))
        self.pass_var = tk.StringVar()
        pass_entry = ttk.Entry(form_frame, textvariable=self.pass_var, 
                          show='*', style='Modern.TEntry')
        pass_entry.pack(fill='x', pady=(0, 25), ipady=10)
        
        # Botón Iniciar
        login_btn = ttk.Button(form_frame, text="Iniciar", 
                          style='Modern.TButton', command=self._login)
        login_btn.pack(fill='x', pady=(0, 30), ipady=10)
        
        # Registro
        register_frame = ttk.Frame(form_frame, style='Modern.TFrame')
        register_frame.pack(pady=(10, 0))
        
        tk.Label(register_frame, text="¿No tienes una cuenta? ", 
                bg=COLORS['bg_primary'], fg=COLORS['text_secondary'],
                font=('Segoe UI', 10)).pack(side='left')
        
        register_link = tk.Label(register_frame, text="Regístrate", 
                               bg=COLORS['bg_primary'], fg=COLORS['text_primary'],
                               font=('Segoe UI', 10, 'underline'),
                               cursor='hand2')
        register_link.pack(side='left')
        register_link.bind('<Button-1>', lambda e: self.controller.show_page('RegisterPage'))
        
        # Bind Enter key
        user_entry.bind('<Return>', lambda e: pass_entry.focus())
        pass_entry.bind('<Return>', lambda e: self._login())

    def _login(self):
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        ok, role, uid = AuthService.login(username, password)
        if not ok:
            messagebox.showerror("Error", "Credenciales inválidas")
            return
        
        if role == 'admin':
            code = simpledialog.askstring("Administrador", 
                                        "Ingrese la clave maestra:", show='*')
            if code != ADMIN_SECRET:
                messagebox.showerror("Error", "Clave de administrador incorrecta")
                return
        
        self.controller.current_role = role
        self.controller.current_user_id = uid
        self.controller.current_username = username
        
        self.user_var.set('')
        self.pass_var.set('')
        
        next_page = 'AdminMenuPage' if role == 'admin' else 'PlayerMenuPage'
        self.controller.show_page(next_page)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Crear un frame con scroll
        main_frame = ttk.Frame(self, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Título
        title_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        title_frame.pack(pady=(20, 20))
        
        ttk.Label(title_frame, text="REGISTRO DE CUENTA", 
                 style='Title.TLabel').pack()
        
        # Tarjeta de registro con altura fija
        card_frame = ttk.Frame(main_frame, style='Card.TFrame')
        card_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        content_frame = ttk.Frame(card_frame, style='Card.TFrame')
        content_frame.pack(padx=30, pady=30, fill='both', expand=True)
        
        # Campos del formulario con espaciado reducido
        fields = [
            ("Usuario *", "user_var"),
            ("Contraseña *", "pass_var"),
            ("Rol *", "role_var"),
            ("Clave Admin (solo para admin)", "key_var")
        ]
        
        self.vars = {}
        for label_text, var_name in fields:
            ttk.Label(content_frame, text=label_text, 
                     style='Card.TLabel').pack(anchor='w', pady=(0, 3))
            
            self.vars[var_name] = tk.StringVar()
            
            if var_name == "role_var":
                widget = ttk.Combobox(content_frame, textvariable=self.vars[var_name],
                                    values=['jugador', 'admin'], state='readonly',
                                    style='Modern.TCombobox')
            else:
                show_char = '*' if 'pass' in var_name or 'key' in var_name else ''
                widget = ttk.Entry(content_frame, textvariable=self.vars[var_name],
                                 show=show_char, style='Modern.TEntry')
            
            widget.pack(fill='x', pady=(0, 10), ipady=6)
        
        # Nota
        ttk.Label(content_frame, text="* Campo obligatorio", 
                 style='Card.TLabel', font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 15))
        
        # Botones
        btn_frame = ttk.Frame(content_frame, style='Card.TFrame')
        btn_frame.pack(fill='x')
        
        register_btn = ttk.Button(btn_frame, text="Registrarse", 
                                 style='Modern.TButton', command=self._register)
        register_btn.pack(fill='x', pady=(0, 8), ipady=6)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", 
                               style='Secondary.TButton',
                               command=lambda: self.controller.show_page('LoginPage'))
        cancel_btn.pack(fill='x', ipady=6)

    def _register(self):
        username = self.vars['user_var'].get().strip()
        password = self.vars['pass_var'].get().strip()
        role = self.vars['role_var'].get().strip()
        admin_key = self.vars['key_var'].get().strip()
        
        if not username or not password or not role:
            messagebox.showerror("Error", "Complete los campos obligatorios")
            return
        
        if role == 'admin' and admin_key != ADMIN_SECRET:
            messagebox.showerror("Error", "Clave de administrador inválida")
            return
        
        if AuthService.register(username, password, role):
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            
            # Iniciar sesión automáticamente después del registro
            ok, user_role, uid = AuthService.login(username, password)
            if ok:
                if user_role == 'admin':
                    code = simpledialog.askstring("Administrador", 
                                                "Ingrese la clave maestra:", show='*')
                    if code != ADMIN_SECRET:
                        messagebox.showerror("Error", "Clave de administrador incorrecta")
                        for var in self.vars.values():
                            var.set('')
                        self.controller.show_page('LoginPage')
                        return
                
                # Configurar sesión
                self.controller.current_role = user_role
                self.controller.current_user_id = uid
                self.controller.current_username = username
                
                # Limpiar formulario
                for var in self.vars.values():
                    var.set('')
                
                # Ir al menú correspondiente
                next_page = 'AdminMenuPage' if user_role == 'admin' else 'PlayerMenuPage'
                self.controller.show_page(next_page)
            else:
                # Si falla el login automático, ir a login manual
                for var in self.vars.values():
                    var.set('')
                self.controller.show_page('LoginPage')
        else:
            messagebox.showerror("Error", "Error al registrar usuario")

class PlayerMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 40))
        
        ttk.Label(header_frame, text="MENÚ JUGADOR", 
                 style='Title.TLabel').pack()
        
        menu_frame = ttk.Frame(self, style='Modern.TFrame')
        menu_frame.pack(expand=True)
        
        buttons = [
            ("Reservar Cancha", lambda: self.controller.show_page('ReservationPage')),
            ("Ver Mis Reservas", lambda: self.controller.show_page('ViewReservationsPage')),
            ("Inscribirse a Torneo", lambda: self.controller.show_page('TournamentRegistrationPage')),
            ("Cerrar Sesión", self._logout)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(menu_frame, text=text, style='Modern.TButton', 
                           command=command)
            btn.pack(pady=10, ipadx=40, ipady=12)

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class AdminMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 40))
        
        ttk.Label(header_frame, text="PANEL DE ADMINISTRACIÓN", 
                 style='Title.TLabel').pack()
        
        menu_frame = ttk.Frame(self, style='Modern.TFrame')
        menu_frame.pack(expand=True)
        
        buttons = [
            ("Ver Reservas", lambda: self.controller.show_page('ViewReservationsPage')),
            ("Gestionar Torneo de Padel", lambda: self.controller.show_page('TournamentPage')),
            ("Ver Usuarios", lambda: self.controller.show_page('AdminUsersPage')),
            ("Cerrar Sesión", self._logout)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(menu_frame, text=text, style='Modern.TButton', 
                           command=command)
            btn.pack(pady=10, ipadx=40, ipady=12)

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class ReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(header_frame, text="Cerrar sesión", style='Secondary.TButton',
                  command=self._logout).pack(side='right')
        
        title_frame = ttk.Frame(self, style='Modern.TFrame')
        title_frame.pack(pady=(20, 30))
        
        ttk.Label(title_frame, text="Reservar cancha", 
                 style='Title.TLabel').pack()
        
        form_frame = ttk.Frame(self, style='Card.TFrame')
        form_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        content_frame = ttk.Frame(form_frame, style='Card.TFrame')
        content_frame.pack(padx=40, pady=40, fill='both', expand=True)
        
        # Fecha
        ttk.Label(content_frame, text="Fecha", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.day_var = tk.StringVar()
        days = [(datetime.today() + timedelta(days=i)).strftime(DATE_FORMAT)
                for i in range(1, MAX_DAYS + 1)]
        self.cb_day = ttk.Combobox(content_frame, values=days, textvariable=self.day_var,
                                  state='readonly', style='Modern.TCombobox')
        self.cb_day.pack(fill='x', pady=(0, 20), ipady=8)
        self.cb_day.bind('<<ComboboxSelected>>', lambda e: self.refresh_slots())
        
        # Hora
        ttk.Label(content_frame, text="Hora", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.time_var = tk.StringVar()
        self.cb_time = ttk.Combobox(content_frame, values=[], textvariable=self.time_var,
                                   state='readonly', style='Modern.TCombobox')
        self.cb_time.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Mensaje de estado
        self.msg_label = ttk.Label(content_frame, text="", style='Card.TLabel')
        self.msg_label.pack(pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(content_frame, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        confirm_btn = ttk.Button(btn_frame, text="Confirmar reserva", 
                               style='Modern.TButton', command=self._confirm)
        confirm_btn.pack(fill='x', pady=(0, 10), ipady=8)
        
        back_btn = ttk.Button(btn_frame, text="Volver", style='Secondary.TButton',
                             command=self._go_back)
        back_btn.pack(fill='x', ipady=8)

    def refresh_slots(self):
        fecha = self.day_var.get()
        if not fecha:
            return
        
        try:
            rm = ReservationManager()
            slots = rm.get_available_slots(fecha)
            rm.desconectar()
            self.cb_time['values'] = slots
            self.time_var.set('')
            
            if not slots:
                self.msg_label.config(text="No hay canchas disponibles para esta fecha")
            else:
                self.msg_label.config(text="")
        except Exception as e:
            self.msg_label.config(text=f"Error al cargar horarios: {str(e)}")

    def _confirm(self):
        fecha = self.day_var.get()
        hora = self.time_var.get()
        uid = self.controller.current_user_id
        
        if not fecha or not hora:
            messagebox.showerror("Error", "Seleccione fecha y hora")
            return
        
        try:
            rm = ReservationManager()
            ok, msg = rm.reservar(uid, fecha, hora)
            rm.desconectar()
            
            if ok:
                messagebox.showinfo("Reserva", msg)
                self.refresh_slots()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar reserva: {str(e)}")

    def _go_back(self):
        if self.controller.current_role == 'admin':
            self.controller.show_page('AdminMenuPage')
        else:
            self.controller.show_page('PlayerMenuPage')

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class ViewReservationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.header_frame = ttk.Frame(self, style='Modern.TFrame')
        self.header_frame.pack(fill='x', pady=(20, 0))
        ttk.Button(self.header_frame, text="Cerrar sesión", style='Secondary.TButton',
                  command=self._logout).pack(side='right')

        self.title_frame = ttk.Frame(self, style='Modern.TFrame')
        self.title_frame.pack(pady=(20, 30))
        self.title_label = ttk.Label(self.title_frame, text="", style='Title.TLabel')
        self.title_label.pack()

        self.table_frame = ttk.Frame(self, style='Card.TFrame')
        self.table_frame.pack(pady=20, padx=40, fill='both', expand=True)

        self.btn_frame = ttk.Frame(self, style='Modern.TFrame')
        self.btn_frame.pack(pady=20)
        self.delete_btn = ttk.Button(self.btn_frame, text="Eliminar Reserva", 
                               style='Danger.TButton',
                               command=self._delete_reservation)
        self.delete_btn.pack(side='left', padx=(0, 10), ipady=8, ipadx=20)
        self.back_btn = ttk.Button(self.btn_frame, text="Volver", style='Secondary.TButton',
                             command=self._go_back)
        self.back_btn.pack(side='left', ipady=8, ipadx=20)

        self.tree = None  # Se creará dinámicamente en refresh_reservations
        self.scrollbar = None

    def refresh_reservations(self):
        # Limpiar tabla y título anteriores
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        # Título
        if self.controller.current_role == 'admin':
            title_text = "Todas las Reservas"
            columns = ('ID', 'Fecha', 'Hora', 'Cancha', 'Usuario')
        else:
            title_text = "Mis Reservas"
            columns = ('Fecha', 'Hora', 'Cancha', 'Usuario')
        self.title_label.config(text=title_text)
        # Crear nueva tabla
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', style='Modern.Treeview')
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50, anchor='center')
            elif col == 'Fecha':
                self.tree.column(col, width=120, anchor='center')
            elif col == 'Hora':
                self.tree.column(col, width=100, anchor='center')
            elif col == 'Cancha':
                self.tree.column(col, width=100, anchor='center')
            elif col == 'Usuario':
                self.tree.column(col, width=140, anchor='center')
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=20)
        self.scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=20)
        # Llenar datos
        try:
            rm = ReservationManager()
            is_admin = self.controller.current_role == 'admin'
            user_id = self.controller.current_user_id
            reservations = rm.get_reservations_with_ids(user_id, is_admin)
            rm.desconectar()
            for res_id, dia, hora, cancha, usuario in reservations:
                if is_admin:
                    item_id = self.tree.insert('', 'end', values=(res_id, dia, hora, cancha, usuario))
                else:
                    item_id = self.tree.insert('', 'end', values=(dia, hora, cancha, usuario), tags=(res_id,))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar reservas: {str(e)}")

    def _delete_reservation(self):
        if self.tree is None:
            messagebox.showwarning("Advertencia", "No hay reservas para eliminar")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para eliminar")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if self.controller.current_role == 'admin':
            # Para admin: ID está en la primera columna
            res_id = values[0]
            fecha = values[1]
            hora = values[2]
            usuario = values[4]
        else:
            # Para jugadores: ID está en los tags
            res_id = item['tags'][0]
            fecha = values[0]
            hora = values[1]
            usuario = values[3]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar la reserva de {usuario} "
                              f"para el {fecha} a las {hora}?"):
            try:
                rm = ReservationManager()
                is_admin = self.controller.current_role == 'admin'
                user_id = self.controller.current_user_id
                
                ok, msg = rm.delete_reservation(res_id, user_id, is_admin)
                rm.desconectar()
                
                if ok:
                    messagebox.showinfo("Éxito", msg)
                    self.refresh_reservations()
                else:
                    messagebox.showerror("Error", msg)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar reserva: {str(e)}")

    def _go_back(self):
        if self.controller.current_role == 'admin':
            self.controller.show_page('AdminMenuPage')
        else:
            self.controller.show_page('PlayerMenuPage')

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class TournamentPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(header_frame, text="Cerrar sesión", style='Secondary.TButton',
                  command=self._logout).pack(side='right')
        
        title_frame = ttk.Frame(self, style='Modern.TFrame')
        title_frame.pack(pady=(20, 30))
        
        ttk.Label(title_frame, text="🏆 CREAR TORNEO DE PADEL", 
                 style='Title.TLabel').pack()
        
        # Contenedor principal con scroll
        main_container = ttk.Frame(self, style='Modern.TFrame')
        main_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        form_frame = ttk.Frame(main_container, style='Card.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        content_frame = ttk.Frame(form_frame, style='Card.TFrame')
        content_frame.pack(padx=40, pady=40, fill='both', expand=True)
        
        # Nombre del torneo
        ttk.Label(content_frame, text="Nombre del Torneo", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(content_frame, textvariable=self.name_var, 
                              style='Modern.TEntry')
        name_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Fecha del torneo
        ttk.Label(content_frame, text="Fecha del Torneo (Sábados disponibles)", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.date_var = tk.StringVar()
        self.cb_date = ttk.Combobox(content_frame, textvariable=self.date_var,
                                   state='readonly', style='Modern.TCombobox')
        self.cb_date.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Máximo de equipos
        ttk.Label(content_frame, text="Máximo de Equipos", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.max_teams_var = tk.StringVar(value="8")
        max_teams_cb = ttk.Combobox(content_frame, textvariable=self.max_teams_var,
                                   values=['4', '6', '8', '10', '12', '16'], 
                                   state='readonly', style='Modern.TCombobox')
        max_teams_cb.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Mensaje de estado
        self.msg_label = ttk.Label(content_frame, text="", style='Card.TLabel')
        self.msg_label.pack(pady=(0, 20))
        
        # Botones - ASEGURAR QUE ESTÉN VISIBLES
        btn_frame = ttk.Frame(content_frame, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        create_btn = ttk.Button(btn_frame, text="Crear Torneo", 
                               style='Success.TButton', command=self._create_tournament)
        create_btn.pack(fill='x', pady=(0, 10), ipady=10)
        
        manage_btn = ttk.Button(btn_frame, text="Gestionar Torneos", 
                               style='Modern.TButton', 
                               command=lambda: self.controller.show_page('TournamentManagementPage'))
        manage_btn.pack(fill='x', pady=(0, 10), ipady=10)
        
        back_btn = ttk.Button(btn_frame, text="Volver atrás", style='Secondary.TButton',
                             command=lambda: self.controller.show_page('AdminMenuPage'))
        back_btn.pack(fill='x', ipady=10)
        
        # Cargar fechas disponibles
        self._load_available_dates()

    def _load_available_dates(self):
        try:
            tm = TournamentManager()
            saturdays = tm.get_available_saturdays()
            tm.desconectar()
            
            # Formatear fechas para mostrar en dd/mm/aaaa
            formatted_dates = []
            for date_str in saturdays:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted = date_obj.strftime("%d/%m/%Y (%A)")
                formatted_dates.append(f"{formatted}")
            self.cb_date['values'] = formatted_dates
            self.msg_label.config(text=f"Fechas disponibles: próximos {len(saturdays)} sábados")
        except Exception as e:
            self.msg_label.config(text=f"Error al cargar fechas: {str(e)}")

    def _create_tournament(self):
        name = self.name_var.get().strip()
        date_selection = self.date_var.get()
        max_teams = self.max_teams_var.get()
        
        if not name or not date_selection or not max_teams:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        # Extraer la fecha del formato "dd/mm/yyyy (Day)"
        date_str = date_selection.split(' ')[0]  # dd/mm/yyyy
        # Convertir a yyyy-mm-dd para la base de datos
        try:
            date_db = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Formato de fecha inválido")
            return
        try:
            tm = TournamentManager()
            ok, result = tm.create_tournament(name, date_db, int(max_teams))
            tm.desconectar()
            if ok:
                messagebox.showinfo("Éxito", f"Torneo '{name}' creado exitosamente!\nID del torneo: {result}")
                self.name_var.set('')
                self.date_var.set('')
                self.max_teams_var.set('8')
            else:
                messagebox.showerror("Error", f"Error al crear torneo: {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear torneo: {str(e)}")

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class TournamentRegistrationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(header_frame, text="Cerrar sesión", style='Secondary.TButton',
                  command=self._logout).pack(side='right')
        
        title_frame = ttk.Frame(self, style='Modern.TFrame')
        title_frame.pack(pady=(20, 30))
        
        ttk.Label(title_frame, text="🏆 INSCRIPCIÓN A TORNEO", 
                 style='Title.TLabel').pack()
        
        # Info del torneo
        self.info_frame = ttk.Frame(self, style='Card.TFrame')
        self.info_frame.pack(pady=(0, 20), padx=40, fill='x')
        
        self.info_content = ttk.Frame(self.info_frame, style='Card.TFrame')
        self.info_content.pack(padx=20, pady=20, fill='x')
        
        self.tournament_info_label = ttk.Label(self.info_content, text="Cargando información del torneo...", 
                                              style='Card.TLabel', font=('Segoe UI', 12))
        self.tournament_info_label.pack()
        
        # Formulario de inscripción
        form_frame = ttk.Frame(self, style='Card.TFrame')
        form_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        content_frame = ttk.Frame(form_frame, style='Card.TFrame')
        content_frame.pack(padx=40, pady=40, fill='both', expand=True)
        
        # Nombre del equipo
        ttk.Label(content_frame, text="Nombre del Equipo", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.team_name_var = tk.StringVar()
        team_entry = ttk.Entry(content_frame, textvariable=self.team_name_var, 
                              style='Modern.TEntry')
        team_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Jugador 1
        ttk.Label(content_frame, text="Jugador 1", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.player1_var = tk.StringVar()
        player1_entry = ttk.Entry(content_frame, textvariable=self.player1_var, 
                                 style='Modern.TEntry')
        player1_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Jugador 2
        ttk.Label(content_frame, text="Jugador 2", 
                 style='Card.TLabel').pack(anchor='w', pady=(0, 5))
        self.player2_var = tk.StringVar()
        player2_entry = ttk.Entry(content_frame, textvariable=self.player2_var, 
                                 style='Modern.TEntry')
        player2_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Mensaje de estado
        self.msg_label = ttk.Label(content_frame, text="", style='Card.TLabel')
        self.msg_label.pack(pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(content_frame, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        self.register_btn = ttk.Button(btn_frame, text="Inscribir Equipo", 
                                      style='Success.TButton', command=self._register_team)
        self.register_btn.pack(fill='x', pady=(0, 10), ipady=8)
        
        back_btn = ttk.Button(btn_frame, text="Volver al Menú", style='Secondary.TButton',
                             command=lambda: self.controller.show_page('PlayerMenuPage'))
        back_btn.pack(fill='x', ipady=8)

    def refresh_tournament_info(self):
        try:
            tm = TournamentManager()
            tournament = tm.get_active_tournament()
            
            if tournament:
                self.tournament_id, name, date, max_teams = tournament
                teams = tm.get_tournament_teams(self.tournament_id)
                current_teams = len(teams)
                
                # Manejar fecha como str o datetime.date
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                else:
                    date_obj = date  # Ya es datetime.date
                formatted_date = date_obj.strftime("%d/%m/%Y")
                
                info_text = (f"🏆 {name}\n"
                           f"📅 Fecha: {formatted_date}\n"
                           f"👥 Equipos: {current_teams}/{max_teams}")
                
                self.tournament_info_label.config(text=info_text)
                
                if current_teams >= max_teams:
                    self.msg_label.config(text="⚠️ Torneo completo")
                    self.register_btn.config(state='disabled')
                else:
                    self.msg_label.config(text=f"✅ Quedan {max_teams - current_teams} cupos disponibles")
                    self.register_btn.config(state='normal')
            else:
                self.tournament_info_label.config(text="❌ No hay torneos abiertos para inscripción")
                self.register_btn.config(state='disabled')
                self.tournament_id = None
            
            tm.desconectar()
            
        except Exception as e:
            self.tournament_info_label.config(text=f"Error al cargar torneo: {str(e)}")
            self.register_btn.config(state='disabled')

    def _register_team(self):
        if not self.tournament_id:
            messagebox.showerror("Error", "No hay torneo disponible")
            return
        
        team_name = self.team_name_var.get().strip()
        player1 = self.player1_var.get().strip()
        player2 = self.player2_var.get().strip()
        
        if not team_name or not player1 or not player2:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        try:
            tm = TournamentManager()
            ok, msg = tm.register_team(self.tournament_id, team_name, player1, player2, 
                                     self.controller.current_user_id)
            tm.desconectar()
            
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.team_name_var.set('')
                self.player1_var.set('')
                self.player2_var.set('')
                self.refresh_tournament_info()
            else:
                messagebox.showerror("Error", msg)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al inscribir equipo: {str(e)}")

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class TournamentManagementPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(header_frame, text="Cerrar sesión", style='Secondary.TButton',
                  command=self._logout).pack(side='right')
        
        title_frame = ttk.Frame(self, style='Modern.TFrame')
        title_frame.pack(pady=(20, 30))
        
        ttk.Label(title_frame, text="🏆 GESTIÓN DE TORNEOS", 
                 style='Title.TLabel').pack()
        
        # Información del torneo activo
        info_frame = ttk.Frame(self, style='Card.TFrame')
        info_frame.pack(pady=(0, 20), padx=40, fill='x')
        
        info_content = ttk.Frame(info_frame, style='Card.TFrame')
        info_content.pack(padx=20, pady=20, fill='x')
        
        self.tournament_info_label = ttk.Label(info_content, text="Cargando...", 
                                              style='Card.TLabel', font=('Segoe UI', 12))
        self.tournament_info_label.pack()
        
        # Tabla de equipos
        teams_frame = ttk.Frame(self, style='Card.TFrame')
        teams_frame.pack(pady=(0, 20), padx=40, fill='both', expand=True)
        
        ttk.Label(teams_frame, text="Equipos Inscritos", 
                 style='Card.TLabel', font=('Segoe UI', 14, 'bold')).pack(pady=(20, 10))
        
        # Treeview para equipos
        columns = ('ID', 'Equipo', 'Jugador 1', 'Jugador 2', 'Usuario')
        self.teams_tree = ttk.Treeview(teams_frame, columns=columns, show='headings',
                                      style='Modern.Treeview', height=6)
        
        for col in columns:
            self.teams_tree.heading(col, text=col)
            self.teams_tree.column(col, width=120, anchor='center')
        
        teams_scrollbar = ttk.Scrollbar(teams_frame, orient='vertical', command=self.teams_tree.yview)
        self.teams_tree.configure(yscrollcommand=teams_scrollbar.set)
        
        self.teams_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        teams_scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=(0, 20))
        
        # Botones de acción
        btn_frame = ttk.Frame(self, style='Modern.TFrame')
        btn_frame.pack(pady=20)
        
        self.generate_btn = ttk.Button(btn_frame, text="Generar Fixture", 
                                      style='Success.TButton', command=self._generate_fixture)
        self.generate_btn.pack(side='left', padx=(0, 10), ipady=8, ipadx=20)
        
        view_matches_btn = ttk.Button(btn_frame, text="Ver Partidos", 
                                     style='Modern.TButton', command=self._view_matches)
        view_matches_btn.pack(side='left', padx=(0, 10), ipady=8, ipadx=20)
        
        back_btn = ttk.Button(btn_frame, text="Volver", style='Secondary.TButton',
                             command=lambda: self.controller.show_page('TournamentPage'))
        back_btn.pack(side='left', ipady=8, ipadx=20)

    def refresh_tournament_data(self):
        try:
            tm = TournamentManager()
            tournament = tm.get_active_tournament()
            
            if tournament:
                self.tournament_id, name, date, max_teams = tournament
                teams = tm.get_tournament_teams(self.tournament_id)
                
                # Manejar fecha como str o datetime.date
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                else:
                    date_obj = date  # Ya es datetime.date
                formatted_date = date_obj.strftime("%d/%m/%Y")
                
                info_text = (f"🏆 {name}\n"
                           f"📅 Fecha: {formatted_date}\n"
                           f"👥 Equipos inscritos: {len(teams)}/{max_teams}")
                
                self.tournament_info_label.config(text=info_text)
                
                # Limpiar y llenar tabla de equipos
                for item in self.teams_tree.get_children():
                    self.teams_tree.delete(item)
                
                for team in teams:
                    team_id, team_name, player1, player2, username = team
                    self.teams_tree.insert('', 'end', values=(team_id, team_name, player1, player2, username))
                
                # Habilitar botón de fixture si hay al menos 2 equipos
                if len(teams) >= 2:
                    self.generate_btn.config(state='normal')
                else:
                    self.generate_btn.config(state='disabled')
                    
            else:
                self.tournament_info_label.config(text="❌ No hay torneos activos")
                self.generate_btn.config(state='disabled')
                self.tournament_id = None
            
            tm.desconectar()
            
        except Exception as e:
            self.tournament_info_label.config(text=f"Error: {str(e)}")

    def _generate_fixture(self):
        if not self.tournament_id:
            messagebox.showerror("Error", "No hay torneo activo")
            return
        
        if messagebox.askyesno("Confirmar", "¿Generar fixture del torneo?\n"
                                          "Esto cerrará las inscripciones."):
            try:
                tm = TournamentManager()
                ok, msg = tm.generate_fixture(self.tournament_id)
                tm.desconectar()
                
                if ok:
                    messagebox.showinfo("Éxito", msg)
                    self.refresh_tournament_data()
                else:
                    messagebox.showerror("Error", msg)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar fixture: {str(e)}")

    def _view_matches(self):
        if not self.tournament_id:
            messagebox.showerror("Error", "No hay torneo activo")
            return
        
        try:
            tm = TournamentManager()
            matches = tm.get_tournament_matches(self.tournament_id)
            tm.desconectar()
            
            if not matches:
                messagebox.showinfo("Info", "No hay partidos generados aún")
                return
            
            # Crear ventana para mostrar partidos
            matches_window = tk.Toplevel(self)
            matches_window.title("Fixture del Torneo")
            matches_window.geometry("600x400")
            matches_window.configure(bg=COLORS['bg_primary'])
            
            # Tabla de partidos
            columns = ('Partido', 'Equipo 1', 'Equipo 2', 'Estado')
            matches_tree = ttk.Treeview(matches_window, columns=columns, show='headings',
                                       style='Modern.Treeview')
            
            for col in columns:
                matches_tree.heading(col, text=col)
                matches_tree.column(col, width=140, anchor='center')
            
            for match in matches:
                match_id, match_num, team1, team2, score1, score2, status = match
                status_text = "Pendiente" if status == 'pendiente' else f"{score1}-{score2}"
                matches_tree.insert('', 'end', values=(f"Partido {match_num}", team1, team2, status_text))
            
            matches_tree.pack(fill='both', expand=True, padx=20, pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar partidos: {str(e)}")

    def _delete_tournament(self):
        if not hasattr(self, 'tournament_id') or not self.tournament_id:
            messagebox.showerror("Error", "No hay torneo activo para eliminar")
            return
        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar el torneo actual? Esta acción no se puede deshacer."):
            return
        try:
            tm = TournamentManager()
            ok, msg = tm.delete_tournament(self.tournament_id)
            tm.desconectar()
            if ok:
                messagebox.showinfo("Éxito", "Torneo eliminado correctamente")
                self.refresh_tournament_data()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar torneo: {str(e)}")

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

class AdminUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(20, 0))
        ttk.Button(header_frame, text="Cerrar sesión", style='Secondary.TButton', command=self._logout).pack(side='right')
        title_frame = ttk.Frame(self, style='Modern.TFrame')
        title_frame.pack(pady=(20, 30))
        ttk.Label(title_frame, text="👤 GESTIÓN DE USUARIOS", style='Title.TLabel').pack()
        table_frame = ttk.Frame(self, style='Card.TFrame')
        table_frame.pack(pady=20, padx=40, fill='both', expand=True)
        columns = ('Usuario', 'Rol')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor='center')
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=20)
        btn_frame = ttk.Frame(self, style='Modern.TFrame')
        btn_frame.pack(pady=20)
        delete_btn = ttk.Button(btn_frame, text="Eliminar Usuario", style='Danger.TButton', command=self._delete_user)
        delete_btn.pack(side='left', padx=(0, 10), ipady=8, ipadx=20)
        back_btn = ttk.Button(btn_frame, text="Volver", style='Secondary.TButton', command=lambda: self.controller.show_page('AdminMenuPage'))
        back_btn.pack(side='left', ipady=8, ipadx=20)
        self.refresh_users()

    def refresh_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            from padel_backend import UsuarioManager  # type: ignore
            um = UsuarioManager()
            um.cursor.execute("SELECT usuario, tipo FROM usuarios")
            users = um.cursor.fetchall()
            um.desconectar()
            for usuario, tipo in users:
                self.tree.insert('', 'end', values=(usuario, tipo))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {str(e)}")

    def _delete_user(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return
        item = self.tree.item(selection[0])
        usuario = item['values'][0]
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el usuario '{usuario}'?"):
            return
        try:
            from padel_backend import UsuarioManager  # type: ignore
            um = UsuarioManager()
            um.cursor.execute("DELETE FROM usuarios WHERE usuario = %s", (usuario,))
            um.db.commit()
            um.desconectar()
            self.refresh_users()
            messagebox.showinfo("Éxito", f"Usuario '{usuario}' eliminado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")

    def _logout(self):
        self.controller.current_user_id = None
        self.controller.current_role = None
        self.controller.current_username = None
        self.controller.show_page('LoginPage')

if __name__ == '__main__':
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
