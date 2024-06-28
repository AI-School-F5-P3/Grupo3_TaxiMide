import hashlib 
import re    
import os
import json   #importamos librerias
import time
import logging
import argparse
import tkinter as tk
import customtkinter
from tkinter import messagebox, simpledialog
import sqlite3

# Obtener el directorio actual del script en ejecución y asignarlo a la variable current_dir
current_dir = os.path.dirname(os.path.abspath(__file__))

# Definir la ruta de la carpeta "records" en el directorio superior y asignarlo a la variable records_dir
records_dir = os.path.join(current_dir, "records")

# Crear directorio "records" si no existe
if not os.path.exists(records_dir):
    os.makedirs(records_dir)

# Definir las rutas de los archivos basadas en la carpeta "records"
password_path = os.path.join(records_dir, "password.json")
db_path = os.path.join(records_dir, "taximetro.db")
log_path = os.path.join(records_dir, "taximideapp.log")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_path), 
    logging.StreamHandler()  
])

class CustomPasswordDialog(tk.Toplevel):
    def __init__(self, parent, message, title="Autenticación"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        
        self.body_frame = tk.Frame(self, bg="dodgerblue")
        self.body_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.body_frame, text=message, font=("Helvetica", 16), bg="dodgerblue", fg="black")
        self.label.pack(pady=(0, 10))

        self.entry = tk.Entry(self.body_frame, show="*", font=("Helvetica", 12), bg="lightgrey", fg="black")
        self.entry.pack(pady=(10, 10))
        self.entry.focus_set()

        self.ok_button = customtkinter.CTkButton(self.body_frame, text="OK", command=self.ok, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.ok_button.pack(side=tk.LEFT, padx=50)

        self.cancel_button = customtkinter.CTkButton(self.body_frame, text="Cancel", command=self.cancel, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.cancel_button.pack(side=tk.RIGHT, padx=50)
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.grab_set()
        self.geometry("500x200")
        self.attributes('-topmost', True)
        self.result = None

        self.bind("<Return>", lambda event: self.ok())
        self.bind("<Escape>", lambda event: self.cancel())
        
    def ok(self):
        self.result = self.entry.get()
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.parent.destroy()

class CustomNotificationDialog(tk.Toplevel):
    def __init__(self, parent, message, title, color):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        
        self.body_frame = tk.Frame(self, bg=color)
        self.body_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.body_frame, text=message, font=("Helvetica", 14), bg=color, fg="black", wraplength=300)
        self.label.pack(pady=(5, 20))

        self.ok_button = customtkinter.CTkButton(self.body_frame, text="OK", command=self.destroy, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.ok_button.pack(pady=5)
        

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.geometry("500x250")
        self.attributes('-topmost', True)

        self.bind("<Return>", lambda event: self.destroy())


class Taximetro:
    def __init__(self, contraseña, root):
        self.db_path = 'taximetro.db'
        self.tarifa_parado = 0.02
        self.tarifa_movimiento = 0.05
        self.tiempo_total = 0
        self.total_euros = 0
        self.carrera_iniciada = False
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
        self.password_hash = self.hash_password(contraseña)
        self.password_plaintext = contraseña
        self.autenticado = False
        self.conexion_bd = None
        self.root = root  # Inicializamos self.root
        self.load_password(contraseña)
        self.crear_tabla_registros()
        logging.info("Taxímetro iniciado con tarifas por defecto y contraseña establecida.")

    def show_custom_error(self, message):
        CustomNotificationDialog(self.root, message, "Error", "tomato")

    def show_custom_warning(self, message):
        CustomNotificationDialog(self.root, message, "Warning", "dark goldenrod")

    def show_custom_info(self, message):
        CustomNotificationDialog(self.root, message, "Info", "cyan")
        
        #programamos hashing de contraseñas
    def hash_password(self, password):
        password_bytes = password.encode('utf-8')
        hasher = hashlib.sha256()
        hasher.update(password_bytes)
        password_hash = hasher.hexdigest()
        
        return password_hash
    
    def save_password(self):
        data = {
            "password_hash": self.password_hash
        }
        with open(password_path, "w") as f:
            json.dump(data, f)
        logging.info("Contraseña guardada")
    
    def load_password(self, default_password):
        try:
            with open(password_path, "r") as f:
                data = json.load(f)
            self.password_hash = data["password_hash"]
            
            logging.info("Contraseña cargada")

        except FileNotFoundError:
            self.password_hash = self.hash_password(default_password)
            self.password_plaintext = default_password
            self.save_password()
            logging.info("Contraseña por defecto establecida")

    def empezar_carrera(self):
        if not self.carrera_iniciada:
            self.carrera_iniciada = False
            self.resetear_valores()
            self.tiempo_ultimo_cambio = time.time()
            self.en_movimiento = False  # Ensure we start in "parado" state
            self.estado_label.configure(text="Taxi en parado.")
            self.boton_empezar_carrera.configure(state=tk.DISABLED)
            self.boton_marcha.configure(state=tk.NORMAL)
            self.boton_parada.configure(state=tk.DISABLED)  # Disable "Parada" button initially
            self.canva_fin.configure(state=tk.NORMAL)
            logging.info("Carrera iniciada. Taxi en parado.")
            self.actualizar_tiempo_costo()
        

    def iniciar_carrera(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main window initially
        self.autenticar(root)
        if not self.autenticado:
            root.quit()
            return
        
        self.root.deiconify()
        self.root.title("TaxiMide")
        self.root.geometry("600x500")

        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "logo.png")
        
        #aquí creamos la división de los box donde irán cada elemento dentro
        self.frame_izquierda = tk.Frame(self.root, width=200,bg="dodgerblue" )
        self.frame_izquierda.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_derecha = tk.Frame(self.root, bg="grey24")
        self.frame_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_derecha_arriba = tk.Frame(self.frame_derecha, height=400, bg="light goldenrod")
        self.frame_derecha_arriba.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.estado_label = tk.Label(self.frame_derecha_arriba, text="Estado: Taxi en parado", font=("Helvetica", 18), bg="light goldenrod", fg="black")
        self.estado_label.pack(pady=(100, 10))
        
        self.tiempo_total_label = tk.Label(self.frame_derecha_arriba, text="Tiempo Total: 0 segundos", font=("Helvetica", 14), bg="light goldenrod", fg="black")
        self.tiempo_total_label.pack(pady=10)
        
        self.tiempo_parado_label = tk.Label(self.frame_derecha_arriba, text="Tiempo Parado: 0 segundos", font=("Helvetica", 14), bg="light goldenrod", fg="black")
        self.tiempo_parado_label.pack(pady=10)
        
        self.tiempo_movimiento_label = tk.Label(self.frame_derecha_arriba, text="Tiempo en Movimiento: 0 segundos", font=("Helvetica", 14), bg="light goldenrod", fg="black")
        self.tiempo_movimiento_label.pack(pady=10)
        
        self.total_euros_label = tk.Label(self.frame_derecha_arriba, text="Total a Cobrar: 0.00 euros", font=("Helvetica", 16), bg="light goldenrod", fg="black")
        self.total_euros_label.pack(pady=10)

        self.frame_derecha_abajo = tk.Frame(self.frame_derecha, height=200, bg="dodgerblue")
        self.frame_derecha_abajo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.boton_empezar_carrera = customtkinter.CTkButton(self.frame_derecha_abajo, text="Empezar Carrera", command=self.empezar_carrera, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=200, height=50)
        self.boton_empezar_carrera.pack(pady=10)
        
        self.boton_marcha = customtkinter.CTkButton(self.frame_derecha_abajo, text="Marcha", command=self.marcha, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=200, height=50, state=tk.DISABLED)
        self.boton_marcha.pack(pady=10)
        
        self.boton_parada = customtkinter.CTkButton(self.frame_derecha_abajo, text="Parada", command=self.parada, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=200, height=50, state=tk.DISABLED)
        self.boton_parada.pack(pady=10)

        self.canva_fin = customtkinter.CTkButton(self.frame_derecha_abajo, text="Fin de Carrera", command=self.finalizar_carrera, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=200, height=50, state=tk.DISABLED)
        self.canva_fin.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()
    
    def autenticar(self, root):
        dialog = CustomPasswordDialog(root, "Ingrese su contraseña:")
        root.wait_window(dialog)
        password = dialog.result
        if password == self.password_plaintext:
            self.autenticado = True
        else:
            messagebox.showerror("Autenticación Fallida", "Contraseña incorrecta.")
            self.autenticado = False
            
    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.root.destroy()

    def actualizar_tiempo_costo(self):
        if not self.carrera_iniciada:
            return

        ahora = time.time()
        delta_tiempo = ahora - self.tiempo_ultimo_cambio
        self.tiempo_total += delta_tiempo
        self.tiempo_ultimo_cambio = ahora

        if self.en_movimiento:
            self.tiempo_movimiento += delta_tiempo
        else:
            self.tiempo_parado += delta_tiempo

        self.total_euros = (self.tiempo_parado * self.tarifa_parado) + (self.tiempo_movimiento * self.tarifa_movimiento)

        self.tiempo_total_label.configure(text=f"Tiempo Total: {int(self.tiempo_total)} segundos")
        self.tiempo_parado_label.configure(text=f"Tiempo Parado: {int(self.tiempo_parado)} segundos")
        self.tiempo_movimiento_label.configure(text=f"Tiempo en Movimiento: {int(self.tiempo_movimiento)} segundos")
        self.total_euros_label.configure(text=f"Total a Cobrar: {self.total_euros:.2f} euros")

        self.root.after(1000, self.actualizar_tiempo_costo)

    def resetear_valores(self):
        self.tiempo_total = 0
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
        self.total_euros = 0

    def marcha(self):
        if not self.carrera_iniciada:
            return

        self.en_movimiento = True
        self.tiempo_ultimo_cambio = time.time()
        self.estado_label.configure(text="Taxi en movimiento.")
        self.boton_marcha.configure(state=tk.DISABLED)
        self.boton_parada.configure(state=tk.NORMAL)
        self.canva_fin.configure(state=tk.NORMAL)
        logging.info("Taxi en movimiento.")

    def parada(self):
        if not self.carrera_iniciada:
            return

        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.estado_label.configure(text="Taxi en parado.")
        self.boton_marcha.configure(state=tk.NORMAL)
        self.boton_parada.configure(state=tk.DISABLED)
        logging.info("Taxi en parado.")

    def finalizar_carrera(self):
        if not self.carrera_iniciada:
            return

        self.carrera_iniciada = False
        self.en_movimiento = False
        self.actualizar_tiempo_costo()  # Ensure final update
        self.guardar_registro()
        self.estado_label.configure(text="Carrera finalizada.")
        self.boton_empezar_carrera.configure(state=tk.NORMAL)
        self.boton_marcha.configure(state=tk.DISABLED)
        self.boton_parada.configure(state=tk.DISABLED)
        self.canva_fin.configure(state=tk.DISABLED)
        logging.info("Carrera finalizada.")

    def crear_tabla_registros(self):
        self.conexion_bd = sqlite3.connect(db_path)
        cursor = self.conexion_bd.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tiempo_total INTEGER,
            tiempo_parado INTEGER,
            tiempo_movimiento INTEGER,
            total_euros REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conexion_bd.commit()

    def guardar_registro(self):
        if self.conexion_bd:
            cursor = self.conexion_bd.cursor()
            cursor.execute("""
            INSERT INTO registros (tiempo_total, tiempo_parado, tiempo_movimiento, total_euros) 
            VALUES (?, ?, ?, ?)
            """, (self.tiempo_total, self.tiempo_parado, self.tiempo_movimiento, self.total_euros))
            self.conexion_bd.commit()
            logging.info("Registro de carrera guardado en la base de datos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--password", help="Contraseña para el taxímetro", required=True)
    args = parser.parse_args()

    contraseña = args.password
    root = tk.Tk()
    app = Taximetro(contraseña, root)
    app.iniciar_carrera(root)
