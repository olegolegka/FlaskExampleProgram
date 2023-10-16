from flask import Flask,render_template, url_for, request,redirect
from models import db, User
from werkzeug.security import generate_password_hash,check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ignat.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/home')
@app.route("/index/")
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return "login"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password = generate_password_hash(password, "sha256")
        new_user = User(name=name, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/signin")
        except:
            return "Добавление не удалось"
    else:
        return render_template('signup.html')


@app.route('/catalog')
def catalog():
    return "catalog"


@app.route('/item')
def show_item():
    return "item"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)