
# Ruyu

Este documento es correspondiente al frontend y backend del sitio web del proyecto final de ingeniería realizado por los alumnos Francisco Ruibal Palacio y Matías Fernando Yuan en al año 2024.

El siguiente instructivo tiene como objetivo explicar como inicializar tanto el frontend como el backend de manera local.

## Requerimientos Previos
Se asume que se utiliza windows como sistema operativo.

Para el correcto funcionamiento, se debe instalar previamente las ultimas versiones de Node.js y Python. Se pueden encontrar a continuación:
 - [Node.js](https://nodejs.org/en/download/prebuilt-installer)
 - [Python](https://www.python.org/downloads/)

## Instalación

Clonar el proyecto desde Github, o descargarlo en formato zip, y extraerlo en la computadora.

### Frontend

Dentro de la carpeta /Client ejecutar el siguiente comando en una terminal para instalar dependencias:

```bash
  npm i
```

Una vez instaladas las dependencias, el entorno se puede iniciar mediante:

```bash
  npm run dev
```
Una vez iniciado, se puede ingresar introduciendo el siguiente link en el navegador web:

http://localhost:3000/

### Backend
Dentro de la carpeta /ml-api, crear un entorno de python para poder ejecutar los comandos. para ello, abrir una terminal y escribir lo siguiente:
```bash
  py -3 -m venv .venv
```
Luego se activa el entorno con el siguiente comando:

```bash
  .venv\Scripts\activate
```

Dentro de la carpeta /ml-api ejecutar los siguientes comandos en una terminal para instalar dependencias:

```bash
  pip install flask
```
```bash
  pip install joblib
```
```bash
  pip install flask_cors
```
```bash
  pip install pandas
```
```bash
  pip install pymongo
```
```bash
  pip install python_dotenv
```
```bash
  pip install scikit_learn
```
```bash
  pip install xgboost
```
Finalmente, para inicializar el backend, ejecutar el sigiente comando:

```bash
  py app.py

```
Con ambos entornos iniciados, ya se puede utilizar la aplicacion con todas sus funcionalidades.

Para finalizar los procesos, en cada terminal se deben oprimir las teclas Ctrl+C. Se podrá ver en la terminal que el proceso finaliza.




