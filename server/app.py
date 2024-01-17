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


# write your routes here!
api.add_resource(AuthorRoutes, '/authors/<int:id>')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
