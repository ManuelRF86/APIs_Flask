from flask import Flask, request, jsonify
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd
import sqlite3
from os import environ

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
app = Flask(__name__)


def create_database():
    df = pd.read_csv('data/advertising.csv')
    conn = sqlite3.connect('data/advertising_database.db')
    df.to_sql('advertising_database', conn, index=False, if_exists='replace')
    conn.close()


@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"
    
@app.route('/predict', methods=['GET'])
def predict():

    model = pickle.load(open('./data/advertising_model','rb'))
    data = request.get_json()

    valores = data['data'][0]
    tv, radio, newspaper = map(int, valores)

    prediction = model.predict([[tv, radio, newspaper]])
    return jsonify({'prediction': round(prediction[0], 2)})
    
   
    
@app.route('/ingest', methods=['POST'])
def test_ingest_endpoint():

    data = request.json

    if 'data' not in data or not isinstance(data['data'], list):
        return "JSON no válido"


    conn = sqlite3.connect('data/advertising_database.db')
    cursor = conn.cursor()

    for valor in data['data']:
        if len(valor) != 4:
            return "erro, introduzca 4 valores"
        
        cursor.execute("INSERT INTO advertising_database (tv, radio, newpaper, sales) VALUES (?, ?, ?, ?)",
                       (valor[0], valor[1], valor[2], valor[3]))


    conn.commit()
    conn.close()

    return {'message': 'Datos ingresados correctamente'}




@app.route('/retrain', methods=['POST'])
def test_retrain_endpoint():
    # Conectar a la base de datos y cargar los datos
    conn = sqlite3.connect('data/advertising_database.db')
    query = "SELECT * FROM advertising_database"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Separar las características (X) y la variable objetivo (y)
    X = df[['TV', 'radio', 'newpaper']]
    y = df['sales']

    # Dividir los datos en conjuntos de entrenamiento y prueba
    

    # Crear y entrenar el modelo
    model = LinearRegression()
    model.fit(X, y)

    with open('data/advertising_model', 'wb') as file:
        pickle.dump(model, file)

    return {'message': 'Modelo reentrenado correctamente.'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)