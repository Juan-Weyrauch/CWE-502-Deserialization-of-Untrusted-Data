# Demo CWE-502

Programa por consola que importa un personaje con nombre, nivel y vida. Compara una versión vulnerable con `pickle` y una mitigada con JSON y validación de datos.

El propio programa genera las entradas de prueba en memoria. No hay que cargar archivos ni iniciar un servidor.

## Cómo ejecutarlo

Requiere Python 3. Probado en Windows con Python 3.14.5. No necesita instalar paquetes.

Extraé el ZIP y abrí PowerShell en la carpeta que contiene `demo.py` y `test_demo.py`. Cada ejecución tiene esta forma:

```powershell
py demo.py VERSION CASO
```

## Opciones de ejecución

| Comando | Qué prueba | Resultado esperado |
|---|---|---|
| `py demo.py vulnerable legitimo` | Un personaje serializado con pickle. | Acepta a Juan con nivel 8 y vida 75. |
| `py demo.py vulnerable manipulado` | Una entrada preparada para llamar a `print` durante la deserialización. | Muestra `[EFECTO]` entre `[1]` y `[2]`. Después rechaza el resultado por su tipo. |
| `py demo.py vulnerable malformado` | Bytes que no forman un pickle válido. | Rechaza la entrada por formato incorrecto. |
| `py demo.py mitigado legitimo` | Los datos del personaje en JSON. | Acepta a Juan con nivel 8 y vida 75. |
| `py demo.py mitigado manipulado` | JSON con un campo adicional llamado `funcion`. | Rechaza la entrada porque solo permite nombre, nivel y vida. |
| `py demo.py mitigado invalido` | JSON válido, pero con vida igual a -20. | Rechaza el valor fuera de rango. |
| `py demo.py mitigado texto` | El nombre contiene el texto `print("HOLA")`. | Acepta ese nombre como texto, sin ejecutarlo. |
| `py demo.py mitigado pickle` | La entrada pickle preparada, entregada al lector JSON. | Rechaza el formato sin mostrar `[EFECTO]`. |
| `py demo.py mitigado malformado` | Texto que no forma un JSON válido. | Rechaza la entrada por formato incorrecto. |
| `py -m unittest -v` | Ejecuta las cinco pruebas automatizadas. | Termina con `Ran 5 tests` y `OK`. |
| `py demo.py --help` | Muestra la ayuda del programa. | Lista los argumentos disponibles. |

Usá las combinaciones de la tabla: `invalido`, `texto` y `pickle` solo están disponibles en la versión mitigada.

## Qué hace cada versión

**Vulnerable:** llama a `pickle.loads` y después comprueba el tipo del resultado. La entrada preparada ejecuta `print` dentro de esa llamada. El rechazo posterior no deshace el efecto.

**Mitigada:** limita la entrada a 4096 bytes, lee JSON, comprueba los campos y crea el personaje desde el código de la aplicación.

| Campo | Regla |
|---|---|
| `nombre` | Texto de 1 a 40 caracteres después de quitar espacios de los extremos. |
| `nivel` | Entero entre 1 y 100. No acepta booleanos. |
| `vida` | Entero entre 0 y 100. No acepta booleanos. |

Los 4096 bytes (4 KiB) son un límite elegido para esta demo, no una exigencia del formato. Se comprueban antes de interpretar el JSON, cuando los bytes ya están en memoria.

## Notas de uso

- `ACEPTADO` indica que el importador devolvió un personaje. `RECHAZADO` indica que detectó un error; en los casos negativos es el resultado esperado.
- En `mitigado texto`, ver `print("HOLA")` dentro del nombre no significa que se haya ejecutado.
- Si no encuentra `demo.py`, revisá la carpeta actual con `dir`. Si no reconoce `py`, probá `python`.
- Cada comando termina solo. No hay un servicio que detener.
- Usá únicamente las entradas incluidas: no cargues archivos pickle de terceros en la versión vulnerable.
