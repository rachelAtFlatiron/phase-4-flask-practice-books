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
@app.route('/authors/<int:id>', methods=["GET", "DELETE"])
def author_by_id(id):
    #get auth for get or delete
    auth = Author.query.filter_by(id=id).first()
    #error message
    if(not auth):
        return make_response({'message': f'Author {id} not found'}, 404)
    #get request 
    if(request.method == "GET"):
        return make_response(auth.to_dict(), 200)
    if(request.method == "DELETE"):
        db.session.delete(auth)
        db.session.commit()
        return make_response({}, 204)
        
@app.route('/books', methods=["POST", "GET"])
def all_books():
    if(request.method == "GET"):
        books = Book.query.all()
        if(not books):
            return make_response({':('}, 404)
        books_dict = [book.to_dict(rules=('-publisher', '-author')) for book in books]
        return make_response(books_dict, 200)
    if(request.method == "POST"):
        try:
            # get the data
            data = request.get_json()
            # create new book instance 
            new_book = Book(title=data.get('title'), page_count=data.get('page_count'), author_id=data.get('author_id'), publisher_id=data.get('publisher_id'))
            # add/commit book instance
            db.session.add(new_book)
            db.session.commit()
        except:
            return make_response({'message': 'something went wrong '}, 422)
        # return make_response
        #return make_response(new_book.to_dict(only=('id', 'title', 'page_count', 'author.name', 'publisher.name')), 201)
        return make_response({
            "id": new_book.id,
            "name": new_book.title,
            "page_count": new_book.page_count,
            "author_name": new_book.author.name, # :) 
            "publisher_name": new_book.publisher.name
        }, 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
