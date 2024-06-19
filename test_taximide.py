import unittest
import time
from unittest.mock import patch, MagicMock
import tkinter as tk
from tkinter import simpledialog, messagebox
from taximide6 import Taximetro

class TestTaximetro(unittest.TestCase):
    def setUp(self):
        self.taximetro = Taximetro(contraseña="test")

    def test_autenticacion_correcta(self):
        root = tk.Tk()
        with patch.object(simpledialog, 'askstring', return_value="test"):
            with patch.object(messagebox, 'showerror'):
                self.taximetro.autenticar(root)
                self.assertTrue(self.taximetro.autenticado)
    
    def test_autenticacion_incorrecta(self):
        root = tk.Tk()
        with patch.object(simpledialog, 'askstring', return_value="incorrecta"):
            with patch.object(messagebox, 'showerror') as mock_showerror:
                self.taximetro.autenticar(root)
                self.assertFalse(self.taximetro.autenticado)
                mock_showerror.assert_called_once()

    def test_iniciar_movimiento(self):
        self.taximetro.autenticado = True
        self.taximetro.en_movimiento = False
        self.taximetro.estado_label = MagicMock()

        self.taximetro.iniciar_movimiento()
        self.assertTrue(self.taximetro.en_movimiento)
        self.taximetro.estado_label.config.assert_called_once_with(text="Taxi en movimiento.", fg="green")

    def test_finalizar_carrera(self):
        self.taximetro.autenticado = True
        self.taximetro.tiempo_ultimo_cambio = time.time() - 3600  # Hace una hora
        self.taximetro.tiempo_parado = 1800  # 30 minutos
        self.taximetro.tiempo_movimiento = 3600  # 1 hora
        self.taximetro.total_euros = (self.taximetro.tiempo_parado * self.taximetro.tarifa_parado) + \
                                     (self.taximetro.tiempo_movimiento * self.taximetro.tarifa_movimiento)
        self.taximetro.conexion_bd = MagicMock()

        self.taximetro.finalizar_carrera()

        self.taximetro.insertar_registro.assert_called_once()
        self.taximetro.conexion_bd.close.assert_called_once()

    def tearDown(self):
        del self.taximetro

if __name__ == "__main__":
    unittest.main()
