import os
import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import func

from datetime import datetime
from models.data_models import db, Author, Book


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, os.getenv('DATABASE_PATH'))

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db.init_app(app)

with app.app_context():
  db.create_all()

@app.route('/', methods=['GET'])
def root():
    """
    Redirects root URL to the home page.
    """
    return redirect(url_for('home'))


@app.route('/home', methods=['GET'])
def home():
    """
    Displays the homepage with a list of books.
    Supports sorting and search functionality.
    """
    sort_by = request.args.get('sort_by', 'title')
    search = request.args.get('search', '').strip()

    query = Book.query.join(Author)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            func.lower(Book.title).like(func.lower(pattern)) |
            func.lower(Author.name).like(func.lower(pattern))
        )

    if sort_by == 'title':
        query = query.order_by(func.lower(Book.title))
    elif sort_by == 'author':
        query = query.order_by(func.lower(Author.name))
    elif sort_by == 'year':
        query = query.order_by(Book.publication_year.desc())

    books = query.all()
    return render_template('home.html', books=books)



@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handles the form for adding a new author.
    On GET, displays the form.
    On POST, processes and stores the author in the database.
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        date_of_death_str = request.form.get('date_of_death', '').strip()
        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d") if date_of_birth_str else None
        date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d") if date_of_death_str else None

        author = Author(name=name,
                        date_of_birth=date_of_birth,
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
    """
    Handles the form for adding a new book.
    On GET, displays the form.
    On POST, processes and stores the book in the database.
    Creates the author if not already present.
    """
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

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """
    Deletes the book with the given ID.
    """
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash('Book successfully deleted!')
        return redirect(url_for('home'))
    else:
        flash('Error deleting post. Please try again.')


if __name__ == '__main__':
    app.run()
