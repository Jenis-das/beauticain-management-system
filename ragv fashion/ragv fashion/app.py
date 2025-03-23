from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SECRET_KEY'] = 'your_secret_key'  
db = SQLAlchemy(app)  

class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)
    


@app.route('/')
def home():
    return render_template('index.html')
    
        
                
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        email = request.form['email']  
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')  
        user = User(email=email, password=password)  
        db.session.add(user)  
        db.session.commit()  
        return redirect(url_for('login'))  
    return render_template('register.html')
    
    





@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'POST':  
        email = request.form['email']  
        password = request.form['password']  
        user = User.query.filter_by(email=email).first()  
        if user and check_password_hash(user.password, password):  
            session['user_id'] = user.id  
            return redirect(url_for('dashboard'))  
        return "Invalid credentials"  
    return render_template('login.html')
    
    
    
    
    
    
    
    
@app.route('/dashboard')  
def dashboard():  
    if 'user_id' not in session:  
        return redirect(url_for('login'))  
    return "Welcome to your dashboard!"  

@app.route('/logout')  
def logout():  
    session.pop('user_id', None)  
    return redirect(url_for('login'))
    
    
    
    
    
    
    

    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
    