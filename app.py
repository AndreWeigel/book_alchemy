import os

from flask import Flask, render_template, request, flash, redirect, url_for
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import jinja2

from datetime import datetime
from models.data_models import db, Author, Book


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}"
app.config['SECRET_KEY'] = 'your-secure-key-here'
db.init_app(app)

with app.app_context():
  db.create_all()


@app.route('/home', methods=['GET'])
def home():

    #Get books
    books = Book.query.all()
    authors = Author.query.all()

    return render_template('home.html', books=books, authors=authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        birthdate_str = request.form.get('birthdate', '').strip()
        date_of_death_str = request.form.get('date_of_death', '').strip()
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d") if birthdate_str else None
        date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d") if date_of_death_str else None

        author = Author(name=name,
                        date_of_birth=birthdate,
                        date_of_death=date_of_death)

        # Create a new blog post and add it
        if author:
            db.session.add(author)
            db.session.commit()

            flash('Author successfully added!')
        else:
            flash('Error adding post. Please try again.')

        return redirect(url_for('home'))
    # Render the form for GET requests
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        author_name = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publication_year = request.form.get('publication_year', '').strip()

        # Look for the author in the database
        author = Author.query.filter_by(name=author_name).first()

        # Create new author if necessary
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        book = Book(title=title,
                        author_id=author.id,
                        isbn=isbn,
                    publication_year = int(publication_year))

        # Create a new blog post and add it
        if book:
            db.session.add(book)
            db.session.commit()

            flash('Book successfully added!')
        else:
            flash('Error adding post. Please try again.')

        return redirect(url_for('home'))
    # Render the form for GET requests
    return render_template('add_book.html')




if __name__ == '__main__':
    app.run()
