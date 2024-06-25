import unittest
from unittest.mock import patch, Mock
import tkinter as tk
from taximide2 import Taximetro

class TestTaximetroApp(unittest.TestCase):

    def setUp(self):
        self.password = "test_password"  # Contraseña de prueba
        self.root = tk.Tk()
        self.app = Taximetro(self.password)
        self.app.estado_label = Mock()  # Mock para estado_label y otros componentes de GUI
        
    def tearDown(self):
        self.app.__del__()  # Llamar explícitamente al destructor para cerrar la conexión a la BD
        self.root.destroy()
        
    def test_empezar_carrera(self):
        self.app.empezar_carrera()
        self.assertTrue(self.app.carrera_iniciada, "La carrera debería haber comenzado.")
        self.app.estado_label.configure.assert_called_once_with(text="Taxi en parado.")

    def test_iniciar_movimiento(self):
        self.app.empezar_carrera()
        self.app.iniciar_movimiento()
        self.assertTrue(self.app.en_movimiento, "El taxi debería estar en movimiento.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en movimiento.")

    def test_detener_movimiento(self):
        self.app.empezar_carrera()
        self.app.iniciar_movimiento()
        self.app.detener_movimiento()
        self.assertFalse(self.app.en_movimiento, "El taxi debería estar parado.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en parado.")

    def test_finalizar_carrera(self):
        self.app.empezar_carrera()
        self.app.finalizar_carrera()
        self.assertFalse(self.app.carrera_iniciada, "La carrera debería haber finalizado.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en parado.")

    @patch('taximide.Taximetro.autenticar')
    def test_autenticacion(self, mock_autenticar):
        mock_autenticar.return_value = True
        self.app.autenticar(self.root)
        self.assertTrue(self.app.autenticado, "El usuario debería estar autenticado.")

    def test_configuracion_tarifas(self):
        self.app.configurar_tarifas()
        self.assertEqual(self.app.tarifa_parado, 0.02, "La tarifa en parado debería ser 0.02 €/minuto.")
        self.assertEqual(self.app.tarifa_movimiento, 0.05, "La tarifa en movimiento debería ser 0.05 €/minuto.")

    def test_registro_carrera(self):
        self.app.empezar_carrera()
        self.app.tiempo_total = 10
        self.app.total_euros = 5.0
        self.app.finalizar_carrera()
        cursor = self.app.conexion_bd.cursor()
        cursor.execute("SELECT * FROM registros WHERE total_euros = 5.0")  # Ajuste en la consulta SQL
        registros = cursor.fetchall()
        self.assertGreater(len(registros), 0, "Debería haber al menos un registro con un total de 5.0 euros.")

if __name__ == '__main__':
    unittest.main()

# Cambios realizados:

# - **Contraseña en `setUp`**: Se agregó una contraseña (`self.password`) que se utiliza para inicializar `Taximetro`. Esto refleja el comportamiento esperado de la aplicación.
  
# - **Nombres de métodos ajustados**: Los nombres de métodos como `test_iniciar_carrera`, `test_iniciar_movimiento`, `test_detener_movimiento`, etc., se ajustaron para reflejar los métodos reales en `Taximetro`.

# - **Consulta SQL en `test_registro_carrera`**: Se ajustó la consulta SQL para buscar registros con `total_euros = 5.0`, ya que `total` no es un campo en la tabla `registros`.

# Estos ajustes deberían permitir que las pruebas reflejen correctamente el comportamiento esperado de la aplicación `Taximetro`. Asegúrate de que los métodos y propiedades en `Taximetro` estén implementados y nombrados correctamente para que las pruebas funcionen sin problemas.
