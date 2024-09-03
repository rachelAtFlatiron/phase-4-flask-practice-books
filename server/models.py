from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# write your models here!
class Author(db.Model, SerializerMixin):
    __tablename__ = "authors"
    #constraints will run when you try to add them to the database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    bibliography = db.relationship('Book', back_populates='author')
    publishers = association_proxy('bibliography', 'publisher')

    serialize_rules=('-bibliography.author', '-bibliography.publisher')

    def __repr__(self):
        return f'<Author {self.id} {self.name} >'

class Publisher(db.Model, SerializerMixin):
    __tablename__ = "publishers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False)

    book_list = db.relationship('Book', back_populates='publisher')
    authors = association_proxy('book_list', 'author')
    #1600 <= founding_year <= 2024, validation
    #validations will run when you first create the instance
    @validates('founding_year')
    def validate_year(self, key, user_value):
        if(1600 <= user_value <= 2024):
            return user_value 
        raise ValueError('founding year must be between 1600 and 2024')

    serialize_rules = ('-book_list.publisher', )
    def __repr__(self):
        return f'<Publisher {self.id} {self.name} >' 

class Book(db.Model, SerializerMixin):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer, nullable=False)

    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    publisher = db.relationship('Publisher', back_populates='book_list')
    author = db.relationship('Author', back_populates='bibliography')
    #page_count > 0, validation 
    @validates('page_count')
    def validate_page(self, key, user_value):
        if(user_value > 0):
            return user_value 
        raise ValueError('page count must be greater than 0')

    serialize_rules=('-publisher.book_list', '-author.bibliography')

    def __repr__(self):
        return f'<Book {self.id} {self.title}>'
