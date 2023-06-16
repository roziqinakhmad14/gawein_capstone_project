from flask import Flask, redirect, url_for, request, flash, render_template, jsonify
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import sklearn
import os, pickle, pytesseract, re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

model = pickle.load(open('model_pkl','rb'))
vectorizer = pickle.load(open('vectorizer_pkl','rb'))

#database engine
engine = create_engine('sqlite:///sqlite.db')
db = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

#user model
class User(UserMixin, db):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = Column(String(100), unique=True)
    password = Column(String(100))
    first_name = Column(String(1000))
    last_name = Column(String(1000))

db.metadata.create_all(engine)

@app.route('/')
def index():
    return 'Welcome to Gawe.In'

@app.route('/profile')
@login_required
def profile():
    return 'This is profile page'

@app.route('/login')
def login():
    return 'Login'

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = session.query(User).filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again')
        return redirect(url_for('login'))
    
    login_user(user, remember=remember)
    return redirect(url_for('profile'))

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return session.query(User).get(id)

@app.route('/signup')
def signup():
    return 'Signup'

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    user = session.query(User).filter_by(email=email).first()

    if user:
        return redirect(url_for('login'))
    
    new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'))
    session.add(new_user)
    session.commit()

    return redirect(url_for('login'))

@app.route('/upload')
def upload():
    return 'Upload your resume here!'

@app.route('/upload', methods=['POST'])
def upload_post():
   data = request.args.get('cv')
   img_path = request.files['img_file']
   img = Image.open(img_path)
   text = pytesseract.image_to_string(img)
   escape_char = ['\a', '\b', '\f', '\n', '\r', '\t', '\v']
   raw_char = ['\\a', '\\b', '\\f', '\\n', '\\r', '\\t', '\\v']
   for i in range(len(escape_char)):
       text = text.replace(escape_char[i], raw_char[i])
   text = re.sub('http\S+\s*', ' ', text)  # remove URLs
   text = re.sub('RT|cc', ' ', text)  # remove RT and cc
   text = re.sub('#\S+', '', text)  # remove hashtags
   text = re.sub('@\S+', '  ', text)  # remove mentions
   text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)  # remove punctuations
   text = re.sub(r'[^\x00-\x7f]',r' ', text) 
   text = re.sub('\s+', ' ', text)  # remove extra whitespace
   data = text

   feature = vectorizer.transform([data])
   prediction = model.predict(feature)[0]
   print(prediction)
   return jsonify({'result': prediction})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)