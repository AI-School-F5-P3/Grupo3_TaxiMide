import unittest
from unittest.mock import Mock, patch
import time
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from io import StringIO
import sys

from taximide import Taximetro

class TestTaximetro(unittest.TestCase):
    
    def setUp(self):
        # Configuración inicial para cada prueba
        self.taximetro = Taximetro(contraseña='testpass')
        self.root_mock = Mock()

    def test_autenticar_correctamente(self):
        # Prueba de autenticación correcta
        with patch('builtins.simpledialog.askstring', return_value='testpass'):
            self.taximetro.autenticar(self.root_mock)
            self.assertTrue(self.taximetro.autenticado)
    
    def test_autenticar_incorrectamente(self):
        # Prueba de autenticación incorrecta
        with patch('builtins.simpledialog.askstring', return_value='incorrectpass'):
            with patch('tkinter.messagebox.showerror'):
                self.taximetro.autenticar(self.root_mock)
                self.assertFalse(self.taximetro.autenticado)

    def test_crear_tabla_registros(self):
        # Prueba para verificar la creación de la tabla en la base de datos
        self.taximetro.conexion_bd = sqlite3.connect(':memory:')  # Usando base de datos en memoria para pruebas
        self.taximetro.crear_tabla_registros()
        cursor = self.taximetro.conexion_bd.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registros';")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
    
    def test_insertar_registro(self):
        # Prueba para verificar la inserción de registros en la base de datos
        self.taximetro.conexion_bd = sqlite3.connect(':memory:')  # Usando base de datos en memoria para pruebas
        self.taximetro.crear_tabla_registros()
        self.taximetro.insertar_registro(
            tiempo_inicio='2023-01-01 12:00:00',
            tiempo_fin='2023-01-01 12:30:00',
            tiempo_parado=15.0,
            tiempo_movimiento=15.0,
            total_euros=7.50
        )
        cursor = self.taximetro.conexion_bd.cursor()
        cursor.execute("SELECT * FROM registros;")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[3], 15.0)  # Verifica que el tiempo parado sea correcto en la prueba

    def test_iniciar_movimiento(self):
        # Prueba para verificar el inicio del movimiento
        initial_time = time.time()
        self.taximetro._cambiar_estado(initial_time, False)  # Iniciar en estado parado
        self.taximetro.iniciar_movimiento()
        self.assertTrue(self.taximetro.en_movimiento)
    
    def test_detener_movimiento(self):
        # Prueba para verificar la detención del movimiento
        initial_time = time.time()
        self.taximetro._cambiar_estado(initial_time, True)  # Iniciar en estado de movimiento
        self.taximetro.detener_movimiento()
        self.assertFalse(self.taximetro.en_movimiento)

    def test_finalizar_carrera(self):
        # Prueba para verificar el cálculo del total y la inserción de registros al finalizar la carrera
        initial_time = time.time()
        self.taximetro._cambiar_estado(initial_time, True)  # Iniciar en estado de movimiento
        self.taximetro.finalizar_carrera()
        self.assertEqual(self.taximetro.total_euros, 0.75)  # Asumiendo tarifas de prueba
    
    def test_resetear_valores(self):
        # Prueba para verificar el reseteo de los valores después de finalizar una carrera
        self.taximetro.resetear_valores()
        self.assertEqual(self.taximetro.tiempo_total, 0)
        self.assertEqual(self.taximetro.total_euros, 0)
        self.assertFalse(self.taximetro.en_movimiento)
        self.assertEqual(self.taximetro.tiempo_parado, 0)
        self.assertEqual(self.taximetro.tiempo_movimiento, 0)

    def test_cambiar_contraseña(self):
        # Prueba para verificar el cambio de contraseña
        self.taximetro.autenticado = True
        initial_password = self.taximetro.contraseña
        new_password = 'newpass'
        with patch('builtins.simpledialog.askstring', side_effect=[new_password, new_password]):
            self.taximetro.cambiar_contraseña()
            self.assertEqual(self.taximetro.contraseña, new_password)

    def test_preguntar_nueva_carrera(self):
        # Prueba para verificar la pregunta de inicio de nueva carrera
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.taximetro.preguntar_nueva_carrera()
            self.assertFalse(self.root_mock.destroy.called)  # Verifica que no se destruya la ventana si se inicia una nueva carrera

    def test_cerrar_conexion_bd_al_destruir(self):
        # Prueba para verificar el cierre de la conexión a la base de datos al destruir la instancia
        self.taximetro.conexion_bd = Mock()
        self.taximetro.__del__()
        self.taximetro.conexion_bd.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
