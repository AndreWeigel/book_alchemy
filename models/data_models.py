from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        end_date = self.date_of_death if self.date_of_death else "present"
        return f"{self.name} ({self.date_of_birth} - {end_date})"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    isbn = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)