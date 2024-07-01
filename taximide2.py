# sin comentarios
import hashlib 
import re   
import os 
import json
import time 
import logging 
import argparse 
import tkinter as tk 
import customtkinter 
from tkinter import messagebox, simpledialog 
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))

records_dir = os.path.join(current_dir, "records")
if not os.path.exists(records_dir):
    os.makedirs(records_dir)

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
        self.db_path = db_path
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
        self.root = root
        self.estado_label = tk.Label(root, text="Taxi en movimiento")
        self.boton_marcha = tk.Button(root, text="Iniciar Marcha", command=self.iniciar_movimiento)
        self.boton_parada = tk.Button(root, text="Detener Marcha", command=self.detener_movimiento)
        self.load_password(contraseña)
        self.crear_tabla_registros()
        logging.info("Taxímetro iniciado con tarifas por defecto y contraseña establecida.")

    def show_custom_error(self, message):
        CustomNotificationDialog(self.root, message, "Error", "tomato")

    def show_custom_warning(self, message):
        CustomNotificationDialog(self.root, message, "Warning", "dark goldenrod")

    def show_custom_info(self, message):
        CustomNotificationDialog(self.root, message, "Info", "cyan")
        
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
            self.en_movimiento = False  
            self.estado_label.configure(text="Taxi en parado.")
            self.boton_empezar_carrera.configure(state=tk.DISABLED)
            self.boton_marcha.configure(state=tk.NORMAL)
            self.boton_parada.configure(state=tk.DISABLED)
            self.canva_fin.configure(state=tk.NORMAL)
            logging.info("Carrera iniciada. Taxi en parado.")
            self.actualizar_tiempo_costo()

    def iniciar_carrera(self, root):
        self.root = root
        self.root.withdraw() 
        self.autenticar(root)
        if not self.autenticado:
            root.quit()
            return
        self.root.deiconify()
        self.root.title("TaxiMide")
        self.root.geometry("600x500")
        script_dir = os.path.dirname(__file__) 
        logo_path = os.path.join(script_dir, "logo.png")
        self.frame_izquierda = tk.Frame(self.root, width=200,bg="dodgerblue" )
        self.frame_izquierda.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_derecha = tk.Frame(self.root, bg="grey24")
        self.frame_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_derecha_arriba = tk.Frame(self.frame_derecha, height=400, bg="light goldenrod")
        self.frame_derecha_arriba.pack(side=tk.TOP, fill=tk.BOTH)
        self.estado_label = tk.Label(self.frame_derecha_arriba, text="Taxi en parado.", font=("Helvetica", 20), fg="dodgerblue", bg="light goldenrod")
        self.estado_label.pack(pady=10)
        self.tarifa_parado_label = tk.Label(self.frame_derecha, text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/segundos", font=("Helvetica", 16), fg="deepskyblue", bg="grey24")
        self.tarifa_parado_label.pack(pady=10)
        self.tarifa_movimiento_label = tk.Label(self.frame_derecha, text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/segundos", font=("Helvetica", 16), fg="deepskyblue", bg="grey24")
        self.tarifa_movimiento_label.pack(pady=10)
        self.total_label = tk.Label(self.frame_derecha, text="Total a cobrar: 0.00 euros", font=("Helvetica", 18), fg="deepskyblue", bg="grey24")
        self.canvas_tiempo = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_tiempo.pack(pady=10)
        self.canvas_euros = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_euros.pack(pady=10)
        self.canva_fin = customtkinter.CTkButton(self.frame_derecha, text="Fin", font=("helvetica", 24, "bold"), command=self.finalizar_carrera, width=150, height=50, hover_color="tomato", text_color="blue4", fg_color="grey60", state=tk.DISABLED)
        self.canva_fin.pack(pady=5)
        self.logo_image = tk.PhotoImage(file=logo_path).subsample(3, 3) #.subsample(3, 3) reduce el tamaño de la imagen a 1/3 en ambas dimensiones.
        self.logo_label = tk.Label(self.frame_izquierda,image=self.logo_image, bg="#3498db")
        self.logo_label.pack(pady=5)
        self.boton_empezar_carrera = customtkinter.CTkButton(self.frame_izquierda, text="Start", hover_color="pale green", text_color="black", font=("Helvetica", 18, "bold"), command=self.empezar_carrera, width=150, height=30, fg_color="light goldenrod")
        self.boton_empezar_carrera.pack(pady=5)
        self.boton_marcha = customtkinter.CTkButton(self.frame_izquierda, text="Marcha", hover_color="pale green", text_color="black", font=("Helvetica", 20, "bold"), command=self.iniciar_movimiento, width=150, height=30, fg_color="light goldenrod", state=tk.DISABLED)
        self.boton_marcha.pack(pady=5)
        self.boton_parada = customtkinter.CTkButton(self.frame_izquierda, text="Parada", font=("Helvetica", 20, "bold"), command=self.detener_movimiento, width=150, height=30, hover_color="tomato", text_color="black", fg_color="light goldenrod", state=tk.DISABLED)
        self.boton_parada.pack(pady=5)
        self.boton_configurar = customtkinter.CTkButton(self.frame_izquierda, text="Tarifas", font=("Helvetica", 20, "bold"), command=self.configurar_tarifas, width=150, height=30, hover_color="cyan", text_color="black", fg_color="light goldenrod")
        self.boton_configurar.pack(pady=5)
        self.boton_cambiar_contraseña = customtkinter.CTkButton(self.frame_izquierda, text="Contraseña", font=("Helvetica", 20, "bold"), command=self.cambiar_contraseña, width=150, height=30, hover_color="cyan", text_color="black", fg_color="light goldenrod")
        self.boton_cambiar_contraseña.pack(pady=5)
        self.boton_quit = customtkinter.CTkButton(self.frame_izquierda, text="Exit", font=("Helvetica", 20, "bold"), command=self.root.destroy, width=150, height=30, hover_color="cyan", text_color="black", fg_color="light goldenrod")
        self.boton_quit.pack(pady=5)
        self.carrera_iniciada = False
        self.actualizar_canvas(self.canvas_tiempo, "00:00:00")
        self.actualizar_canvas(self.canvas_euros, "0.00 €")
        self.root.deiconify()

    def actualizar_tiempo_costo(self):
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio
        if self.en_movimiento:
            self.tiempo_movimiento += tiempo_transcurrido
        else:
            self.tiempo_parado += tiempo_transcurrido
        self.tiempo_total = self.tiempo_movimiento + self.tiempo_parado
        self.total_euros = (self.tiempo_movimiento * self.tarifa_movimiento) + (self.tiempo_parado * self.tarifa_parado)
        horas, resto = divmod(self.tiempo_total, 3600)
        minutos, segundos = divmod(resto, 60)
        tiempo_formateado = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}"
        self.actualizar_canvas(self.canvas_tiempo, tiempo_formateado)
        self.actualizar_canvas(self.canvas_euros, f"{self.total_euros:.2f} €")
        self.tiempo_ultimo_cambio = tiempo_actual
        self.root.after(1000, self.actualizar_tiempo_costo)

    def actualizar_canvas(self, canvas, texto):
        canvas.delete("all") 
        canvas.create_text(150, 30, text=texto, font=("Arial", 38), fill="white")

    def autenticar(self, root):
        try:
            intentos = 3
            while intentos > 0:
                if not self.autenticado:
                    root.deiconify()  
                    dialog = CustomPasswordDialog(root, "Ingresa la contraseña para continuar:")
                    root.withdraw()
                    root.wait_window(dialog)
                    if dialog.result is not None:
                        if self.verify_password(dialog.result):
                            self.autenticado = True
                            logging.info("Contraseña correcta. Acceso concedido.")
                            break
                        else:
                            intentos -= 1
                            if intentos > 0:
                                self.show_custom_error(f"Contraseña incorrecta. Te quedan {intentos} intentos.")
                            logging.warning("Intento de acceso con contraseña incorrecta.")
                    else:
                        return
                else:
                    break
            if intentos == 0:
                logging.error("Número máximo de intentos alcanzado. Cierre del programa.")
                root.deiconify()
                self.show_custom_error("Número máximo de intentos alcanzado. Cierre del programa.")
                root.quit()
        except Exception as e:
            logging.error(f"Error en autenticar: {str(e)}")
            self.show_custom_error(f"Error de autenticación: {str(e)}")
            return False
        if self.autenticado:
            root.deiconify() 

    def verify_password(self, entered_password):
        if self.password_plaintext == "1234" and entered_password == "1234":
            logging.warning("Contraseña por defecto. Por favor cambiala")
            self.show_custom_warning("Estás usando contraseña por defecto. Por favor cambiala por razones de la seguridad.")
        return (entered_password == self.password_plaintext or 
                self.hash_password(entered_password) == self.password_hash)
        
    def cambiar_contraseña(self):
        try:
            if not self.autenticado:
                logging.warning("No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
                self.show_custom_error("No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
                return
            dialog_new = CustomPasswordDialog(self.root, "Introduce la nueva contraseña:", "Nueva Contraseña")
            self.root.wait_window(dialog_new)
            if dialog_new.result is None:
                logging.warning("Cambio de contraseña cancelado.")
                return
            new_password = dialog_new.result
            if not self.validate_password(new_password):
                self.show_custom_warning("La nueva contraseña no cumple los requisitos.  \nDebe tener al menos 6 caracteres y solo puede contener letras, números y los caracteres . - _")
                return
            dialog_confirm = CustomPasswordDialog(self.root, "Confirma la nueva contraseña:", "Confirmar Contraseña")
            self.root.wait_window(dialog_confirm)
            if dialog_confirm.result is None:
                logging.warning("Cambio de contraseña cancelado.")
                return
            if new_password == dialog_confirm.result:
                self.password_hash = self.hash_password(new_password)
                self.password_plaintext = new_password
                self.save_password()
                logging.info("Contraseña cambiada exitosamente.")
                self.show_custom_info("Contraseña cambiada exitosamente.")
                self.autenticado = False
                self.autenticar(self.root)
            else:
                self.show_custom_error("Las contraseñas no coinciden.")
                logging.warning("Las contraseñas no coinciden en el cambio de contraseña.")
        except Exception as e:
            logging.error(f"Error en cambiar_contraseña: {str(e)}")
            self.show_custom_error(f"Error al cambiar la contraseña: {str(e)}")

    def validate_password(self, contraseña):
        if len(contraseña) < 6:
            return False
        if not re.match("^[a-zA-Z0-9._-]+$", contraseña):
            return False
        return True
    def crear_tabla_registros(self): 
        try: 
            self.conexion_bd = sqlite3.connect(db_path) 
            cursor = self.conexion_bd.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tiempo_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tiempo_fin TIMESTAMP,
                    tiempo_parado REAL,
                    tiempo_movimiento REAL,
                    total_euros REAL
                )
            ''') 
            self.conexion_bd.commit() 
            logging.info("Tabla 'registros' creada correctamente.")
        except sqlite3.Error as e:
            logging.error(f"Error al crear la tabla 'registros': {e}")
    
    def insertar_registro(self, tiempo_inicio, tiempo_fin, tiempo_parado, tiempo_movimiento, total_euros):
        try:
            cursor = self.conexion_bd.cursor()
            cursor.execute('''
                INSERT INTO registros (tiempo_inicio, tiempo_fin, tiempo_parado, tiempo_movimiento, total_euros)
                VALUES (?, ?, ?, ?, ?)
            ''', (tiempo_inicio, tiempo_fin, tiempo_parado, tiempo_movimiento, total_euros))
            self.conexion_bd.commit()
            self.conexion_bd.commit()
            logging.info("Registro insertado correctamente en la tabla 'registros'.")
        except sqlite3.Error as e:
            logging.error(f"Error al insertar registro en la tabla 'registros': {e}")

    def configurar_tarifas(self):
        if not self.autenticado:
            logging.warning("No se ha autenticado. Debes autenticarte para configurar las tarifas.")
            messagebox.showerror("Error", "No se ha autenticado. Debes autenticarte para configurar las tarifas.")
            return
        try:
            nueva_tarifa_parado = float(simpledialog.askstring("Configurar tarifas", "Introduce la nueva tarifa en parado (€/segundo):"))
            nueva_tarifa_movimiento = float(simpledialog.askstring("Configurar tarifas", "Introduce la nueva tarifa en movimiento (€/segundo):"))
            self.tarifa_parado = nueva_tarifa_parado
            self.tarifa_movimiento = nueva_tarifa_movimiento
            logging.info("Tarifas actualizadas en parado: %.2f, y en movimiento: %.2f", self.tarifa_parado, self.tarifa_movimiento)
            self.tarifa_parado_label.configure(text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/segundo")
            self.tarifa_movimiento_label.configure(text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/segundo")
            messagebox.showinfo("Éxito", "Tarifas actualizadas.")
        except ValueError:
            logging.error("Error al introducir tarifas. Valores no numéricos.")
            messagebox.showerror("Error", "Introduce valores numéricos válidos.")
            
    def _cambiar_estado(self, tiempo_actual, en_movimiento):
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio
        if self.en_movimiento:
            self.tiempo_movimiento += tiempo_transcurrido
        else:
            self.tiempo_parado += tiempo_transcurrido
        self.en_movimiento = en_movimiento
        self.tiempo_ultimo_cambio = tiempo_actual
        estado = "movimiento" if en_movimiento else "parado"
        self.estado_label.configure(text=f"Taxi en {estado}.")
        if en_movimiento:
            self.boton_marcha.configure(state=tk.DISABLED)
            self.boton_parada.configure(state=tk.NORMAL)
        else:
            self.boton_marcha.configure(state=tk.NORMAL)
            self.boton_parada.configure(state=tk.DISABLED)
        logging.info(f"Taxi en {estado}.")

    def iniciar_movimiento(self):
        self._cambiar_estado(time.time(), True)

    def detener_movimiento(self):
        self._cambiar_estado(time.time(), False)

    def finalizar_carrera(self):
        tiempo_actual = time.time()
        self._cambiar_estado(tiempo_actual, self.en_movimiento)
        self.total_euros = (self.tiempo_movimiento * self.tarifa_movimiento) + (self.tiempo_parado * self.tarifa_parado) 
        self.total_label.config(text=f"Total a cobrar: {self.total_euros:.2f} euros")
        messagebox.showinfo("Carrera finalizada", f"Total a cobrar: {self.total_euros:.2f} euros")
        self.insertar_registro(
            tiempo_inicio=self.tiempo_ultimo_cambio - (self.tiempo_parado + self.tiempo_movimiento),
            tiempo_fin=self.tiempo_ultimo_cambio,
            tiempo_parado=self.tiempo_parado,
            tiempo_movimiento=self.tiempo_movimiento,
            total_euros=self.total_euros
        )
        self.resetear_valores()
        self.preguntar_nueva_carrera()

    def preguntar_nueva_carrera(self):
        nueva_carrera = messagebox.askyesno("Nueva carrera", "¿Deseas iniciar una nueva carrera?")
        if nueva_carrera:
            self.en_movimiento = False 
            self.empezar_carrera()
        else:
            self.root.destroy() 
    
    def resetear_valores(self):
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
        self.carrera_iniciada = False
        self.actualizar_canvas(self.canvas_tiempo, "00:00:00")
        self.actualizar_canvas(self.canvas_euros, "0.00 €")
   
    def __del__(self):
        try:
            if self.conexion_bd:
                self.conexion_bd.close()
                logging.info("Conexión a la base de datos cerrada correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión a la base de datos: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description='TaxiMide - Aplicación GUI')
    parser.add_argument('--password', type=str, default='1234', help='Contraseña para configurar tarifas (por defecto: "1234")')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    root = tk.Tk()
    root.withdraw()
    taximetro = Taximetro(args.password, root)
    taximetro.iniciar_carrera(root)
    root.mainloop()