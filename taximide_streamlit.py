import hashlib
import re
import time
import logging
import sqlite3
import streamlit as st

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

    def iniciar_carrera(self):
        self.autenticar()
        if not self.autenticado:
            return
        
        st.title("TaxiMide")
        st.sidebar.header("Control de Carrera")
        self.estado_label = st.empty()
        self.total_label = st.empty()
        self.actualizar_tiempo_costo()

        if st.sidebar.button("Marcha"):
            self.iniciar_movimiento()
        
        if st.sidebar.button("Parada"):
            self.detener_movimiento()

        if st.sidebar.button("Configurar tarifas"):
            self.configurar_tarifas()

        if st.sidebar.button("Cambiar contraseña"):
            self.cambiar_contraseña()

        if st.sidebar.button("Fin"):
            self.finalizar_carrera()
        
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

        self.estado_label.markdown(f"### Taxi {'en movimiento' if self.en_movimiento else 'en parado'}")
        self.total_label.markdown(f"### Total a cobrar: {self.total_euros:.2f} euros")
        st.markdown(f"#### Tiempo total: {tiempo_formateado}")

        self.tiempo_ultimo_cambio = tiempo_actual
        st.experimental_rerun()

    def autenticar(self):
        intentos = 3
        while intentos > 0:
            if not self.autenticado:
                entered_password = st.text_input("Ingresa la contraseña para continuar:", type="password", key="auth_password")
                if st.button("Autenticar", key="auth_button"):
                    if self.verificar_password(entered_password):
                        self.autenticado = True
                        logging.info("Contraseña correcta. Acceso concedido.")
                    else:
                        st.error("Contraseña incorrecta. Inténtalo de nuevo.")
                        logging.warning("Intento de acceso con contraseña incorrecta.")
                        intentos -= 1
            else:
                break

        if intentos == 0:
            logging.error("Número máximo de intentos alcanzado. Cierre del programa.")
            st.error("Número máximo de intentos alcanzado. Cierre del programa.")
            st.stop()

    def verificar_password(self, entered_password):
        return entered_password == self.password_plaintext or self.hash_password(entered_password) == self.password_hash

    def cambiar_contraseña(self):
        if not self.autenticado:
            logging.warning("No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
            st.error("No se ha autenticado. Debes autenticarte para cambiar la contraseña.")
            return

        new_password = st.text_input("Introduce la nueva contraseña:", type="password", key="new_password")
        confirm_password = st.text_input("Confirma la nueva contraseña:", type="password", key="confirm_password")

        if st.button("Cambiar contraseña"):
            if new_password != confirm_password:
                logging.warning("La nueva contraseña no coincide con la confirmación.")
                st.error("La nueva contraseña no coincide con la confirmación.")
                return

            if not self.validate_password(new_password):
                st.error("La nueva contraseña no cumple los requisitos. Debe tener al menos 6 caracteres y solo puede contener letras, números y los caracteres . - _")
                return

            self.password_hash = self.hash_password(new_password)
            logging.info("Contraseña cambiada exitosamente.")
            st.success("Contraseña cambiada exitosamente.")
            self.autenticado = False
            self.autenticar()

    def validate_password(self, contraseña):
        if len(contraseña) < 6:
            return False
        if not re.match("^[a-zA-Z0-9._-]+$", contraseña):
            return False
        return True

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
            st.error("No se ha autenticado. Debes autenticarte para configurar las tarifas.")
            return

        try:
            nueva_tarifa_parado = float(st.text_input("Introduce la nueva tarifa en parado (€/minuto):", key="tarifa_parado"))
            nueva_tarifa_movimiento = float(st.text_input("Introduce la nueva tarifa en movimiento (€/minuto):", key="tarifa_movimiento"))
            self.tarifa_parado = nueva_tarifa_parado
            self.tarifa_movimiento = nueva_tarifa_movimiento
            logging.info("Tarifas actualizadas en parado: %.2f, y en movimiento: %.2f", self.tarifa_parado, self.tarifa_movimiento)
            st.success("Tarifas actualizadas.")
        except ValueError:
            logging.error("Error al introducir tarifas. Valores no numéricos.")
            st.error("Introduce valores numéricos válidos.")

    def _cambiar_estado(self, tiempo_actual, en_movimiento):
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_cambio
        if self.en_movimiento:
            self.tiempo_movimiento += tiempo_transcurrido
        else:
            self.tiempo_parado += tiempo_transcurrido

        self.en_movimiento = en_movimiento
        self.tiempo_ultimo_cambio = tiempo_actual
        estado = "movimiento" if en_movimiento else "parado"
        st.session_state.estado = estado
        logging.info(f"Taxi en {estado}.")

    def iniciar_movimiento(self):
        self._cambiar_estado(time.time(), True)

    def detener_movimiento(self):
        self._cambiar_estado(time.time(), False)

    def finalizar_carrera(self):
        tiempo_actual = time.time()
        self._cambiar_estado(tiempo_actual, self.en_movimiento)
        self.total_euros = (self.tiempo_movimiento * self.tarifa_movimiento) + (self.tiempo_parado * self.tarifa_parado)
        st.success(f"Total a cobrar: {self.total_euros:.2f} euros")
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
        nueva_carrera = st.button("¿Deseas iniciar una nueva carrera?")
        if not nueva_carrera:
            st.stop()

    def resetear_valores(self):
        self.tiempo_total = 0
        self.total_euros = 0
        self.en_movimiento = False
        self.tiempo_ultimo_cambio = time.time()
        self.tiempo_parado = 0
        self.tiempo_movimiento = 0

    def __del__(self):
        try:
            if self.conexion_bd:
                self.conexion_bd.close()
                logging.info("Conexión a la base de datos cerrada correctamente.")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión a la base de datos: {e}")

def main():
    st.set_page_config(page_title="TaxiMide App", page_icon=":car:", layout="wide")
    args = parse_args()
    taximetro = Taximetro(args.password)
    taximetro.iniciar_carrera()

if __name__ == "__main__":
    main()
