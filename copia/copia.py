# En esta versión 8 el programa guarda en una base de datos (sqlite3) los registros de carreras pasadas
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
# Configuramos el módulo "logging" para registrar eventos en un archivo ("taximetro.log") y en la consola. El formato del registro incluye la hora, el nivel de severidad y el mensaje.  

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
        self.contraseña = contraseña
        self.autenticado = False
        self.conexion_bd = None
        self.tiempo_transcurrido = 0
        self.dinero_a_pagar = 0.00
        self.crear_tabla_registros()
        logging.info("Taxímetro iniciado con tarifas por defecto y contraseña establecida.")
        # Inicializa variables de la instancia, incluidas las tarifas, el estado del taxímetro, la autenticación y la conexión a la base de datos. Llama al método "crear_tabla_registros" para configurar la base de datos y registra un mensaje de inicio.

    def iniciar_carrera(self, root):
        self.autenticar(root)
        if not self.autenticado:
            return
        
        self.root = root
        self.root.title("Taxímetro Digital")
        self.root.geometry("600x500")

        self.frame_izquierda = tk.Frame(self.root, width=200,bg="deepskyblue2" )
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

        self.logo_image = tk.PhotoImage(file="logo.png").subsample(3, 3)
        self.logo_label = tk.Label(self.frame_izquierda,image=self.logo_image, bg="#3498db")
        self.logo_label.pack(pady=5)
        
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

        self.canvas_tiempo = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_tiempo.pack(pady=10)

        self.canvas_euros = tk.Canvas(self.frame_derecha, width=300, height=50, bg="grey", highlightthickness=5)
        self.canvas_euros.pack(pady=10)
       
        self.canva_fin = tk.Button(self.frame_derecha, text="Fin", activebackground="red", font=("helvetica", 14, "bold"), command=self.finalizar_carrera, width=18, fg="dodgerblue", bg="grey24")
        self.canva_fin.pack(pady=5)
        
        self.actualizar_tiempo_costo()

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

        # Actualizamos los contadores visuales en el Canvas
        self.actualizar_canvas(self.canvas_tiempo, tiempo_formateado)
        self.actualizar_canvas(self.canvas_euros, f"{self.total_euros:.2f} €")

        self.tiempo_ultimo_cambio = tiempo_actual
        self.root.after(1000, self.actualizar_tiempo_costo)

    def actualizar_canvas(self, canvas, texto):
        canvas.delete("all")  # Borramos todo lo dibujado previamente en el Canvas
        canvas.create_text(150, 30, text=texto, font=("Arial", 38), fill="white")
   
    def autenticar(self, root):
        intentos = 3
        while intentos > 0:
            if not self.autenticado:
                contraseña_ingresada = simpledialog.askstring("Autenticación", "Ingresa la contraseña para continuar:", show='*')
                if contraseña_ingresada == self.contraseña:
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
    # Definimos el método "crear_tabla_registros", que crea una tabla en la base de datos para almacenar los registros de las carreras.

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
    # Definimos el método "insertar_registro", que inserta un registro en la tabla "registros" de la base de datos.

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

        nueva_contraseña = simpledialog.askstring("Cambiar contraseña", "Introduce la nueva contraseña:", show='*')
        confirmacion_contraseña = simpledialog.askstring("Cambiar contraseña", "Confirma la nueva contraseña:", show='*')

        if nueva_contraseña == confirmacion_contraseña:
            self.contraseña = nueva_contraseña
            logging.info("Contraseña cambiada exitosamente.")
            messagebox.showinfo("Éxito", "Contraseña cambiada exitosamente.")
        else:
            logging.warning("La nueva contraseña no coincide con la confirmación.")
            messagebox.showerror("Error", "La nueva contraseña no coincide con la confirmación.")
        
    def _cambiar_estado(self, tiempo_actual, en_movimiento):
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio
        self.tiempo_transcurrido += tiempo_transcurrido
        if self.en_movimiento:
            self.tiempo_movimiento += tiempo_transcurrido
        else:
            self.tiempo_parado += tiempo_transcurrido

        self.en_movimiento = en_movimiento
        self.tiempo_ultimo_cambio = tiempo_actual
        estado = "movimiento" if en_movimiento else "parado"
        self.estado_label.config(text=f"Taxi en {estado}.")
        logging.info(f"Taxi en {estado}.")
    # Define el método "_cambiar_estado", que actualiza el estado del taxi (parado o en movimiento) y el tiempo transcurrido desde el último cambio de estado. 

    def iniciar_movimiento(self):
        self._cambiar_estado(time.time(), True)
    # Define el método "iniciar_movimiento", que actualiza el estado del taxi a "en movimiento" y actualiza el tiempo transcurrido desde el último cambio de estado.

    def detener_movimiento(self):
        self._cambiar_estado(time.time(), False)
    # Define el método "detener_movimiento", que actualiza el estado del taxi a "parado" y actualiza el tiempo transcurrido desde el último cambio de estado.
    

    def finalizar_carrera(self):
        tiempo_actual = time.time()
        self._cambiar_estado(tiempo_actual, self.en_movimiento)
        self.total_euros = (self.tiempo_movimiento * self.tarifa_movimiento) + (self.tiempo_parado * self.tarifa_parado)
        self.dinero_a_pagar = self.total_euros
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
    # Define el método "finalizar_carrera", que calcula el total a cobrar, muestra el total al usuario, inserta el registro en la base de datos, resetea los valores y pregunta al usuario si desea iniciar una nueva carrera.
    
    def actualizar_interfaz(self):
        self.total_label.config(text=f"Total a cobrar: {self.dinero_a_pagar:.2f} euros")
        self.tiempo_label.config(text=f"Tiempo transcurrido: {self.tiempo_transcurrido:.2f} segundos")

        self.root.after(100, self.actualizar_interfaz)
    def preguntar_nueva_carrera(self):
        nueva_carrera = messagebox.askyesno("Nueva carrera", "¿Deseas iniciar una nueva carrera?")
        if not nueva_carrera:
            self.root.destroy()
    # Define el método "preguntar_nueva_carrera", que muestra un mensaje para preguntar al usuario si desea iniciar una nueva carrera. Si el usuario responde "Sí", se inicia una nueva carrera. Si el usuario responde "No", se cierra la aplicación.

    def resetear_valores(self):
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0
    # Define el método "resetear_valores", que resetea los valores de tiempo y total a sus valores iniciales.

    def __del__(self):
        if self.conexion_bd:
            self.conexion_bd.close()
            logging.info("Conexión a la base de datos cerrada correctamente.")
    # Define el método "__del__", que cierra la conexión a la base de datos cuando se destruye la instancia del taxímetro.

def parse_args():
    parser = argparse.ArgumentParser(description='Taxímetro digital - Aplicación GUI')
    parser.add_argument('--contraseña', type=str, default='1234', help='Contraseña para configurar tarifas (por defecto: "1234")')
    return parser.parse_args()
# Define la función "parse_args", que analiza los argumentos de la línea de comandos para obtener la contraseña. 

if __name__ == "__main__":
    args = parse_args()
    taximetro = Taximetro(contraseña=args.contraseña)
    root = tk.Tk()
    taximetro.iniciar_carrera(root)
    root.mainloop()
# El bloque principal del programa se ejecuta si el script se ejecuta directamente. Analiza los argumentos de la línea de comandos, crea una instancia del "Taxímetro" con la contraseña proporcionada, inicia la interfaz gráfica y entra en el bucle principal de "tkinter".