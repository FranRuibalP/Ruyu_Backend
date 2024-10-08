# app.py (Flask API)
from flask import Flask, request, jsonify
import joblib  
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)
load_dotenv()

# Conección a MongoDB (Las credenciales de conexión se encuentran en el archivo .env)
client = MongoClient(os.getenv('MONGODB_URI'))
# Seleccionar la base de datos y la colección donde se subirá el JSON
db = client['Ruyu']

# Lista de géneros posibles
all_genres = [

    'Action', 'Adventure', 'Casual', 'Early Access', 'Education',
    'Free to Play', 'Indie','Massively Multiplayer', 'RPG', 'Racing', 'Simulation',
    'Sports', 'Strategy'
]

# Cargar el modelo de machine learning previamente entrenado
salesModel = joblib.load('models/model_best_stacking.pkl')
hitsModel = joblib.load('models/modelo_hits.pkl')

def extract_year_and_season(date_str):
    # Convertir la cadena de fecha a un objeto datetime
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    # Extraer el año
    year = date_obj.year

    # Determinar la temporada
    month = date_obj.month
    if month in [12, 1, 2]:
        season = 'Winter'
    elif month in [3, 4, 5]:
        season = 'Spring'
    elif month in [6, 7, 8]:
        season = 'Summer'
    elif month in [9, 10, 11]:
        season = 'Fall'
    else:
        season = 'Unknown'  # En caso de que el mes no sea válido

    return year, season

#RUTAS DE PREDICCIONES
@app.route('/predict-sales-model', methods=['POST'])
def predictSales():
   
    # Obtener los datos de la solicitud POST
    data = request.get_json()

    # Extraer los datos necesarios del JSON
    price = float(data.get('price'))
    reviews = int(data.get('reviews'))
    reviewScore = float(data.get('score'))
    if float(data.get('avgCopies')) == 0:
        avg_publisher_copies = 100
    else:
        avg_publisher_copies = float(data.get('avgCopies'))
    publishers = data.get('publisher')
    # Convertir la lista de géneros a un diccionario con 1s y 0s
    genres = {genre: (1 if genre in data.get('genres') else 0) for genre in all_genres}
    year, season = extract_year_and_season(data.get('releaseDate'))
    
    
    #Input que se entrega al modelo
    input_data = pd.DataFrame({
    'price': [price],
    'reviews': [reviews],
    'reviewScore': [reviewScore],
    'publishers': [publishers],
    'avg_publisher_copies': [avg_publisher_copies],
    'year': [year],
    'season': [season],
    **genres
    })

    ''' TESTS
    print(publishers)
    print(avg_publisher_copies)
    print(genres)
    '''
    
    # Realizar la predicción
    predicted_copies_sold = salesModel.predict(input_data)
    # Convertir el resultado a un tipo de datos básico
    predicted_copies_sold = predicted_copies_sold.tolist()
    # Devolver la predicción en formato JSON
    return jsonify({'sales': predicted_copies_sold})


@app.route('/predict-genres-model', methods=['GET'])
def predictGenres():
    #Datos obtenidos del modelo ya entrenado
    numbers = [5.00, 4.80, 4.57, 4.19, 4.19, 4.19, 3.71, 3.71, 3.43, 3.19, 3.00]
    return jsonify(numbers)


@app.route('/predict-hits-model', methods=['POST'])
def predictHits():
   
    # Obtener los datos de la solicitud POST
    data = request.get_json()

    # Extraer los datos necesarios del JSON
    price = float(data.get('price'))
    reviews = int(data.get('reviews'))
    reviewScore = float(data.get('score'))
    publishers = data.get('publisher')
    if float(data.get('avgCopies')) == 0:
        avg_publisher_copies = 100
    else:
        avg_publisher_copies = float(data.get('avgCopies'))
    
    # Convertir la lista de géneros a un diccionario con 1s y 0s
    genres = {genre: (1 if genre in data.get('genres') else 0) for genre in all_genres}
    year, season = extract_year_and_season(data.get('releaseDate'))
    
    #Input que se entrega al modelo
    input_data = pd.DataFrame({
    'price': [price],
    'reviews': [reviews],
    'reviewScore': [reviewScore],
    'publishers': [publishers],
    'avg_publisher_copies': [avg_publisher_copies],
    'year': [year],
    'season': [season],
    'years_since_release': [datetime.now().year - year],
    **genres
})
    
    # Realizar la predicción
    predicted_hits = hitsModel.predict_proba(input_data)
    # Convertir el resultado a un tipo de datos básico
    predicted_hits = predicted_hits.tolist()
    #print(predicted_hits)
    # Devolver la predicción en formato JSON
    return jsonify({'hits': predicted_hits})

#RUTAS MONGODB
@app.route('/publishers', methods=['GET'])
def getPublishers():
    collection = db['publishers']
    search_query = request.args.get('q', '')  
    limit = int(request.args.get('limit', 10))  # Límite de resultados (por defecto, 10)
    
    # Realiza la consulta de búsqueda en MongoDB, usando una expresión regular para coincidir con el término
    publishers_data = collection.find(
        {'publishers': {'$regex': search_query, '$options': 'i'}},  # Búsqueda insensible a mayúsculas/minúsculas
        {'_id': 0, 'publishers': 1, 'avg_publisher_copies': 1}  # Solo selecciona los campos necesarios
    ).limit(limit)
    
    publishers_list = list(publishers_data)  # Convierte los resultados a una lista
    return jsonify(publishers_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
