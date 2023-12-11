# import json
from flask import Flask, request, jsonify
import sqlite3
import os

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config["DEBUG"] = True




@app.route('/', methods=['GET'])
def welcome():
    return "Welcome to mi API conected to my books database"

# 0.Ruta para obtener todos los libros

@app.route('/get_all_books', methods=['GET'])
def get_all_books():
    
    #conectarme a la base de datos
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    books_json = []
    for book in books:
        book_dict = {
            'id': book[0],  # Ajusta los índices según tu esquema
            'published': book[1],
            'author': book[2],
            'title': book[3],
            'first_sentence': book[4]
            # Agrega más campos según tu esquema
        }
        books_json.append(book_dict)

    return books_json


# 1.Ruta para obtener el conteo de libros por autor ordenados de forma descendente

@app.route('/get__number_books_by_author', methods=['GET'])
def get_number_books_by_author():
    # Conectar a la base de datos
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT author, COUNT(*) as book_count FROM books GROUP BY author ORDER BY book_count DESC')
    books = cursor.fetchall()
    conn.close()

    # Convertir los resultados a un formato JSON
    result_json = [{'author': author, 'book_count': book_count} for author, book_count in books]

    return jsonify(result_json)

# 2.Ruta para obtener los libros de un autor como argumento en la llamada
@app.route('/get_books_author', methods=['GET'])
def get_books_author():
    # Conectar a la base de datos
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    author = request.args['author']
    results = [book for book in books if book[2] == author]

    return results

# 3.Ruta para obtener los libros filtrados por título, publicación y autor
@app.route('/get_books_params', methods=['GET'])
def get_books_params():
    # Conectar a la base de datos
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    author = request.args.get('author')
    published = request.args.get('published')
    title = request.args.get('title')

    # Filtrar libros según los parámetros
    results = []

    for book in books:
        if (author is None or book[2] == author) and \
           (published is None or book[1] == int(published)) and \
           (title is None or book[3] == title):
            results.append({
                'id': book[0],
                'published': book[1],
                'author': book[2],
                'title': book[3],
                'first_sentence': book[4]
                # Agrega más campos según tu esquema
            })

    return jsonify(results)

app.run()