import contextlib
import io
import json
import unittest
from demo import (Personaje, MARCA, LIMITE, generar_entrada,
                  importar_vulnerable, importar_mitigado)


class PruebasDemo(unittest.TestCase):
    def test_legitimos_equivalentes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            vulnerable = importar_vulnerable(generar_entrada('vulnerable', 'legitimo'))
        mitigado = importar_mitigado(generar_entrada('mitigado', 'legitimo'))
        self.assertEqual(vulnerable, mitigado)
        self.assertEqual(mitigado, Personaje('Juan', 8, 75))

    def test_efecto_antes_del_rechazo(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            datos = generar_entrada('vulnerable', 'manipulado')
        self.assertEqual(salida.getvalue(), '')  # Serializar no ejecuta print.
        with contextlib.redirect_stdout(salida), self.assertRaises(ValueError):
            importar_vulnerable(datos)
        texto = salida.getvalue()
        self.assertLess(texto.index('[1]'), texto.index(MARCA))
        self.assertLess(texto.index(MARCA), texto.index('[2]'))

    def test_mitigado_rechaza_sin_efecto(self):
        for caso in ['malformado', 'manipulado', 'invalido', 'pickle']:
            with self.subTest(caso=caso):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida), self.assertRaises(ValueError):
                    importar_mitigado(generar_entrada('mitigado', caso))
                self.assertNotIn(MARCA, salida.getvalue())

    def test_texto_no_se_ejecuta(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            personaje = importar_mitigado(generar_entrada('mitigado', 'texto'))
        self.assertEqual(personaje.nombre, 'print("HOLA")')
        self.assertEqual(salida.getvalue(), '')

    def test_limite_y_esquema(self):
        entradas = [b' ' * (LIMITE + 1), b'[]', b'{}']
        for campo, valor in [('nivel', True), ('vida', 101), ('nombre', '  '), ('nivel', '8')]:
            datos = {'nombre': 'Juan', 'nivel': 8, 'vida': 75}
            datos[campo] = valor
            entradas.append(json.dumps(datos).encode())
        for entrada in entradas:
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                importar_mitigado(entrada)


if __name__ == '__main__':
    unittest.main()
