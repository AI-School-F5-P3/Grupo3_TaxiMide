import hashlib
import re
import time
import logging
import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("taximideapp.log"),
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
        self.root.title("TaxiMide")
        self.root.geometry("600x500")
        
        self.frame_izquierda = tk.Frame(self.root, width=200, bg="deepskyblue2")
        self.frame_izquierda.pack(side=tk.LEFT, fill=tk.Y)
        
        self.frame_derecha = tk.Frame(self.root, bg="grey24")
        self.frame_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.frame_derecha_arriba = tk.Frame(self.frame_derecha, height=400, bg="light goldenrod")
        self.frame_derecha_arriba.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.estado_label = tk.Label(self.frame_derecha_arriba, text="Taxi en parado.", font=("Helvetica", 20), fg="dodgerblue", bg="light goldenrod")
        self.estado_label.pack(pady=10)

        self.tarifa_parado_label = tk.Label(self.frame_derecha, text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/minuto", font=("Helvetica", 16), fg="dodgerblue", bg="grey24")
        self.tarifa_parado_label.pack(pady=10)

        self.tarifa_movimiento_label = tk.Label(self.frame_derecha, text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/minuto", font=("Helvetica", 16), fg="dodgerblue", bg="grey24")
        self.tarifa_movimiento_label.pack(pady=10)
        
        self.total_label = tk.Label(self.frame_derecha, text="Total a cobrar: 0.00 euros", font=("Helvetica", 18), fg="dodgerblue", bg="grey24")
        self.total_label.pack(pady=10)

        self.canvas_tiempo = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_tiempo.pack(pady=10)

        self.canvas_euros = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_euros.pack(pady=10)
        
        self.canva_fin = tk.Button(self.frame_derecha, text="Fin", activebackground="red", font=("helvetica", 14, "bold"), command=self.finalizar_carrera, width=18, fg="dodgerblue", bg="grey24")
        self.canva_fin.pack(pady=5)
        
        self.cargar_logo()  # Llama al método para cargar el logo

        self.boton_marcha = tk.Button(self.frame_izquierda, text="Marcha", activebackground="blue", font=("Helvetica", 14, "bold"), command=self.iniciar_movimiento, width=18, bg="light goldenrod", fg="black")
        self.boton_marcha.pack(pady=5)
     
        self.boton_parada = tk.Button(self.frame_izquierda, text="Parada", activebackground="blue", font=("Helvetica", 14, "bold"), command=self.detener_movimiento, width=18, bg="light goldenrod", fg="black")
        self.boton_parada.pack(pady=5)

        self.boton_configurar = tk.Button(self.frame_izquierda, text="Configurar tarifas", activebackground="blue", font=("Helvetica", 14, "bold"), command=self.configurar_tarifas, width=18, bg="light goldenrod", fg="black")
        self.boton_configurar.pack(pady=5)

        self.boton_cambiar_contraseña = tk.Button(self.frame_izquierda, text="Cambiar contraseña", activebackground="blue", font=("Helvetica", 14, "bold"), command=self.cambiar_contraseña, width=18, bg="light goldenrod", fg="black")
        self.boton_cambiar_contraseña.pack(pady=5)
        
        self.boton_quit = tk.Button(self.frame_izquierda, text="Exit", activebackground="blue", font=("helvetica", 14, "bold"), command=root.quit, width=18, bg="light goldenrod", fg="black")
        self.boton_quit.pack(pady=5)
    
        self.actualizar_tiempo_costo()

    def cargar_logo(self):
        try:
            logo_path = "logo.png"  # Ruta al archivo del logo, ajusta según tu estructura de directorios
            if os.path.exists(logo_path):
                self.logo_image = tk.PhotoImage(file=logo_path).subsample(3, 3)
                self.logo_label = tk.Label(self.frame_izquierda, image=self.logo_image, bg="#3498db")
                self.logo_label.pack(pady=5)
            else:
                logging.warning(f"No se encontró el archivo '{logo_path}'. Se usará un label alternativo.")
                self.logo_image = None
        except Exception as e:
            logging.error(f"Error al cargar el logo: {e}")
            self.logo_image = None

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

    def iniciar_movimiento(self):
        if not self.en_movimiento:
            self.en_movimiento = True
            logging.info("Taxi en movimiento.")
            self.estado_label.config(text="Taxi en movimiento.", fg="green")
            self.tiempo_ultimo_cambio = time.time()

    def detener_movimiento(self):
        if self.en_movimiento:
            self.en_movimiento = False
            logging.info("Taxi en parado.")
            self.estado_label.config(text="Taxi en parado.", fg="dodgerblue")
            self.tiempo_ultimo_cambio = time.time()

    def configurar_tarifas(self):
        nueva_tarifa_parado = simpledialog.askfloat("Configurar Tarifas", "Introduce la nueva tarifa en parado (€/minuto):", initialvalue=self.tarifa_parado)
        nueva_tarifa_movimiento = simpledialog.askfloat("Configurar Tarifas", "Introduce la nueva tarifa en movimiento (€/minuto):", initialvalue=self.tarifa_movimiento)
        
        if nueva_tarifa_parado is not None and nueva_tarifa_movimiento is not None:
            self.tarifa_parado = nueva_tarifa_parado
            self.tarifa_movimiento = nueva_tarifa_movimiento
            logging.info("Tarifas actualizadas correctamente.")
            self.tarifa_parado_label.config(text=f"Tarifa en parado: {self.tarifa_parado:.2f} €/minuto")
            self.tarifa_movimiento_label.config(text=f"Tarifa en movimiento: {self.tarifa_movimiento:.2f} €/minuto")
        else:
            logging.warning("Configuración de tarifas cancelada.")

    def cambiar_contraseña(self):
        nueva_contraseña = simpledialog.askstring("Cambiar Contraseña", "Ingresa la nueva contraseña:", show='*')
        if nueva_contraseña:
            self.password_plaintext = nueva_contraseña
            self.password_hash = self.hash_password(nueva_contraseña)
            logging.info("Contraseña cambiada correctamente.")
        else:
            logging.warning("Cambio de contraseña cancelado.")

    def finalizar_carrera(self):
        messagebox.showinfo("Carrera Finalizada", f"Se han cobrado {self.total_euros:.2f} euros por {self.tiempo_total:.2f} segundos de servicio.")
        logging.info(f"Carrera finalizada. Total cobrado: {self.total_euros:.2f} euros.")
        self.resetear_valores()
        self.root.destroy()

    def resetear_valores(self):
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
        self.actualizar_canvas(self.canvas_tiempo, "00:00:00")
        self.actualizar_canvas(self.canvas_euros, "0.00 €")

    def crear_tabla_registros(self):
        try:
            self.conexion_bd = sqlite3.connect("registros.db")
            cursor = self.conexion_bd.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS registros (id INTEGER PRIMARY KEY, fecha TEXT, tiempo_total FLOAT, total_euros FLOAT)")
            self.conexion_bd.commit()
            logging.info("Tabla 'registros' creada correctamente.")
        except Exception as e:
            logging.error(f"Error al crear la tabla 'registros': {e}")
        finally:
            if self.conexion_bd:
                self.conexion_bd.close()

if __name__ == "__main__":
    root = tk.Tk()
    contraseña = "1234"  # Reemplaza con tu contraseña real
    taximetro = Taximetro(contraseña)
    taximetro.iniciar_carrera(root)
    root.mainloop()
