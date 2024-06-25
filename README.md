
<div style="text-align: center;">
  <img src="https://github.com/AI-School-F5-P3/Grupo3_taxi/assets/150898218/63b938ce-ced5-49dd-9fb3-98c3e01184b0" alt="Logotipo App Degradado Azul Verde">
</div>

# Bienvenido a nuestro primer proyecto! Un taxímetro inteligente.🚕
Este proyecto es una aplicación GUI para un taxímetro digital, desarrollada en Python utilizando las bibliotecas tkinter y customtkinter. La aplicación permite calcular las tarifas de un taxi en movimiento y en parado, gestionar contraseñas para configurar tarifas, y registrar los viajes en una base de datos SQLite

## Características
* Tarifas por defecto: 0.02 €/minuto en parado y 0.05 €/minuto en movimiento.
* Autenticación: Protección con contraseña para acceder a las funciones de configuración.
* Interfaz gráfica: Fácil de usar, con botones para iniciar/parar el movimiento y finalizar la carrera.
* Registros: Almacena los datos de los viajes (tiempo y costo) en una base de datos SQLite.
* Configuración de tarifas: Permite cambiar las tarifas de paro y movimiento.
* Gestión de contraseñas: Capacidad de cambiar la contraseña con validación de requisitos mínimos.

## Requisitos
* Python 3.x
* Bibliotecas: hashlib, re, time, logging, argparse, tkinter, customtkinter, sqlite3

## Instalación
1. Clonar el repositorio:
Copiar código
git clone git@github.com:AI-School-F5-P3/Grupo3_TaxiMide.git

2. Instalar las dependencias:
pip install customtkinter

3. Ejecutar la aplicación:
python taximetro.py --password tu_contraseña

## Uso
1. Iniciar la aplicación: Al iniciar, se solicitará la contraseña configurada para poder acceder a las funciones de la aplicación.
2. Interfaz principal:
  * Marcha: Inicia el conteo del tiempo en movimiento.
  * Parada: Detiene el conteo del tiempo en movimiento y lo cambia a tiempo en parado.
  * Tarifas: Permite configurar nuevas tarifas para el tiempo en movimiento y en parado.
  * Contraseña: Permite cambiar la contraseña actual.
  * Exit: Cierra la aplicación.
3. Finalizar la carrera: Calcula el total a cobrar y guarda los datos en la base de datos.

