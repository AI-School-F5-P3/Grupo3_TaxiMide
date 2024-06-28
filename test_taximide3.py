import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk

# Importar el módulo que queremos probar
import taximide4

class TestTaximetro(unittest.TestCase):
    
    def setUp(self):
        # Preparar las condiciones necesarias para cada prueba, si las hay
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        # Limpiar después de cada prueba, si es necesario
        self.root.destroy()
    
    def test_hash_password(self):
        taximetro = taximide4.Taximetro("password")
        hashed_password = taximetro.hash_password("password")
        self.assertEqual(hashed_password, "a7b3c6f1a8d8c3b8f4b8e8b4d4b6b1d3c2a1a8f8d3e8c0a4a7e2b1f1e0f7c8")
    
    def test_verify_password(self):
        taximetro = taximide4.Taximetro("password")
        self.assertTrue(taximetro.verify_password("password"))
        self.assertFalse(taximetro.verify_password("incorrect_password"))
    
    # Ejemplo de cómo simular la interacción con el diálogo de contraseña
    @patch.object(taximide4, 'CustomPasswordDialog')
    def test_autenticar_correctamente(self, MockCustomPasswordDialog):
        # Configurar el mock para devolver la contraseña correcta
        mock_dialog = MagicMock()
        mock_dialog.result = "password"
        MockCustomPasswordDialog.return_value = mock_dialog
        
        taximetro = taximide4.Taximetro("password")
        taximetro.autenticar(self.root)
        self.assertTrue(taximetro.autenticado)
    
    @patch.object(taximide4, 'CustomPasswordDialog')
    def test_autenticar_incorrectamente(self, MockCustomPasswordDialog):
        # Configurar el mock para devolver una contraseña incorrecta
        mock_dialog = MagicMock()
        mock_dialog.result = "incorrect_password"
        MockCustomPasswordDialog.return_value = mock_dialog
        
        taximetro = taximide4.Taximetro("password")
        taximetro.autenticar(self.root)
        self.assertFalse(taximetro.autenticado)
    
    def test_validate_password(self):
        taximetro = taximide4.Taximetro("password")
        self.assertTrue(taximetro.validate_password("valid_password1"))
        self.assertTrue(taximetro.validate_password("valid_password_2"))
        self.assertFalse(taximetro.validate_password("short"))
        self.assertFalse(taximetro.validate_password("invalid!"))
    
    # Ejemplo de cómo probar la configuración de tarifas
    @patch.object(tk.simpledialog, 'askstring')
    def test_configurar_tarifas(self, MockAskString):
        # Configurar el mock para devolver las tarifas ingresadas
        MockAskString.side_effect = ["0.03", "0.06"]
        
        taximetro = taximide4.Taximetro("password")
        taximetro.autenticado = True
        
        taximetro.configurar_tarifas()
        self.assertEqual(taximetro.tarifa_parado, 0.03)
        self.assertEqual(taximetro.tarifa_movimiento, 0.06)
    
    # Otros tests pueden ser agregados según las funcionalidades que desees probar
    
if __name__ == '__main__':
    unittest.main()

