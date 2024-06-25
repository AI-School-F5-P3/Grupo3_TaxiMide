# TaxiMide - Taxímetro Digital

## Índice

-   [Descripción](#descripci%C3%B3n)
-   [Requisitos](#requisitos)
-   [Instalación](#instalaci%C3%B3n)
-   [Uso](#uso)
    -   [Autenticación](#autenticaci%C3%B3n)
    -   [Interfaz](#interfaz)
    -   [Funcionalidades](#funcionalidades)
    -   [Registro de Carreras](#registro-de-carreras)
-   [Código](#c%C3%B3digo)
    -   [Importación de Bibliotecas](#importaci%C3%B3n-de-bibliotecas)
    -   [Configuración de Logging](#configuraci%C3%B3n-de-logging)
    -   [Diálogos Personalizados](#di%C3%A1logos-personalizados)
        -   [Diálogo de Contraseña](#di%C3%A1logo-de-contrase%C3%B1a)
        -   [Diálogo de Notificación](#di%C3%A1logo-de-notificaci%C3%B3n)
    -   [Clase Taxímetro](#clase-tax%C3%ADmetro)
        -   [Inicialización](#inicializaci%C3%B3n)
        -   [Hashing de Contraseñas](#hashing-de-contrase%C3%B1as)
        -   [Guardar y Cargar Contraseña](#guardar-y-cargar-contrase%C3%B1a)
        -   [Autenticación](#autenticaci%C3%B3n)
        -   [Cambio de Contraseña](#cambio-de-contrase%C3%B1a)
        -   [Validación de Contraseña](#validaci%C3%B3n-de-contrase%C3%B1a)
        -   [Configuración de Tarifas](#configuraci%C3%B3n-de-tarifas)
        -   [Gestión de Estado del Taxi](#gesti%C3%B3n-de-estado-del-taxi)
        -   [Actualización de Tiempo y Coste](#actualizaci%C3%B3n-de-tiempo-y-coste)
    -   [Base de Datos](#base-de-datos)
        -   [Creación de Tabla de Registros](#creaci%C3%B3n-de-tabla-de-registros)
        -   [Inserción de Registro](#inserci%C3%B3n-de-registro)
    -   [Ejecución Principal](#ejecuci%C3%B3n-principal)
-   [Contribución](#contribuci%C3%B3n)
-   [Licencia](#licencia)

## Descripción

TaxiMide es una aplicación de taxímetro digital diseñada para facilitar el cálculo de tarifas en carreras de taxi. La aplicación permite gestionar tarifas, iniciar y detener carreras, y calcular el coste total basado en el tiempo de parada y movimiento del vehículo. También incluye autenticación mediante contraseña y la posibilidad de configurar tarifas personalizadas.

## Requisitos

-   Python 3.x
-   Bibliotecas adicionales: hashlib, re, os, json, time, logging, argparse, tkinter, customtkinter, sqlite3

## Instalación

1.  Clonar el repositorio o descargar los archivos.
2.  Instalar las bibliotecas necesarias utilizando `pip`:
    
    `pip install customtkinter` 
    
3.  Ejecutar la aplicación:
    
    `python taximetro.py` 
    

## Uso

### Autenticación

Al iniciar la aplicación, se pedirá una contraseña para continuar. La contraseña por defecto es `1234`. Se recomienda cambiar esta contraseña por razones de seguridad.

### Interfaz

La interfaz se divide en dos paneles:

-   **Panel Izquierdo**: Contiene botones para iniciar la carrera, poner el taxi en marcha, detener el movimiento, configurar tarifas, cambiar la contraseña y salir de la aplicación.
-   **Panel Derecho**: Muestra el estado actual del taxi (parado o en movimiento), las tarifas en parado y en movimiento, y el total a cobrar. También incluye contadores visuales para el tiempo y el coste total.

### Funcionalidades

-   **Iniciar Carrera**: Resetea los valores y prepara el taxímetro para una nueva carrera.
-   **Marcha/Parada**: Cambia el estado del taxi entre parado y en movimiento.
-   **Configurar Tarifas**: Permite configurar nuevas tarifas para el tiempo en parado y en movimiento.
-   **Cambiar Contraseña**: Permite cambiar la contraseña de autenticación.
-   **Finalizar Carrera**: Calcula el coste total y guarda un registro de la carrera en la base de datos SQLite.

### Registro de Carreras

La aplicación guarda un registro de cada carrera en una base de datos SQLite (`taximetro.db`). Cada registro incluye la hora de inicio, hora de fin, tiempo en parado, tiempo en movimiento y el total en euros.

## Código

### Importación de Bibliotecas

`import hashlib`

`import re`

`import os`

`import json`

`import time`

`import logging`

`import argparse`

`import tkinter as tk`

`import customtkinter`

`from tkinter import messagebox, simpledialog`

`import sqlite3`

### Configuración de Logging

`logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[`
    `logging.FileHandler("taximideapp.log"), `
    `logging.StreamHandler()`
`])` 

### Diálogos Personalizados

#### Diálogo de Contraseña

`class CustomPasswordDialog(tk.Toplevel):`


#### Diálogo de Notificación

`class CustomNotificationDialog(tk.Toplevel):`


### Clase Taxímetro

#### Inicialización

`class Taximetro:`

`   def __init__(self, contraseña):`


#### Hashing de Contraseñas

`def hash_password(self, password):`


#### Guardar y Cargar Contraseña

`def save_password(self):`

`def load_password(self, default_password):`


#### Autenticación

`def autenticar(self, root):`

`def verify_password(self, entered_password):`


#### Cambio de Contraseña

`def cambiar_contraseña(self):`


#### Validación de Contraseña

`def validate_password(self, contraseña):`


#### Configuración de Tarifas

`def configurar_tarifas(self):`


#### Gestión de Estado del Taxi

`def empezar_carrera(self):`

`def iniciar_movimiento(self):`

`def detener_movimiento(self):`

`def finalizar_carrera(self):`


#### Actualización de Tiempo y Coste

`def actualizar_tiempo_costo(self):`


`def actualizar_canvas(self, canvas, texto):`


### Base de Datos

#### Creación de Tabla de Registros

`def crear_tabla_registros(self):`


#### Inserción de Registro

`def insertar_registro(self, tiempo_inicio, tiempo_fin, tiempo_parado, tiempo_movimiento, total_euros):`


### Ejecución Principal

`if __name__ == "__main__":`

`   parser = argparse.ArgumentParser(description="Iniciar la aplicación de taxímetro")`

`   parser.add_argument("-p", "--password", type=str, default="1234", help="Contraseña para el taxímetro")`

`   args = parser.parse_args()`


`   root = tk.Tk()`

`   taximetro = Taximetro(args.password)`

`   taximetro.iniciar_carrera(root)`

`   root.mainloop()`

## Contribución

Las contribuciones son bienvenidas. Por favor, crea un fork del repositorio, realiza tus cambios y abre un pull request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.