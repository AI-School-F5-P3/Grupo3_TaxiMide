import unittest
from unittest.mock import patch
import tkinter as tk
from taximide import Taximetro

class TestTaximetroApp(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = Taximetro(self.root)
        
    def tearDown(self):
        self.app.cerrar_conexion_bd()
        self.root.destroy()
        
    def test_iniciar_carrera(self):
        self.app.empezar_carrera()
        self.assertTrue(self.app.carrera_iniciada, "La carrera debería haber comenzado.")
        self.assertEqual(self.app.estado_label['text'], "Carrera en marcha.")
        
    def test_iniciar_movimiento(self):
        self.app.empezar_carrera()
        self.app.iniciar_movimiento()
        self.assertTrue(self.app.en_movimiento, "El taxi debería estar en movimiento.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en movimiento.")
        
    def test_iniciar_paro(self):
        self.app.empezar_carrera()
        self.app.iniciar_movimiento()
        self.app.iniciar_paro()
        self.assertFalse(self.app.en_movimiento, "El taxi debería estar parado.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en parado.")
        
    def test_finalizar_carrera(self):
        self.app.empezar_carrera()
        self.app.finalizar_carrera()
        self.assertFalse(self.app.carrera_iniciada, "La carrera debería haber finalizado.")
        self.assertEqual(self.app.estado_label['text'], "Taxi en parado.")
        
    @patch('taximetro.Taximetro.autenticar')
    def test_autenticacion(self, mock_autenticar):
        mock_autenticar.return_value = True
        self.app.autenticar()
        self.assertTrue(self.app.autenticado, "El usuario debería estar autenticado.")
    
    def test_configuracion_tarifas(self):
        self.app.tarifa_parado = 0.03
        self.app.tarifa_movimiento = 0.06
        self.assertEqual(self.app.tarifa_parado, 0.03, "La tarifa en parado debería ser 0.03 €/minuto.")
        self.assertEqual(self.app.tarifa_movimiento, 0.06, "La tarifa en movimiento debería ser 0.06 €/minuto.")

    def test_registro_carrera(self):
        self.app.empezar_carrera()
        self.app.tiempo_total = 10
        self.app.total_euros = 5.0
        self.app.finalizar_carrera()
        cursor = self.app.conexion_bd.cursor()
        cursor.execute("SELECT * FROM registros WHERE total = 5.0")
        registros = cursor.fetchall()
        self.assertGreater(len(registros), 0, "Debería haber al menos un registro con un total de 5.0 euros.")
        self.app.cerrar_conexion_bd()
        
if __name__ == '__main__':
    unittest.main()
