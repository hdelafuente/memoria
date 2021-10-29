# Memoria Hugo de la Fuente

Memoria para optar al título de ingeniero civil en ciencias de la computación, este repositorio compone todo lo desarrollado para la ejecución de la memoria.

## Instalación

Primero debemos tener instalado Ta-Lib (MacOS):

```
$ brew install ta-lib
```

Segundo instalamos las dependencias del proyecto usando pip en un ambiente virtual de python

```
$ python3 -m venv .env/
$ pip install -r requirements.txt
```

## Uso

Para hacer backtests primero debemos extraer información de las últimas noticias corriendo el archivo `data_extractor.py `, el proceso puede tardar varios minutos, paciencia....

Luego creamos la carpeta `data` (el extractor debería hacerlo por su cuenta) y movemos el archivo csv generado a esta carpeta con el nombre `test.csv`

Finalmente corremos el proyecto para ver los resultados, para ello usamos:

```
(.env) ~/memoria $ python3 main.py
```

> **Importante**: El ambiente virtual debe estar activo todo el tiempo
