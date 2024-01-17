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

class AuthorRoutes(Resource):
    def get(self, id):
        author = Author.query.get(id)
        if author:
            return make_response({
                'id': author.id,
                'name': author.name,
                'pen_name': author.pen_name,
                'books': [
                    book.to_dict() for book in author.books
                ]
            }, 200)
        else:
            make_response({
                'error': 'Author not found'
            }, 404)
    
    def delete(self, id):
        author = Author.query.get(id)
        if not author:
            return make_response({'error': 'Author not found'}, 404)
        db.session.delete(author)
        db.session.commit()
        return make_response({}, 204)

@app.get('/books')
def all_books():
    try:
        books = Book.query.all()
        return make_response([
            book.to_dict() for book in books
        ], 200)
    except Exception:
        return make_response({'error': 'something went wrong'}, 404)

@app.post('/books')
def post_book():
    try: 
        data = request.get_json() 
        new_book = Book(title=data['title'], 
                        page_count=data['page_count'], 
                        author_id=data['author_id'], 
                        publisher_id=data['publisher_id']
                    )
        db.session.add(new_book)
        db.session.commit()
        return make_response(new_book.to_dict(), 201)
    except Exception:
        return make_response({'error': Exception.with_traceback}, 406)
    
@app.get('/publishers/<int:id>')
def one_publisher(id):
    pub = Publisher.query.get(id)
    if not pub:
        return make_response({'error': 'pub not found'}, 404)
    return make_response({
        'id': pub.id,
        'name': pub.name,
        'founding_year': pub.founding_year,
        'authors': [
            book.author.to_dict(rules=('-books',)) for book in pub.books
        ]
    }, 200)

# write your routes here!
api.add_resource(AuthorRoutes, '/authors/<int:id>')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
