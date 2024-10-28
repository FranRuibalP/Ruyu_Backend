# app.py (Flask API)
from flask import Flask, request, jsonify
import joblib  
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json


app = Flask(__name__)
CORS(app)
load_dotenv()

# Conección a MongoDB (Las credenciales de conexión se encuentran en el archivo .env)
client = MongoClient(os.getenv('MONGODB_URI'))

db = client['Ruyu']


all_genres = [

    'Action', 'Adventure', 'Casual', 'Early Access', 'Education',
    'Free to Play', 'Indie','Massively Multiplayer', 'RPG', 'Racing', 'Simulation',
    'Sports', 'Strategy'
]

file_path = os.path.join("models", "defuzzified_popularity.json")

# Cargar el modelo de machine learning previamente entrenado
salesModel = joblib.load('models/model_best_stacking.pkl')
hitsModel = joblib.load('models/modelo_hits.pkl')



def extract_year_and_season(date_str):
    
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    year = date_obj.year

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
   
    data = request.get_json()

    price = float(data.get('price'))
    reviews = int(data.get('reviews'))
    reviewScore = float(data.get('score'))
    if float(data.get('avgCopies')) == 0:
        avg_publisher_copies = 100
    else:
        avg_publisher_copies = float(data.get('avgCopies'))
    publishers = data.get('publisher')
    
    genres = {genre: (1 if genre in data.get('genres') else 0) for genre in all_genres}
    year, season = extract_year_and_season(data.get('releaseDate'))
    
    
    
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
    predicted_copies_sold = predicted_copies_sold.tolist()
    # Devolver la predicción en formato JSON
    return jsonify({'sales': predicted_copies_sold})


@app.route('/predict-genres-model', methods=['GET'])
def predictGenres():
    
    with open(file_path, "r") as file:
        data = file.read()
        #print(data)
    
    return jsonify(data)


@app.route('/predict-hits-model', methods=['POST'])
def predictHits():
   
    data = request.get_json()

    price = float(data.get('price'))
    reviews = int(data.get('reviews'))
    reviewScore = float(data.get('score'))
    publishers = data.get('publisher')
    if float(data.get('avgCopies')) == 0:
        avg_publisher_copies = 100
    else:
        avg_publisher_copies = float(data.get('avgCopies'))
    
    genres = {genre: (1 if genre in data.get('genres') else 0) for genre in all_genres}
    year, season = extract_year_and_season(data.get('releaseDate'))
    
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
    predicted_hits = predicted_hits.tolist()
    #print(predicted_hits)
    # Devolver la predicción en formato JSON
    return jsonify({'hits': predicted_hits})
#RUTA DE TESTEO
@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello World!'
#RUTAS MONGODB
@app.route('/publishers', methods=['GET'])
def getPublishers():
    collection = db['publishers']
    search_query = request.args.get('q', '')  
    limit = int(request.args.get('limit', 10))  
    
    
    publishers_data = collection.find(
        {'publishers': {'$regex': search_query, '$options': 'i'}},  
        {'_id': 0, 'publishers': 1, 'avg_publisher_copies': 1}  
    ).limit(limit)
    
    publishers_list = list(publishers_data) 
    return jsonify(publishers_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
