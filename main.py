from urllib.parse import urlencode
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Float, Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired
import requests # type: ignore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
Bootstrap5(app)
login_manager = LoginManager(app)

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# CREATE TABLE IN DB


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    # Relationship to access books associated with a user
    books = db.relationship('Book', backref='user', lazy=True)

class Book(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)  # Removed unique=True
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'), nullable=False)




#Forms
class AddForm(FlaskForm):
    title = StringField('Book title')
    confirm = SubmitField('Add Book')


class CritiqueForm(FlaskForm):
    rating = StringField('Enter Your Rating')
    review = StringField('Enter Your Review')
    submit = SubmitField("Add")


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user_query = db.session.execute(db.select(User).where(User.email == email))
        user = user_query.scalar()
        if user:
            flash('Email already exists, log in', 'error')
            return redirect(url_for('login'))

        if len(password) < 5:
            flash('Password must be at least 5 characters long', 'error')
            return redirect(url_for('register'))
        new_user = User(
            email = email,
            password = hash_and_salted_password,
            name = name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return render_template('books.html', name = new_user.name)

    return render_template("register.html")


@app.route('/login' , methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email =  request.form.get('email')
        password = request.form.get('password')

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Check stored password hash against entered password hashed.
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('secrets', name = user.name))
        else:
            flash('Username or password is incorrect', 'error')
            return render_template("login.html")
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    result = db.session.execute(db.select(Book).where(Book.user_id == current_user.id).order_by(Book.rating))
    all_books = result.scalars().all()
    for i in range(len(all_books)):
        all_books[i].ranking = len(all_books) - i

    shelves = [all_books[i:i + 4] for i in range(0, len(all_books), 4)]
    db.session.commit()
    return render_template("books.html", shelves = shelves)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/update', methods = ["GET", "POST"])
def update():
    id = request.args.get('id')
    form = CritiqueForm()
    book_to_update = db.session.execute(db.select(Book).where(Book.id == id)).scalar()

    if request.method == "POST":
        if form.validate_on_submit:
            rating = float(form.rating.data)
            review = form.review.data
            book_to_update = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
            book_to_update.rating = rating
            book_to_update.review = review
            db.session.commit()
        return redirect(url_for('secrets'))
    return render_template('edit.html', form = form, name = book_to_update.title)

@app.route('/delete')
def delete():
    book_id = request.args.get('id')
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    # or book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('secrets'))


@app.route('/edit', methods = ["GET", "POST"])
def edit():
    form = CritiqueForm()
    title = request.args.get('title')
    book_id = request.args.get('bookid')
    publish_year = request.args.get('pyear')
    author = request.args.get('author')
    if request.method == "POST":
        if form.validate_on_submit:
            rating = float(form.rating.data)
            review = form.review.data
            new_book = Book(
                title = title,
                year = publish_year,
                rating = rating,
                review = review,
                img_url = f"https://covers.openlibrary.org/b/id/{book_id}-L.jpg",
                user_id = current_user.id
            )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('secrets'))


    return render_template('edit.html', form = form)

@app.route('/add', methods = ["GET", "POST"])
def add():
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit:
            title = form.title.data
            base_url = 'https://openlibrary.org/search.json'
    
    # Parameters to be included in the URL
            params = {'q': title}
    
    # Encode parameters and create the full URL
            url = f"{base_url}?{urlencode(params)}"
    
    # Make the GET request
            response = requests.get(base_url, params={"title": title})
            data = response.json()["docs"]    
            print(data)
            return render_template('select.html', options = data)

    return render_template('add.html', form = form)

@app.route('/findbook')
def findbook():
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit:
            title = form.title.data
            base_url = 'https://openlibrary.org/search.json'
    
    # Make the GET request
            response = requests.get(base_url, params={"title": title})
            data = response.json()["docs"]    
            print(data)
            return render_template('select.html', options = data)

    return render_template('add.html', form = form)

    

if __name__ == "__main__":
    app.run(debug=True)
