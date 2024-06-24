# cambio visual con iconos y contadores en azul para el tiempo y verde para el dinero. 
import streamlit as st
import hashlib
import time
import logging
import sqlite3
from datetime import datetime

# Configuración del logging
logging.basicConfig(filename='taximetro.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Contraseña por defecto
CONTRASENA_DEFECTO = "1234"

# Conexión a la base de datos SQLite
conn = sqlite3.connect('registros.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS registros
             (id INTEGER PRIMARY KEY, timestamp TEXT, tiempo_total REAL, total_a_cobrar REAL, tarifa REAL)''')
conn.commit()

# Configuración de la página
st.set_page_config(page_title="Taxímetro Digital", page_icon="🚕", layout="wide")

# Variables globales y configuración de sesión
if 'tiempo_total' not in st.session_state:
    st.session_state.tiempo_total = 0
if 'total_a_cobrar' not in st.session_state:
    st.session_state.total_a_cobrar = 0.0
if 'tarifa_parada' not in st.session_state:
    st.session_state.tarifa_parada = 0.02
if 'tarifa_movimiento' not in st.session_state:
    st.session_state.tarifa_movimiento = 0.05
if 'en_movimiento' not in st.session_state:
    st.session_state.en_movimiento = False
if 'ultimo_cambio' not in st.session_state:
    st.session_state.ultimo_cambio = time.time()
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'password_hash' not in st.session_state:
    st.session_state.password_hash = hashlib.sha256(CONTRASENA_DEFECTO.encode()).hexdigest()
if 'fin_carrera' not in st.session_state:
    st.session_state.fin_carrera = False

# Funciones auxiliares
def calcular_costo(tiempo_segundos, tarifa):
    return tiempo_segundos * tarifa

def actualizar_tiempo_costo():
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultimo_cambio
    st.session_state.ultimo_cambio = tiempo_actual
    
    if st.session_state.en_movimiento:
        st.session_state.tiempo_total += tiempo_transcurrido
        st.session_state.total_a_cobrar += calcular_costo(tiempo_transcurrido, st.session_state.tarifa_movimiento)
    else:
        st.session_state.tiempo_total += tiempo_transcurrido
        st.session_state.total_a_cobrar += calcular_costo(tiempo_transcurrido, st.session_state.tarifa_parada)

def iniciar_movimiento():
    actualizar_tiempo_costo()
    st.session_state.en_movimiento = True
    st.success("Taxímetro en marcha. Tarifando a 0.05 €/segundo.")
    logging.info("Taxímetro en movimiento. Tarifando a 0.05 €/segundo.")

def detener_movimiento():
    actualizar_tiempo_costo()
    st.session_state.en_movimiento = False
    st.warning("Taxímetro detenido. Tarifando a 0.02 €/segundo.")
    logging.info("Taxímetro detenido. Tarifando a 0.02 €/segundo.")

def configurar_tarifas():
    nueva_tarifa_parado = st.number_input("Tarifa en parado (€ por segundo)", min_value=0.0, value=st.session_state.tarifa_parada, format="%.2f")
    nueva_tarifa_movimiento = st.number_input("Tarifa en movimiento (€ por segundo)", min_value=0.0, value=st.session_state.tarifa_movimiento, format="%.2f")
    
    if st.button("Guardar tarifas"):
        st.session_state.tarifa_parada = nueva_tarifa_parado
        st.session_state.tarifa_movimiento = nueva_tarifa_movimiento
        st.success("Tarifas actualizadas correctamente.")
        logging.info(f"Tarifas actualizadas: Parado - {nueva_tarifa_parado} €/seg, Movimiento - {nueva_tarifa_movimiento} €/seg")

def cambiar_contraseña():
    nueva_contraseña = st.text_input("Ingresa la nueva contraseña:", type="password")
    confirmar_contraseña = st.text_input("Confirma la nueva contraseña:", type="password")
    
    if st.button("Guardar contraseña"):
        if nueva_contraseña == confirmar_contraseña:
            st.session_state.password_hash = hashlib.sha256(nueva_contraseña.encode()).hexdigest()
            st.success("Contraseña cambiada correctamente.")
            logging.info("Contraseña cambiada correctamente.")
        else:
            st.error("Las contraseñas no coinciden.")

def finalizar_programa():
    actualizar_tiempo_costo()
    st.session_state.fin_carrera = True
    st.markdown(f"<h1 style='font-size:36px; color: #1E90FF;'>El costo total de la carrera es: {st.session_state.total_a_cobrar:.2f} €</h1>", unsafe_allow_html=True)
    logging.info(f"Carrera finalizada. Costo total: {st.session_state.total_a_cobrar:.2f} €")

    # Guardar registro en la base de datos
    tarifa_actual = st.session_state.tarifa_movimiento if st.session_state.en_movimiento else st.session_state.tarifa_parada
    c.execute('''INSERT INTO registros (timestamp, tiempo_total, total_a_cobrar, tarifa) VALUES (?, ?, ?, ?)''', 
              (time.strftime('%Y-%m-%d %H:%M:%S'), st.session_state.tiempo_total, st.session_state.total_a_cobrar, tarifa_actual))
    conn.commit()

    st.write("¿Quieres reiniciar otra carrera?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sí", key="si_reiniciar"):
            reiniciar_carrera()
    with col2:
        if st.button("No", key="no_reiniciar"):
            st.warning("Programa finalizado.")
            conn.close()
            st.stop()

def reiniciar_carrera():
    st.session_state.tiempo_total = 0
    st.session_state.total_a_cobrar = 0.0
    st.session_state.ultimo_cambio = time.time()
    st.session_state.fin_carrera = False
    st.session_state.en_movimiento = False  # Reiniciar el estado de movimiento
    st.success("Carrera reiniciada.")
    logging.info("Carrera reiniciada.")
    st.experimental_rerun()  # Recargar la página para comenzar una nueva carrera

def pagina_inicio():
    st.title("Taxímetro Digital 🚕")
    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #1E90FF;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">Bienvenido al Taxímetro Digital</p>', unsafe_allow_html=True)
    
    contrasena = st.text_input("Ingresa la contraseña:", type="password", key="input_contraseña")
    if st.button("Acceder", key="button_acceder"):
        if hashlib.sha256(contrasena.encode()).hexdigest() == st.session_state.password_hash:
            st.session_state.autenticado = True
            st.experimental_rerun()  # Recargar la página para mostrar la página principal
        else:
            st.error("Contraseña incorrecta. Inténtalo nuevamente.")

def pagina_principal():
    st.sidebar.title("Panel de Control")
    
    if st.sidebar.button("🚗 Marcha", key="boton_marcha"):
        iniciar_movimiento()
    
    if st.sidebar.button("🛑 Parada", key="boton_parada"):
        detener_movimiento()
    
    if st.sidebar.button("⚙️ Configurar Tarifas", key="boton_tarifas"):
        configurar_tarifas()
    
    if st.sidebar.button("🔐 Cambiar Contraseña", key="boton_contraseña"):
        cambiar_contraseña()
    
    if st.sidebar.button("🏁 Fin", key="boton_fin"):
        finalizar_programa()
    
    actualizar_tiempo_costo()
    
    tarifa_actual = st.session_state.tarifa_movimiento if st.session_state.en_movimiento else st.session_state.tarifa_parada
    
    # Mostrar las tarifas por defecto
    st.markdown(f"""
    <div style='border: 2px solid #1E90FF; border-radius: 10px; padding: 10px; margin-bottom: 20px;'>
    <h3 style='color: #1E90FF;'>Tarifas actuales:</h3>
    <p>Parado: {st.session_state.tarifa_parada:.2f} €/segundo</p>
    <p>Movimiento: {st.session_state.tarifa_movimiento:.2f} €/segundo</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar tiempo y costo
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<h1 style='font-size:48px; color: #1E90FF;'>⏱️ Tiempo: {int(st.session_state.tiempo_total)} seg</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1 style='font-size:48px; color: #32CD32;'>💶 Total: {st.session_state.total_a_cobrar:.2f} €</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='font-size:24px; color: #FF4500;'>Tarifa actual: {tarifa_actual:.2f} €/segundo</h2>", unsafe_allow_html=True)

    # Mostrar estado actual
    estado = "En movimiento 🚗" if st.session_state.en_movimiento else "Detenido 🛑"
    st.markdown(f"<h2 style='font-size:36px; color: {'#32CD32' if st.session_state.en_movimiento else '#FF4500'};'>Estado: {estado}</h2>", unsafe_allow_html=True)

    # Mostrar fecha y hora actual
    st.markdown(f"<p style='font-size:18px; color: #808080;'>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)

    if not st.session_state.fin_carrera:
        time.sleep(1)
        st.experimental_rerun()  # Recargar la página cada segundo para actualizar los contadores

def main():
    if not st.session_state.autenticado:
        pagina_inicio()
    else:
        pagina_principal()

if __name__ == "__main__":
    main()