import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import time
from taximide4 import Taximetro  # Asegúrate de que el nombre del archivo principal es taximide4.py

class TestTaxiApp(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = Taximetro(self.root)

    def tearDown(self):
        self.app.destroy()
        self.root.destroy()

    @patch('taximide4.time.time', return_value=1000)
    def test_empezar_carrera(self, mock_time):
        self.app.empezar_carrera()
        self.assertTrue(self.app.carrera_iniciada)
        self.assertEqual(self.app.tiempo_inicio, 1000)
        self.assertEqual(self.app.tiempo_total, 0)
        self.assertEqual(self.app.costo_total, 0)
        self.assertEqual(self.app.label_tiempo.cget("text"), "Tiempo: 00:00:00")
        self.assertEqual(self.app.label_costo.cget("text"), "Costo: 0.00")

    @patch('taximide4.time.time', side_effect=[1000, 1060])
    def test_finalizar_carrera(self, mock_time):
        self.app.empezar_carrera()
        time.sleep(1)
        self.app.finalizar_carrera()
        self.assertFalse(self.app.carrera_iniciada)
        self.assertEqual(self.app.tiempo_total, 60)
        self.assertEqual(self.app.costo_total, 60 * 0.5)  # Suponiendo costo 0.5 por segundo
        self.assertEqual(self.app.label_tiempo.cget("text"), "Tiempo: 00:01:00")
        self.assertEqual(self.app.label_costo.cget("text"), f"Costo: {60 * 0.5:.2f}")

    @patch('taximide4.time.time', return_value=1000)
    def test_marcar_marcha(self, mock_time):
        self.app.empezar_carrera()
        self.app.marcar_parada()
        self.app.marcar_marcha()
        self.assertTrue(self.app.carrera_iniciada)
        self.assertEqual(self.app.tiempo_inicio, 1000)
        self.assertFalse(self.app.marcha)
        self.assertEqual(self.app.label_tiempo.cget("text"), "Tiempo: 00:00:00")
        self.assertEqual(self.app.label_costo.cget("text"), "Costo: 0.00")

    @patch('taximide4.time.time', return_value=1000)
    def test_marcar_parada(self, mock_time):
        self.app.empezar_carrera()
        self.app.marcar_parada()
        self.assertFalse(self.app.marcha)
        self.assertEqual(self.app.label_tiempo.cget("text"), "Tiempo: 00:00:00")
        self.assertEqual(self.app.label_costo.cget("text"), "Costo: 0.00")

if __name__ == '__main__':
    unittest.main()
