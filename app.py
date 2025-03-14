from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

# Konfiguracja aplikacji
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Baza SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Konieczne dla sesji

db = SQLAlchemy(app)

# 📌 Model bazy danych
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=True)  # Jednorazowe hasło

# Tworzenie bazy, jeśli nie istnieje
with app.app_context():
    db.create_all()

# 📌 Generowanie unikalnego loginu
def generate_unique_login():
    while True:
        new_login = ''.join(str(random.randint(1, 9)) for _ in range(10))
        if not User.query.filter_by(login=new_login).first():
            return new_login

# 📌 Generowanie jednorazowego hasła
def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# 📌 Strona główna
@app.route('/')
def home():
    return render_template('home.html')

# 📌 Generowanie loginu i hasła
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        new_login = generate_unique_login()
        new_password = generate_password()

        user = User(login=new_login, password=new_password)
        db.session.add(user)
        db.session.commit()

        return render_template('generated.html', login=new_login, password=new_password)
    return render_template('generate.html')

# 📌 Logowanie użytkownika
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(login=login, password=password).first()

        if user:
            session['user'] = login
            user.password = None  # Hasło jest jednorazowe – kasujemy je po użyciu
            db.session.commit()
            return redirect(url_for('dashboard'))

        return "❌ Błędne dane logowania lub hasło już użyte"

    return render_template('login.html')

# 📌 Panel użytkownika (dashboard)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"🎉 Witaj {session['user']}! Zalogowałeś się poprawnie."
    return redirect(url_for('login'))

# 📌 Uruchomienie aplikacji Flask
if __name__ == '__main__':
    app.run(debug=True)
