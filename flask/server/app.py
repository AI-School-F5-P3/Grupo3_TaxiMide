import hashlib
import time
import logging
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Asegurarse de que el directorio 'server' exista para los archivos de log y la base de datos
if not os.path.exists('server'):
    os.makedirs('server')

# Configuración del logging
logging.basicConfig(filename='server/taximetro.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Contraseña por defecto
CONTRASENA_DEFECTO = "1234"

# Conexión a la base de datos SQLite
conn = sqlite3.connect('server/registros.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS registros (id INTEGER PRIMARY KEY, timestamp TEXT, tiempo_total REAL, total_a_cobrar REAL, tarifa REAL)''')
conn.commit()

# Variables globales y configuración de sesión
tiempo_total = 0
total_a_cobrar = 0.0
tarifa_parada = 0.02
tarifa_movimiento = 0.05
en_movimiento = False
ultimo_cambio = time.time()
autenticado = False
password_hash = hashlib.sha256(CONTRASENA_DEFECTO.encode()).hexdigest()
fin_carrera = False

# Funciones auxiliares
def calcular_costo(tiempo_segundos, tarifa):
    return tiempo_segundos * tarifa

def actualizar_tiempo_costo():
    global tiempo_total, total_a_cobrar, ultimo_cambio, en_movimiento, tarifa_parada, tarifa_movimiento

    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - ultimo_cambio
    ultimo_cambio = tiempo_actual

    if en_movimiento:
        tiempo_total += tiempo_transcurrido
        total_a_cobrar += calcular_costo(tiempo_transcurrido, tarifa_movimiento)
    else:
        tiempo_total += tiempo_transcurrido
        total_a_cobrar += calcular_costo(tiempo_transcurrido, tarifa_parada)

@app.route('/')
def pagina_inicio():
    global autenticado

    if not autenticado:
        return render_template('index.html')
    else:
        return redirect(url_for('pagina_principal'))

@app.route('/login', methods=['POST'])
def login():
    global autenticado, password_hash

    contrasena = request.form['password']

    if hashlib.sha256(contrasena.encode()).hexdigest() == password_hash:
        autenticado = True
        return redirect(url_for('pagina_principal'))
    else:
        return render_template('index.html', error=True)

@app.route('/main')
def pagina_principal():
    global tiempo_total, total_a_cobrar, ultimo_cambio, en_movimiento, tarifa_parada, tarifa_movimiento, autenticado, fin_carrera

    if not autenticado:
        return redirect(url_for('pagina_inicio'))

    actualizar_tiempo_costo()

    return render_template('main.html', tiempo_total=int(tiempo_total), total_a_cobrar=total_a_cobrar, en_movimiento=en_movimiento, tarifa_parada=tarifa_parada, tarifa_movimiento=tarifa_movimiento)

@app.route('/start')
def iniciar_movimiento():
    global en_movimiento

    actualizar_tiempo_costo()
    en_movimiento = True
    logging.info("Taxímetro en movimiento. Tarifando a 0.05 €/segundo.")
    return redirect(url_for('pagina_principal'))

@app.route('/stop')
def detener_movimiento():
    global en_movimiento

    actualizar_tiempo_costo()
    en_movimiento = False
    logging.info("Taxímetro detenido. Tarifando a 0.02 €/segundo.")
    return redirect(url_for('pagina_principal'))

@app.route('/configurar', methods=['GET', 'POST'])
def configurar_tarifas():
    global tarifa_parada, tarifa_movimiento

    if request.method == 'POST':
        nueva_tarifa_parado = float(request.form['tarifa_parada'])
        nueva_tarifa_movimiento = float(request.form['tarifa_movimiento'])

        tarifa_parada = nueva_tarifa_parado
        tarifa_movimiento = nueva_tarifa_movimiento
        logging.info(f"Tarifas actualizadas: Parado - {nueva_tarifa_parado} €/seg, Movimiento - {nueva_tarifa_movimiento} €/seg")
        return redirect(url_for('pagina_principal'))

    return render_template('configurar.html', tarifa_parada=tarifa_parada, tarifa_movimiento=tarifa_movimiento)

@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contraseña():
    global password_hash

    if request.method == 'POST':
        nueva_contraseña = request.form['new_password']
        confirmar_contraseña = request.form['confirm_password']

        if nueva_contraseña == confirmar_contraseña:
            password_hash = hashlib.sha256(nueva_contraseña.encode()).hexdigest()
            logging.info("Contraseña cambiada correctamente.")
            return redirect(url_for('pagina_principal'))
        else:
            return render_template('cambiar_contrasena.html', error=True)

    return render_template('cambiar_contrasena.html')

@app.route('/finalizar')
def finalizar_programa():
    global tiempo_total, total_a_cobrar, en_movimiento, fin_carrera, tarifa_parada, tarifa_movimiento

    actualizar_tiempo_costo()
    fin_carrera = True
    logging.info(f"Carrera finalizada. Costo total: {total_a_cobrar:.2f} €")

    # Guardar registro en la base de datos
    tarifa_actual = tarifa_movimiento if en_movimiento else tarifa_parada
    c.execute('''INSERT INTO registros (timestamp, tiempo_total, total_a_cobrar, tarifa) VALUES (?, ?, ?, ?)''',
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tiempo_total, total_a_cobrar, tarifa_actual))
    conn.commit()

    return render_template('finalizar.html')

@app.route('/reiniciar')
def reiniciar_carrera():
    global tiempo_total, total_a_cobrar, ultimo_cambio, fin_carrera, en_movimiento

    tiempo_total = 0
    total_a_cobrar = 0.0
    ultimo_cambio = time.time()
    fin_carrera = False
    en_movimiento = False
    logging.info("Carrera reiniciada.")
    
    return redirect(url_for('pagina_principal'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
