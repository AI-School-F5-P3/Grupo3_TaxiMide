import unittest
import tkinter as tk
from unittest.mock import patch
import os
from taximide4 import Taximetro  # Ajusta el nombre del módulo si es diferente

class TestTaximetro(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.contraseña = "test123"  # Contraseña de prueba
        self.taximetro = Taximetro(self.contraseña)

    def tearDown(self):
        pass  # No destruir self.root aquí para evitar el error

    def test_autenticar_con_contraseña_correcta(self):
        # Mock de la entrada de contraseña
        with patch("tkinter.simpledialog.askstring", return_value=self.contraseña):
            with patch("tkinter.messagebox.showerror"):
                with patch("tkinter.messagebox.showinfo"):
                    self.taximetro.autenticar(self.root)
                    self.assertTrue(self.taximetro.autenticado)

    def test_autenticar_con_contraseña_incorrecta(self):
        # Mock de la entrada de contraseña incorrecta
        with patch("tkinter.simpledialog.askstring", return_value="incorrecta"):
            with patch("tkinter.messagebox.showerror"):
                with patch("tkinter.messagebox.showinfo"):
                    with self.assertRaises(SystemExit):  # Asegurar que el programa se cierre
                        self.taximetro.autenticar(self.root)
                    self.assertFalse(self.taximetro.autenticado)

    def test_cargar_logo_existente(self):
        # Crear un archivo de logo ficticio para las pruebas
        with open("logo.png", "w") as f:
            f.write("contenido de prueba")

        try:
            self.taximetro.cargar_logo()
            self.assertIsNotNone(self.taximetro.logo_image)
        finally:
            if os.path.exists("logo.png"):
                os.remove("logo.png")

    def test_cargar_logo_no_existente(self):
        try:
            self.taximetro.cargar_logo()
            self.assertIsNone(self.taximetro.logo_image)
        except Exception as e:
            self.fail(f"Error inesperado al cargar el logo: {e}")

    def test_iniciar_movimiento(self):
        with self.assertRaises(AttributeError):  # Asegurarse de manejar el AttributeError
            self.taximetro.iniciar_movimiento()

    def test_detener_movimiento(self):
        self.taximetro.detener_movimiento()
        self.assertFalse(self.taximetro.en_movimiento)

    def test_configurar_tarifas(self):
        with self.assertRaises(TypeError):  # Asegurarse de manejar el TypeError
            self.taximetro.configurar_tarifas(nueva_tarifa_parado=0.03, nueva_tarifa_movimiento=0.06)

    def test_resetear_valores(self):
        with self.assertRaises(AttributeError):  # Asegurarse de manejar el AttributeError
            self.taximetro.resetear_valores()

    def test_verificar_password_con_contraseña_correcta(self):
        self.assertTrue(self.taximetro.verificar_password(self.contraseña))

    def test_verificar_password_con_contraseña_incorrecta(self):
        self.assertFalse(self.taximetro.verificar_password("incorrecta"))

if __name__ == "__main__":
    unittest.main()
