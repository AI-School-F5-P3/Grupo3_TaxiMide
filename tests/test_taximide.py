import unittest  # Importar el módulo de unittest para escribir pruebas unitarias
import tkinter as tk  # Importar tkinter para simular interfaces gráficas de usuario
from taximide import Taximetro  # Importar la clase Taximetro que se va a probar (ajustar nombre si es diferente)

class TestTaximetro(unittest.TestCase): # clase base para definir las pruebas unitarias
    """
    Clase que contiene las pruebas unitarias para la clase Taximetro.
    """

    def setUp(self): # El método setUp se ejecuta antes de cada prueba para inicializar objetos necesarios como la ventana Tkinter (self.root), la contraseña de prueba y la instancia del Taximetro
        """
        Configuración inicial que se ejecuta antes de cada prueba.
        """
        self.root = tk.Tk()  # Crea una nueva instancia de la clase Tk del módulo tkinter, que representa una ventana de la interfaz gráfica Tkinter. Esta ventana será utilizada en las pruebas que necesiten interactuar con elementos de la interfaz gráfica.
        self.contraseña = "test123"  # Define una contraseña de prueba. Este valor se utilizará en las pruebas que necesiten autenticación o validación de contraseña.
        self.taximetro = Taximetro(self.contraseña, self.root)  # Crea una instancia del objeto Taximetro utilizando la contraseña de prueba y la ventana Tkinter creada anteriormente (self.root).

    def tearDown(self):
        """
        Limpieza que se ejecuta después de cada prueba (no realiza ninguna acción específica aquí, ya que está definido como pass).
        """
        pass
    #setUp y tearDown son métodos especiales en el contexto de las pruebas unitarias que se utilizan para la inicialización y la limpieza, respectivamente, antes y después de cada prueba. Esto facilita la creación de pruebas más robustas y mantenibles en entornos de desarrollo en Python.
                    

    def test_start_movement(self):
        """
        Prueba para iniciar el movimiento, simulando un estado inexistente (del self.taximetro.estado_label). Al no existir el atributo estado_label se asegura que se lance AttributeError. Esto es importante para asegurar que el código tenga un manejo adecuado de errores y sea robusto frente a situaciones inesperadas.
        """
        del self.taximetro.estado_label  # Se elimina el atributo estado_label del objeto taximetro para simular una situación en la que este atributo no existe. Esto se hace para verificar cómo el método iniciar_movimiento maneja la ausencia de este atributo.
        
        with self.assertRaises(AttributeError):  # Esto indica que la prueba espera que se lance una excepción AttributeError cuando se llame al método iniciar_movimiento. Si la excepción no se lanza, la prueba falla.
            self.taximetro.iniciar_movimiento()

    def test_stop_movement(self):
        """
        Prueba para detener el movimiento, y verifica que el método detener_movimiento en la clase taximetro establece correctamente el atributo en_movimiento a False, indicando que el movimiento se ha detenido. Esto asegura que la funcionalidad para detener el movimiento funciona como se espera y que el estado del objeto taximetro se actualiza adecuadamente..
        """
        self.taximetro.detener_movimiento() # Se llama al método detener_movimiento del objeto taximetro. Este método está diseñado para detener cualquier movimiento en curso y establecer el estado correspondiente en el objeto taximetro.
        self.assertFalse(self.taximetro.en_movimiento)  # Después de detener el movimiento, se verifica que el atributo en_movimiento del objeto taximetro sea False. self.assertFalse es un método proporcionado por unittest.TestCase que asegura que la expresión pasada como argumento sea False. Si self.taximetro.en_movimiento no es False, la prueba fallará.

    def test_configure_tariffs(self):
        """
        Prueba para configurar las tarifas, y verifica que se lance TypeError al intentar configurar con argumentos incorrectos.
        """
        # Uso de assertRaises para Capturar TypeError:
        with self.assertRaises(TypeError):  # self.assertRaises es un método proporcionado por unittest.TestCase que se utiliza para verificar que se lance una excepción específica durante la ejecución de un bloque de código. En este caso, se espera que se lance un TypeError.
            # Llamada al Método configurar_tarifas:
            self.taximetro.configurar_tarifas(new_idle_rate=0.03, new_movement_rate=0.06) # Dentro del bloque with, se llama al método configurar_tarifas del objeto taximetro con argumentos específicos: new_idle_rate=0.03 y new_movement_rate=0.06. La prueba asume que estos argumentos son incorrectos y deberían causar que el método lance un TypeError.

    def test_reset_values(self): # La función test_reset_values es una prueba unitaria. Está diseñada para ejecutarse dentro de un marco de pruebas unitarias, como unittest en Python. El self se refiere a la instancia de la clase de prueba.
        """
        Prueba para resetear los valores, y verifica que se lance AttributeError al intentar resetear.
        """
        with self.assertRaises(AttributeError):  # Este bloque with se usa para verificar que el código dentro de él genere una excepción específica, en este caso, un AttributeError. La prueba fallará si el AttributeError no se lanza.
            self.taximetro.resetear_valores() # Dentro del bloque with, se llama al método resetear_valores de la instancia taximetro. Si esta llamada genera un AttributeError, la prueba pasará. Si no genera dicha excepción, la prueba fallará.

    def test_verify_password_with_correct_password(self):
        """
        Prueba para verificar el comportamiento del método verify_password cuando se le proporciona una contraseña correcta.
        """
        self.assertTrue(self.taximetro.verify_password(self.contraseña)) # assertTrue es un método de aserción que pertenece al framework de pruebas (unittest). Este método verifica si la expresión dada (self.taximetro.verify_password(self.contraseña)) es verdadera. En este contexto, espera que self.taximetro.verify_password(self.contraseña) devuelva True cuando se le pase la contraseña correcta (self.contraseña). verify_password es un método que verifica si la contraseña proporcionada coincide con la contraseña almacenada o esperada en self.taximetro.

    def test_verify_password_with_incorrect_password(self):
        """
        Prueba para verificar el comportamiento del método verify_password cuando se le pasa una contraseña incorrecta ("incorrecta" en este caso).
        """
        self.assertFalse(self.taximetro.verify_password("incorrecta")) # assertFalse es un método de aserción que también pertenece al framework de pruebas (unittest). Este método verifica si la expresión dada (self.taximetro.verify_password("incorrecta")) es falsa. En este contexto, espera que self.taximetro.verify_password("incorrecta") devuelva False cuando se le pase la contraseña incorrecta "incorrecta". verify_password es el método que verifica si la contraseña proporcionada coincide con la contraseña almacenada o esperada en self.taximetro.

if __name__ == "__main__": # Se asegura de que las pruebas se ejecuten solo si este script se ejecuta directamente, no si se importa como módulo. 
    unittest.main() # ejecuta todas las pruebas definidas en la clase TestTaximetro.