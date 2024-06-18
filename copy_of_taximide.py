import hashlib
import time
import logging
import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("taximetro.log"), 
    logging.StreamHandler()  
])

class Taximetro:
    def __init__(self, contraseña):
        self.tarifa_parado = 0.02
        self.tarifa_movimiento = 0.05
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
        self.password_hash = self.hash_password(contraseña)
        self.password_plaintext = contraseña
        self.autenticado = False
        self.conexion_bd = None
        self.crear_tabla_registros()
        logging.info("Taxímetro iniciado con tarifas por defecto y contraseña establecida.")
        
    def hash_password(self, password):
        password_bytes = password.encode('utf-8')
        
        hasher = hashlib.sha256()
        
        hasher.update(password_bytes)
        
        password_hash = hasher.hexdigest()
        
        return password_hash

    def iniciar_carrera(self, root):
        self.autenticar(root)
        if not self.autenticado:
            return
        
        self.root = root
        self.root.title("Taxímetro Digital")
        self.root.geometry("400x300")
        self.root.configure(bg="black")

        self.estado_label = tk.Label(root, text="Taxi en parado.", font=("Helvetica", 20), fg="white", bg="black")
        self.estado_label.pack(pady=10)

        self.tarifa_parado_label = tk.Label(root, text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/minuto", font=("Helvetica", 16), fg="white", bg="black")
        self.tarifa_parado_label.pack()

        self.tarifa_movimiento_label = tk.Label(root, text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/minuto", font=("Helvetica", 16), fg="white", bg="black")
        self.tarifa_movimiento_label.pack()

        self.total_label = tk.Label(root, text="Total a cobrar: 0.00 euros", font=("Helvetica", 18), fg="white", bg="black")
        self.total_label.pack(pady=10)

        button_frame = tk.Frame(root, bg="red")
        button_frame.pack(pady=10)

        self.boton_marcha = tk.Button(button_frame, text="Marcha", font=("Helvetica", 14, "bold"), command=self.iniciar_movimiento, width=12, bg="white", fg="black")
        self.boton_marcha.grid(row=0, column=0, padx=5, pady=5)

        self.boton_parada = tk.Button(button_frame, text="Parada", font=("Helvetica", 14, "bold"), command=self.detener_movimiento, width=12, bg="white", fg="black")
        self.boton_parada.grid(row=0, column=1, padx=5)

        self.boton_fin = tk.Button(button_frame, text="Fin", font=("Helvetica", 14, "bold"), command=self.finalizar_carrera, width=12, bg="white", fg="black")
        self.boton_fin.grid(row=1, column=0, padx=5, pady=5)

        self.boton_configurar = tk.Button(button_frame, text="Configurar tarifas", font=("Helvetica", 14, "bold"), command=self.configurar_tarifas, width=18, bg="white", fg="black")
        self.boton_configurar.grid(row=1, column=1, padx=5, pady=5)

        self.boton_cambiar_contraseña = tk.Button(button_frame, text="Cambiar contraseña", font=("Helvetica", 14, "bold"), command=self.cambiar_contraseña, width=18, bg="white", fg="black")
        self.boton_cambiar_contraseña.grid(row=2, column=0, columnspan=2, pady=5)

    def autenticar(self, root):
        intentos = 3
        while intentos > 0:
            if not self.autenticado:
                entered_password = simpledialog.askstring("Autenticación", "Ingresa la contraseña para continuar:", show='*')
                if self.verificar_password(entered_password):
                    self.autenticado = True
                    logging.info("Contraseña correcta. Acceso concedido.")
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta. Inténtalo de nuevo.")
                    logging.warning("Intento de acceso con contraseña incorrecta.")
                    intentos -= 1
            else:
                break

        if intentos == 0:
            logging.error("Número máximo de intentos alcanzado. Cierre del programa.")
            messagebox.showerror("Error", "Número máximo de intentos alcanzado. Cierre del programa.")
            root.destroy()
    
    def verificar_password(self, entered_password):
        return entered_password == self.password_plaintext or self.hash_password(entered_password) == self.password_hash

    def crear_tabla_registros(self):
        try:
            self.conexion_bd = sqlite3.connect("registros.db")
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
            logging.info("Registro insertado correctamente en la tabla 'registros'.")
        except sqlite3.Error as e:
            logging.error(f"Error al insertar registro en la tabla 'registros': {e}")


    def configurar_tarifas(self):
        if not self.autenticado:
            logging.warning("No se ha autenticado. Debes autenticarte para configurar las tarifas.")
            messagebox.showerror("Error", "No se ha autenticado. Debes autenticarte para configurar las tarifas.")
            return

        try:
            nueva_tarifa_parado = float(simpledialog.askstring("Configurar tarifas", "Introduce la nueva tarifa en parado (€/minuto):"))
            nueva_tarifa_movimiento = float(simpledialog.askstring("Configurar tarifas", "Introduce la nueva tarifa en movimiento (€/minuto):"))
            self.tarifa_parado = nueva_tarifa_parado
            self.tarifa_movimiento = nueva_tarifa_movimiento
            logging.info("Tarifas actualizadas en parado: %.2f, y en movimiento: %.2f", self.tarifa_parado, self.tarifa_movimiento)
            self.tarifa_parado_label.config(text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/minuto")
            self.tarifa_movimiento_label.config(text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/minuto")
            messagebox.showinfo("Éxito", "Tarifas actualizadas.")
        except ValueError:
            logging.error("Error al introducir tarifas. Valores no numéricos.")
            messagebox.showerror("Error", "Introduce valores numéricos válidos.")

    def cambiar_contraseña(self):
        if not self.autenticado:
            logging.warning("No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
            messagebox.showerror("Error", "No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
            return

        new_password = simpledialog.askstring("Cambiar contraseña", "Introduce la nueva contraseña:", show='*')
        confirm_password = simpledialog.askstring("Cambiar contraseña", "Confirma la nueva contraseña:", show='*')

        if new_password == confirm_password:
            self.password_hash = self.hash_password(new_password)
            logging.info("Contraseña cambiada exitosamente.")
            messagebox.showinfo("Éxito", "Contraseña cambiada exitosamente.")
        else:
            logging.warning("La nueva contraseña no coincide con la confirmación.")
            messagebox.showerror("Error", "La nueva contraseña no coincide con la confirmación.")
        
    def _cambiar_estado(self, tiempo_actual, en_movimiento):
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio
        if self.en_movimiento:
            self.tiempo_movimiento += tiempo_transcurrido
        else:
            self.tiempo_parado += tiempo_transcurrido

        self.en_movimiento = en_movimiento
        self.tiempo_ultimo_cambio = tiempo_actual
        estado = "movimiento" if en_movimiento else "parado"
        self.estado_label.config(text=f"Taxi en {estado}.")
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
        if not nueva_carrera:
            self.root.destroy()
    
    def resetear_valores(self):
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
    
    def __del__(self):
        if self.conexion_bd:
            self.conexion_bd.close()
            logging.info("Conexión a la base de datos cerrada correctamente.")
    
def parse_args():
    parser = argparse.ArgumentParser(description='Taxímetro digital - Aplicación GUI')
    parser.add_argument('--password', type=str, default='1234', help='Contraseña para configurar tarifas (por defecto: "1234")')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    taximetro = Taximetro(args.password)
    root = tk.Tk()
    taximetro.iniciar_carrera(root)
    root.mainloop()