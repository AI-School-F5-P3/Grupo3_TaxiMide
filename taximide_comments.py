import hashlib  # Importamos la biblioteca hashlib para el hashing de contraseñas
import re       # Importamos la biblioteca re para trabajar con expresiones regulares
import time     # Importamos la biblioteca time para trabajar con funciones relacionadas al tiempo
import logging  # Importamos la biblioteca logging para la gestión de registros
import argparse # Importamos la biblioteca argparse para procesar argumentos de línea de comandos
import tkinter as tk  # Importamos la biblioteca tkinter para la interfaz gráfica de usuario
import customtkinter  # Importamos un módulo personalizado customtkinter para botones personalizados
from tkinter import messagebox, simpledialog  # Importamos funciones específicas de tkinter para diálogos
import sqlite3  # Importamos la biblioteca sqlite3 para trabajar con bases de datos SQLite

# Configuración básica del sistema de logging para guardar registros en un archivo y mostrarlos por consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("taximideapp.log"),  # Manejador para guardar registros en un archivo llamado "taximideapp.log"
    logging.StreamHandler()  # Manejador para mostrar registros por consola
])

# Definición de una ventana personalizada para ingresar contraseña
class CustomPasswordDialog(tk.Toplevel):
    def __init__(self, parent, message, title="Autenticación"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        
        # Configuración del marco principal de la ventana
        self.body_frame = tk.Frame(self, bg="dodgerblue")
        self.body_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiqueta para mostrar el mensaje de autenticación
        self.label = tk.Label(self.body_frame, text=message, font=("Helvetica", 16), bg="dodgerblue", fg="black")
        self.label.pack(pady=(0, 10))

        # Campo de entrada para la contraseña
        self.entry = tk.Entry(self.body_frame, show="*", font=("Helvetica", 12), bg="lightgrey", fg="black")
        self.entry.pack(pady=(10, 10))
        self.entry.focus_set()

        # Botón OK para confirmar la contraseña
        self.ok_button = customtkinter.CTkButton(self.body_frame, text="OK", command=self.ok, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.ok_button.pack(side=tk.LEFT, padx=50)

        # Botón Cancelar para cerrar la ventana
        self.cancel_button = customtkinter.CTkButton(self.body_frame, text="Cancel", command=self.cancel, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.cancel_button.pack(side=tk.RIGHT, padx=50)
        
        # Configuración del cierre de la ventana
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.grab_set()  # Para capturar todos los eventos hasta que esta ventana se cierre
        self.geometry("500x200")  # Tamaño de la ventana
        self.attributes('-topmost', True)  # Ventana en el nivel superior
        self.result = None  # Variable para almacenar el resultado de la ventana

        # Atajos de teclado
        self.bind("<Return>", lambda event: self.ok())  # Atajo Enter para el botón OK
        self.bind("<Escape>", lambda event: self.cancel())  # Atajo Escape para el botón Cancel
        
    def ok(self):
        self.result = self.entry.get()  # Obtener el valor del campo de entrada
        self.destroy()  # Cerrar la ventana
    
    def cancel(self):
        self.result = None  # Establecer el resultado como None
        self.parent.destroy()  # Cerrar la ventana principal

# Definición de una ventana personalizada para mostrar notificaciones
class CustomNotificationDialog(tk.Toplevel):
    def __init__(self, parent, message, title, color):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        
        # Configuración del marco principal de la ventana
        self.body_frame = tk.Frame(self, bg=color)
        self.body_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiqueta para mostrar el mensaje de notificación
        self.label = tk.Label(self.body_frame, text=message, font=("Helvetica", 14), bg=color, fg="black", wraplength=300)
        self.label.pack(pady=(5, 20))

        # Botón OK para cerrar la ventana
        self.ok_button = customtkinter.CTkButton(self.body_frame, text="OK", command=self.destroy, font=("Helvetica", 20), hover_color="pale green", text_color="black",  fg_color="light goldenrod", width=100, height=30)
        self.ok_button.pack(pady=5)
        
        # Configuración del cierre de la ventana
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()  # Para capturar todos los eventos hasta que esta ventana se cierre
        self.geometry("500x250")  # Tamaño de la ventana
        self.attributes('-topmost', True)  # Ventana en el nivel superior

        # Atajo de teclado para el botón OK
        self.bind("<Return>", lambda event: self.destroy())


# Clase principal que representa el taxímetro
class Taximetro:
    def __init__(self, contraseña):
        # Inicialización de variables
        self.db_path = 'taximetro.db'  # Ruta de la base de datos SQLite
        self.tarifa_parado = 0.02  # Tarifa por minuto cuando el taxi está parado
        self.tarifa_movimiento = 0.05  # Tarifa por minuto cuando el taxi está en movimiento
        self.tiempo_total = 0  # Tiempo total de la carrera
        self.total_euros = 0  # Total de euros a cobrar
        self.carrera_iniciada = False  # Estado de la carrera (iniciada o no)
        self.en_movimiento = False  # Estado del taxi (en movimiento o parado)
        self.tiempo_ultimo_cambio = time.time()  # Tiempo del último cambio de estado
        self.tiempo_parado = 0  # Tiempo total en estado parado
        self.tiempo_movimiento = 0  # Tiempo total en estado de movimiento
        self.password_hash = self.hash_password(contraseña)  # Hash de la contraseña proporcionada
        self.password_plaintext = contraseña  # Contraseña en texto plano
        self.autenticado = False  # Estado de autenticación
        self.conexion_bd = None  # Conexión a la base de datos SQLite
        self.crear_tabla_registros()  # Método para crear la tabla de registros en la base de datos
        logging.info("Taxímetro iniciado con tarifas por defecto y contraseña establecida.")  # Registro de inicio

    # Método para mostrar un diálogo de error personalizado
    def show_custom_error(self, message):
        CustomNotificationDialog(self.root, message, "Error", "tomato")

    # Método para mostrar un diálogo de advertencia personalizado
    def show_custom_warning(self, message):
        CustomNotificationDialog(self.root, message, "Warning", "dark goldenrod")

    # Método para mostrar un diálogo de información personalizado
    def show_custom_info(self, message):
        CustomNotificationDialog(self.root, message, "Info", "cyan")

    # Método para realizar el hashing de una contraseña
    def hash_password(self, password):
        password_bytes = password.encode('utf-8')  # Codificación de la contraseña en bytes
        hasher = hashlib.sha256()  # Creación de un objeto sha256
        hasher.update(password_bytes)  # Actualización del hasher con la contraseña codificada
        password_hash = hasher.hexdigest()  # Obtención del hash en formato hexadecimal
        return password_hash  # Retorno del hash calculado

    # Método para iniciar una carrera
    def empezar_carrera(self):
        if not self.carrera_iniciada:  # Si la carrera no está iniciada
            self.carrera_iniciada = True  # Se marca como iniciada
            self.resetear_valores()  # Se reinician los valores del taxímetro
            self.tiempo_ultimo_cambio = time.time()  # Se actualiza el tiempo del último cambio
            self.en_movimiento = False  # Se asegura que inicie en estado "parado"
            self.estado_label.configure(text="Taxi en parado.")  # Actualización de la etiqueta de estado
            self.boton_empezar_carrera.configure(state=tk.DISABLED)  # Se deshabilita el botón de "Empezar Carrera"
            self.boton_marcha.configure(state=tk.NORMAL)  # Se habilita el botón de "Marcha"
            self.boton_parada.configure(state=tk.NORMAL)  # Se habilita el botón de "Parada"
            self.boton_fin_carrera.configure(state=tk.NORMAL)  # Se habilita el botón de "Fin de Carrera"
            logging.info("Carrera iniciada.")  # Registro de inicio de carrera
            self.root.after(60000, self.actualizar_carrera)  # Actualización de la carrera cada 60 segundos

    # Método para detener una carrera
    def detener_carrera(self):
        if self.carrera_iniciada:  # Si la carrera está iniciada
            self.carrera_iniciada = False  # Se marca como detenida
            self.en_movimiento = False  # Se asegura que termine en estado "parado"
            self.estado_label.configure(text="Taxi detenido.")  # Actualización de la etiqueta de estado
            self.boton_empezar_carrera.configure(state=tk.NORMAL)  # Se habilita el botón de "Empezar Carrera"
            self.boton_marcha.configure(state=tk.DISABLED)  # Se deshabilita el botón de "Marcha"
            self.boton_parada.configure(state=tk.DISABLED)  # Se deshabilita el botón de "Parada"
            self.boton_fin_carrera.configure(state=tk.DISABLED)  # Se deshabilita el botón de "Fin de Carrera"
            logging.info("Carrera detenida.")  # Registro de fin de carrera

    # Método para actualizar los valores de la carrera
    def actualizar_carrera(self):
        if self.carrera_iniciada:  # Si la carrera está iniciada
            tiempo_actual = time.time()  # Se obtiene el tiempo actual
            tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio  # Cálculo del tiempo transcurrido
            self.tiempo_total += tiempo_transcurrido  # Se actualiza el tiempo total de la carrera

            if self.en_movimiento:  # Si el taxi está en movimiento
                self.tiempo_movimiento += tiempo_transcurrido  # Se actualiza el tiempo de movimiento
                self.total_euros += tiempo_transcurrido * self.tarifa_movimiento  # Se actualiza el total a cobrar
                self.estado_label.configure(text="Taxi en movimiento.")  # Actualización de la etiqueta de estado
            else:  # Si el taxi está parado
                self.tiempo_parado += tiempo_transcurrido  # Se actualiza el tiempo de parada
                self.total_euros += tiempo_transcurrido * self.tarifa_parado  # Se actualiza el total a cobrar
                self.estado_label.configure(text="Taxi en parado.")  # Actualización de la etiqueta de estado

            self.tiempo_ultimo_cambio = tiempo_actual  # Se actualiza el tiempo del último cambio
            self.root.after(60000, self.actualizar_carrera)  # Actualización de la carrera cada 60 segundos

    # Método para resetear los valores del taxímetro
    def resetear_valores(self):
        self.tiempo_total = 0  # Se resetea el tiempo total de la carrera
        self.total_euros = 0  # Se resetea el total a cobrar
        self.tiempo_parado = 0  # Se resetea el tiempo de parada
        self.tiempo_movimiento = 0  # Se resetea el tiempo de movimiento

    # Método para crear la tabla de registros en la base de datos SQLite
    def crear_tabla_registros(self):
        try:
            self.conexion_bd = sqlite3.connect(self.db_path)  # Conexión a la base de datos
            cursor = self.conexion_bd.cursor()  # Cursor para ejecutar comandos SQL
            cursor.execute('''CREATE TABLE IF NOT EXISTS registros
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               fecha_hora TEXT NOT NULL,
                               duracion INTEGER NOT NULL,
                               euros REAL NOT NULL,
                               parado INTEGER NOT NULL,
                               movimiento INTEGER NOT NULL)''')  # Creación de la tabla si no existe
            self.conexion_bd.commit()  # Confirmación de los cambios en la base de datos
            cursor.close()  # Cierre del cursor
        except sqlite3.Error as error:
            logging.error("Error al crear la tabla de registros: %s" % error)  # Registro de error

    # Método para insertar un registro en la base de datos SQLite
    def insertar_registro(self):
        try:
            cursor = self.conexion_bd.cursor()  # Cursor para ejecutar comandos SQL
            cursor.execute('''INSERT INTO registros (fecha_hora, duracion, euros, parado, movimiento)
                              VALUES (?, ?, ?, ?, ?)''',
                           (time.strftime('%Y-%m-%d %H:%M:%S'), int(self.tiempo_total),
                            round(self.total_euros, 2), int(self.tiempo_parado),
                            int(self.tiempo_movimiento)))  # Inserción del registro
            self.conexion_bd.commit()  # Confirmación de los cambios en la base de datos
            cursor.close()  # Cierre del cursor
            logging.info("Registro insertado en la base de datos.")  # Registro de inserción exitosa
        except sqlite3.Error as error:
            logging.error("Error al insertar el registro: %s" % error)  # Registro de error

    # Método para autenticar la contraseña ingresada por el usuario
    def autenticar(self):
        dialog = CustomPasswordDialog(self.root, "Ingrese la contraseña para configurar las tarifas:")  # Ventana de contraseña personalizada
        self.root.wait_window(dialog)  # Espera hasta que la ventana se cierre
        if dialog.result and self.hash_password(dialog.result) == self.password_hash:  # Si la contraseña es correcta
            self.autenticado = True  # Se marca como autenticado
            self.show_custom_info("Contraseña aceptada. Ahora puede configurar las tarifas.")  # Notificación de autenticación exitosa
        else:  # Si la contraseña es incorrecta o no se ingresó
            self.show_custom_error("Contraseña incorrecta. No se pueden configurar las tarifas.")  # Notificación de error de autenticación

    # Método para configurar las tarifas de parado y movimiento
    def configurar_tarifas(self):
        if self.autenticado:  # Si está autenticado
            tarifa_parado = simpledialog.askfloat("Configuración de tarifas", "Ingrese la tarifa por minuto en parado:")  # Diálogo para ingresar la tarifa de parado
            if tarifa_parado is not None and tarifa_parado >= 0:  # Si se ingresó un valor válido
                self.tarifa_parado = tarifa_parado  # Se actualiza la tarifa de parado
                tarifa_movimiento = simpledialog.askfloat("Configuración de tarifas", "Ingrese la tarifa por minuto en movimiento:")  # Diálogo para ingresar la tarifa de movimiento
                if tarifa_movimiento is not None and tarifa_movimiento >= 0:  # Si se ingresó un valor válido
                    self.tarifa_movimiento = tarifa_movimiento  # Se actualiza la tarifa de movimiento
                    self.show_custom_info("Tarifas configuradas correctamente.")  # Notificación de configuración exitosa
        else:  # Si no está autenticado
            self.show_custom_error("Debe autenticarse para configurar las tarifas.")  # Notificación de error de autenticación

    # Método para iniciar la interfaz gráfica de usuario
    def iniciar_interfaz_grafica(self):
        self.root = tk.Tk()  # Creación de la ventana principal
        self.root.title("Taxímetro App")  # Título de la ventana principal
        self.root.geometry("800x600")  # Tamaño de la ventana principal

        # Marco principal para organizar los elementos
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Etiqueta para mostrar el estado del taxi
        self.estado_label = tk.Label(main_frame, text="Taxi detenido.", font=("Helvetica", 16), bg="lightgrey", fg="black", pady=20)
        self.estado_label.pack()

        # Botones para controlar la carrera
        self.boton_empezar_carrera = tk.Button(main_frame, text="Empezar Carrera", command=self.empezar_carrera, state=tk.NORMAL, font=("Helvetica", 14))
        self.boton_empezar_carrera.pack(pady=10)

        self.boton_marcha = tk.Button(main_frame, text="Marcha", command=self.cambiar_estado, state=tk.DISABLED, font=("Helvetica", 14))
        self.boton_marcha.pack(pady=10)

        self.boton_parada = tk.Button(main_frame, text="Parada", command=self.cambiar_estado, state=tk.DISABLED, font=("Helvetica", 14))
        self.boton_parada.pack(pady=10)

        self.boton_fin_carrera = tk.Button(main_frame, text="Fin de Carrera", command=self.detener_carrera, state=tk.DISABLED, font=("Helvetica", 14))
        self.boton_fin_carrera.pack(pady=10)

        # Menú de la aplicación
        menubar = tk.Menu(self.root)
        opciones_menu = tk.Menu(menubar, tearoff=0)
        opciones_menu.add_command(label="Configurar Tarifas", command=self.configurar_tarifas)
        opciones_menu.add_command(label="Autenticar", command=self.autenticar)
        opciones_menu.add_separator()
        opciones_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Opciones", menu=opciones_menu)
        self.root.config(menu=menubar)

        # Iniciar la interfaz gráfica
        self.root.mainloop()

    # Método para cambiar el estado del taxi (parado o en movimiento)
    def cambiar_estado(self):
        if self.en_movimiento:  # Si el taxi está en movimiento
            self.en_movimiento = False  # Se cambia a estado de parado
            self.estado_label.configure(text="Taxi en parado.")  # Actualización de la etiqueta de estado
        else:  # Si el taxi está parado
            self.en_movimiento = True  # Se cambia a estado de movimiento
            self.estado_label.configure(text="Taxi en movimiento.")  # Actualización de la etiqueta de estado
        self.tiempo_ultimo_cambio = time.time()  # Se actualiza el tiempo del último cambio

# Función principal para ejecutar el programa
def main():
    parser = argparse.ArgumentParser(description='Taxímetro App')
    parser.add_argument('--password', type=str, help='Contraseña para iniciar la aplicación')
    args = parser.parse_args()

    if args.password:
        taximetro = Taximetro(args.password)
        taximetro.iniciar_interfaz_grafica()
    else:
        print("Debe proporcionar una contraseña para iniciar la aplicación.")

if __name__ == "__main__":
    main()
