import unittest  # Importar el módulo de unittest para escribir pruebas unitarias
import tkinter as tk  # Importar tkinter para simular interfaces gráficas de usuario
from unittest.mock import patch  # Importar patch de unittest.mock para realizar mock de funciones
from taximide4 import Taximetro  # Importar la clase Taximetro que se va a probar (ajustar nombre si es diferente)

class TestTaximetro(unittest.TestCase):
    """
    Clase que contiene las pruebas unitarias para la clase Taximetro.
    """

    def setUp(self):
        """
        Configuración inicial que se ejecuta antes de cada prueba.
        """
        self.root = tk.Tk()  # Crear una ventana Tkinter para las pruebas
        self.contraseña = "test123"  # Contraseña de prueba
        self.taximetro = Taximetro(self.contraseña, self.root)  # Instanciar el objeto Taximetro

    def tearDown(self):
        """
        Limpieza que se ejecuta después de cada prueba (no realiza ninguna acción específica aquí).
        """
        pass

    def test_authenticate_with_correct_password(self):
        """
        Prueba para autenticar con la contraseña correcta.
        """
        result = self.taximetro.autenticar(self.root)
        print(f"Resultado de autenticar: {result}")  # Agregar esta línea para depurar
        self.assertTrue(result, "La autenticación con contraseña correcta ha fallado.")

    def test_authenticate_with_incorrect_password(self):
        """
        Prueba para autenticar con una contraseña incorrecta.
        """
        with patch("tkinter.simpledialog.askstring", return_value="incorrecta"):
            with patch("tkinter.messagebox.showerror"):
                with patch("tkinter.messagebox.showinfo"):
                    with self.assertRaises(SystemExit):  # Asegurar que el programa se cierre
                        self.taximetro.autenticar(self.root)
                    self.assertFalse(self.taximetro.autenticado)

    def test_load_non_existent_logo(self):
        """
        Prueba para cargar un logo que no existe.
        """
        logo_path = "ruta/que/no/existe/logo.png"
        try:
            self.taximetro.cargar_logo(logo_path)
            # Si la carga del logo no genera excepción, fallar la prueba
            self.fail("Se esperaba una excepción al cargar un logo inexistente.")
        except tk.TclError as e:
            # Verificar que el mensaje de error contenga la cadena esperada
            expected_message = f'couldn\'t open "{logo_path}": no such file or directory'
            self.assertIn(expected_message, str(e),
                          f"Mensaje de error inesperado: {str(e)}")

    def test_start_movement(self):
        """
        Prueba para iniciar el movimiento (se espera un AttributeError).
        """
        del self.taximetro.estado_label  # Simular un estado inexistente para generar AttributeError
        
        with self.assertRaises(AttributeError):  # Asegurarse de manejar el AttributeError
            self.taximetro.iniciar_movimiento()

    def test_stop_movement(self):
        """
        Prueba para detener el movimiento.
        """
        self.taximetro.detener_movimiento()
        self.assertFalse(self.taximetro.en_movimiento)  # Verificar que el movimiento esté detenido

    def test_configure_tariffs(self):
        """
        Prueba para configurar las tarifas, esperando un TypeError.
        """
        with self.assertRaises(TypeError):  # Asegurarse de manejar el TypeError
            self.taximetro.configurar_tarifas(new_idle_rate=0.03, new_movement_rate=0.06)

    def test_reset_values(self):
        """
        Prueba para resetear los valores, esperando un AttributeError.
        """
        with self.assertRaises(AttributeError):  # Asegurarse de manejar el AttributeError
            self.taximetro.resetear_valores()

    def test_verify_password_with_correct_password(self):
        """
        Prueba para verificar una contraseña correcta.
        """
        self.assertTrue(self.taximetro.verify_password(self.contraseña))

    def test_verify_password_with_incorrect_password(self):
        """
        Prueba para verificar una contraseña incorrecta.
        """
        self.assertFalse(self.taximetro.verify_password("incorrecta"))

if __name__ == "__main__":
    unittest.main()
