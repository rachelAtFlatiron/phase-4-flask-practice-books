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
class Book(db.Model, SerializerMixin):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    publisher_id = db.Column(db.Integer, db.ForeignKey("publishers.id"))

    author = db.relationship('Author', back_populates='books') #Author.books
    publisher = db.relationship('Publisher', back_populates='books')

    serialize_rules = ('-author.books', '-publisher.books')

    """
    {
        ...,
        author: {
            ...,
            books: [
                {
                    ...,
                    author: {
                        ...,
                        books: [
                            ...
                        ]
                    }
                }
            ]
        }
    }
    """

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "page_count": self.page_count,
            "author_name": self.author.name,
            "publisher_name": self.publisher.name
        }
    
    
    @validates('page_count')
    def validate_page(self, key, value):
        if value <= 0:
            raise ValueError('pages must be greater than 0')
        else:
            return value 
        
    def __repr__(self):
        return f'<Book id={self.id} title={self.title} author={self.author.name} />'
        
class Publisher(db.Model, SerializerMixin):
    __tablename__ = "publishers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False)

    books = db.relationship('Book', back_populates='publisher')

    # Publisher.books -> Book.author -> author instance
    # books -> author
    authors = association_proxy('books', 'author')

    serialize_rules = ('-books.publisher', )

    @validates("founding_year")
    def validate_year(self, key, value):
        if 1600 <= value <= 2024:
            return value 
        else:
            raise ValueError("year is bad")

    def __repr__(self):
        return f'<Publisher id={self.id} name={self.name} />'

class Author(db.Model, SerializerMixin):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    books = db.relationship('Book', back_populates='author')  #Book.author

    publishers = association_proxy('books', 'publisher')

    serialize_rules = ('-books.author', )

    def __repr__(self):
        return f'<Author id={self.id} name={self.name} />'
  