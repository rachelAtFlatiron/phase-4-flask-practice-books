#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate

from models import db, Author, Book, Publisher # import your models here!

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.get('/')
def index():
    return "Hello world"

# write your routes here!
@app.get('/authors/<int:id>')
def one_author(id):
    try:
        author = Author.query.get(id)
        if not author:
            return make_response({
                'error': 'not found'
            }, 404)
        else:
            # return make_response({
            #     "id": author.id,
            #     "name": author.name,
            #     "pen_name": author.pen_name, 
            #     "books": [
            #         book.to_dict() for book in author.books
            #     ]
            # }, 200)
        
            return make_response({
                **author.to_dict(), #unpacking key/values
                # "books": [ #overwriting the books key/value
                #     book.to_dict() for book in author.books
                # ]
            }, 200)
        
    except Exception:
        return make_response({
            'error': 'something went wrong'
        }, 500)

@app.delete('/authors/<int:id>')
def delete_author(id):
    try:
        author = Author.query.get(id)
        if not author:
            return make_response({'error': 'not found'}, 404)
        db.session.delete(author)
        db.session.commit()
        return make_response({}, 204)
    except Exception:
        return make_response({'error': 'something went wront'}, 500)
    
@app.get('/books')
def all_books():
    try:
        books = Book.query.all()
        if not books:
            return make_response({'error': 'books not found'}, 404)
        return make_response([book.to_dict() for book in books], 200)
    except Exception: 
        return make_response({'error': Exception.__traceback__}, 500)

@app.post('/books')
def create_book():
    try: 
        data = request.get_json()
        #create class instance of book
        new_book = Book(
            title=data['title'],
            page_count=data['page_count'],
            author_id=data["author_id"],
            publisher_id=data["publisher_id"]
        )
        db.session.add(new_book)
        db.session.commit()

        return make_response(new_book.to_dict(), 201)
    except Exception:
        return make_response({'error': Exception.__traceback__}, 500)
    
@app.get('/publishers/<int:id>')
def get_publisher(id):
    pub = Publisher.query.get(id)
    if not pub: 
        return make_response({
            'error': 'not found'
        }, 404)
    else:
        return make_response({
            **pub.to_dict(rules=('-books', )), # destructuring pub's key/value pairs
            # -books scraps the entire books list

            #putting back in an authors list that is based on pub.books
            'authors': [
                {
                    'id': book.author.id,
                    'name': book.author.name,
                    'pen_name': book.author.pen_name
                } for book in pub.books
            ]
        }, 200)

        
if __name__ == '__main__':
    app.run(port=5555, debug=True)
