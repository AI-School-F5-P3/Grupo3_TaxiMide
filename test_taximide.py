import unittest
from unittest.mock import Mock, patch
import time
import sqlite3
from tkinter import simpledialog
from io import StringIO
import sys

from taximide import Taximetro

class TestTaximetro(unittest.TestCase):

    def setUp(self):
        # Configuración inicial para cada prueba
        self.taximetro = Taximetro(contraseña='testpass')
        self.root_mock = Mock()

    @patch('time.time', return_value=1000000.0)
    def test_autenticar_correctamente(self, mock_time):
        # Prueba de autenticación correcta
        with patch('tkinter.simpledialog.askstring', return_value='testpass'):
            self.taximetro.autenticar(self.root_mock)
            self.assertTrue(self.taximetro.autenticado)

    @patch('time.time', return_value=1000000.0)
    def test_autenticar_incorrectamente(self, mock_time):
        # Prueba de autenticación incorrecta
        with patch('tkinter.simpledialog.askstring', return_value='incorrectpass'):
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

    @patch('time.time', return_value=1000000.0)
    def test_iniciar_movimiento(self, mock_time):
        # Prueba para verificar el inicio del movimiento
        self.taximetro._cambiar_estado(mock_time.return_value, False)  # Iniciar en estado parado
        self.taximetro.iniciar_movimiento()
        self.assertTrue(self.taximetro.en_movimiento)

    @patch('time.time', return_value=1000000.0)
    def test_detener_movimiento(self, mock_time):
        # Prueba para verificar la detención del movimiento
        self.taximetro._cambiar_estado(mock_time.return_value, True)  # Iniciar en estado de movimiento
        self.taximetro.detener_movimiento()
        self.assertFalse(self.taximetro.en_movimiento)

    @patch('time.time', side_effect=[1000000.0, 1000000.0 + 900])
    def test_finalizar_carrera(self, mock_time):
        # Prueba para verificar el cálculo del total y la inserción de registros al finalizar la carrera
        self.taximetro._cambiar_estado(mock_time.side_effect[0], True)  # Iniciar en estado de movimiento
        self.taximetro.finalizar_carrera()
        # Asumimos tarifas de prueba para 15 minutos de movimiento
        esperado_total_euros = (900 / 60) * self.taximetro.tarifa_movimiento
        self.assertAlmostEqual(self.taximetro.total_euros, esperado_total_euros)

    def test_resetear_valores(self):
        # Prueba para verificar el reseteo de los valores después de finalizar una carrera
        self.taximetro.resetear_valores()
        self.assertEqual(self.taximetro.tiempo_total, 0)
        self.assertEqual(self.taximetro.total_euros, 0)
        self.assertFalse(self.taximetro.en_movimiento)
        self.assertEqual(self.taximetro.tiempo_parado, 0)
        self.assertEqual(self.taximetro.tiempo_movimiento, 0)

    @patch('time.time', return_value=1000000.0)
    def test_cambiar_contraseña(self, mock_time):
        # Prueba para verificar el cambio de contraseña
        self.taximetro.autenticado = True
        initial_password = self.taximetro.contraseña
        new_password = 'newpass'
        with patch('tkinter.simpledialog.askstring', side_effect=[new_password, new_password]):
            self.taximetro.cambiar_contraseña()
            self.assertEqual(self.taximetro.contraseña, new_password)

    @patch('tkinter.messagebox.askyesno', return_value=True)
    @patch.object(Taximetro, 'iniciar_carrera')
    def test_preguntar_nueva_carrera(self, mock_askyesno, mock_iniciar_carrera):
        # Prueba para verificar la pregunta de inicio de nueva carrera
        self.taximetro.root = self.root_mock
        self.taximetro.preguntar_nueva_carrera()
        mock_iniciar_carrera.assert_called_once()

    def test_cerrar_conexion_bd_al_destruir(self):
        # Prueba para verificar el cierre de la conexión a la base de datos al destruir la instancia
        self.taximetro.conexion_bd = Mock()
        self.taximetro.__del__()
        self.taximetro.conexion_bd.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
