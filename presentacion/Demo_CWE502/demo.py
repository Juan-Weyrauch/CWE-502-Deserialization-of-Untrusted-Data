"""Laboratorio local CWE-502."""
import argparse
import json
import pickle
from dataclasses import dataclass

LIMITE = 4096
MARCA = '[INESPERADO] Se llamo a print DURANTE la deserializacion.'


@dataclass
class Personaje:
    nombre: str
    nivel: int
    vida: int


class EntradaPreparada:
    def __reduce__(self):
        # Al SERIALIZAR se describe una llamada; print no se ejecuta aqui.
        # Al DESERIALIZAR, pickle ejecutara print con este argumento.
        return (print, (MARCA,))


def importar_vulnerable(datos):
    print('[1] Antes de pickle.loads')
    objeto = pickle.loads(datos)  # PUNTO VULNERABLE si la entrada no es confiable.
    print('[2] Despues de pickle.loads')
    # La comprobacion posterior no evita la llamada ya realizada.
    if type(objeto) is not Personaje:
        raise ValueError('Tipo rechazado, pero el efecto ya pudo ocurrir.')
    return objeto


def importar_mitigado(datos):
    if len(datos) > LIMITE:
        raise ValueError('Entrada mayor a 4096 bytes.')
    try:
        valores = json.loads(datos.decode('utf-8'))
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise ValueError('Se requiere JSON valido en UTF-8.') from exc
    
    if type(valores) is not dict or set(valores) != {'nombre', 'nivel', 'vida'}:
        raise ValueError('Se requieren exactamente {nombre, nivel y vida}.')
    
    nombre, nivel, vida = valores['nombre'], valores['nivel'], valores['vida']
    if type(nombre) is not str or not 1 <= len(nombre.strip()) <= 40:
        raise ValueError('Nombre: debe ser texto no vacio de hasta 40 caracteres.')
    
    # type(...) is int rechaza tambien booleanos, que en Python heredan de int.
    if type(nivel) is not int or not 1 <= nivel <= 100:
        raise ValueError('Nivel: debe ser entero entre 1 y 100.')
    
    if type(vida) is not int or not 0 <= vida <= 100:
        raise ValueError('Vida: debe ser entero entre 0 y 100.')
    
    # Los datos no eligen clases ni funciones: la aplicacion decide la construccion.
    return Personaje(nombre.strip(), nivel, vida)


def generar_entrada(version, caso):
    valores = {'nombre': 'Juan', 'nivel': 8, 'vida': 75}
    
    if caso == 'malformado':
        return b'{entrada rota'
    
    if version == 'vulnerable':
        objeto = (
            Personaje(**valores)
            if caso == 'legitimo'
            else EntradaPreparada()
        )

        return pickle.dumps(objeto, protocol=4)
    
    if caso == 'manipulado':
        valores['funcion'] = 'print'
        
    elif caso == 'invalido':
        valores['vida'] = -20
        
    elif caso == 'texto':
        valores['nombre'] = 'print("HOLA")'
        
    elif caso == 'pickle':
        return pickle.dumps(EntradaPreparada(), protocol=4)
    
    return json.dumps(valores).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'version', choices=['vulnerable', 'mitigado'])
    parser.add_argument(
        'caso', choices=['legitimo', 'malformado', 'manipulado', 'invalido', 'texto', 'pickle'])
    
    args = parser.parse_args()
    if args.version == 'vulnerable' and args.caso not in {'legitimo', 'malformado', 'manipulado'}:
        parser.error('Para vulnerable: legitimo, malformado o manipulado.')
        
    # El generador representa al emisor externo en este laboratorio autocontenido.
    # El importador recibe solo bytes; no recibe el nombre del caso.
    datos = generar_entrada(args.version, args.caso)
    importar = importar_vulnerable if args.version == 'vulnerable' else importar_mitigado
    try:
        print('ACEPTADO:', importar(datos))
    except (ValueError, pickle.UnpicklingError, EOFError) as exc:
        print('RECHAZADO:', exc)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
