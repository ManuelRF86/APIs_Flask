from flask import Flask, request, jsonify
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd
import sqlite3

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

def create_database():
    df = pd.read_csv('ejercicio/data/advertising.csv')
    conn = sqlite3.connect('data/advertising_database.db')
    df.to_sql('advertising_database', conn, index=False, if_exists='replace')
    conn.close()

if not os.path.exists('data/advertising_database.db'):
    create_database()




@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"
    
@app.route('/v2/predict', methods=['GET'])
def predict():
    # Conectar a la base de datos
    conn = sqlite3.connect('data/advertising_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM advertising_database')
    advertising = cursor.fetchall()
    conn.close()

    model = pickle.load(open('data/advertising_model','rb'))

    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newpaper = request.args.get('newpaper', None)

    if tv is None or radio is None or newpaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[int(tv),int(radio),int(newpaper)]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'
    
@app.route('/v2/ingest_data', methods=['POST'])
def add_news():

    data = request.get_json()

    # Conectar a la base de datos
    conn = sqlite3.connect('data/advertising_database.db')
    cursor = conn.cursor()

    # Utiliza parámetros de marcadores de posición (?) para evitar SQL injection
    cursor.execute("INSERT INTO advertising_database (tv, radio, newpaper, sales) VALUES (?, ?, ?, ?)",
                       (data['tv'], data['radio'], data['newpaper'], data['sales']))

    conn.commit()
    conn.close()

    return "Nuevo registro introducido"




@app.route('/v2/retrain', methods=['POST'])
def retrain():
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

    return "Modelo reentrenado exitosamente"

app.run()