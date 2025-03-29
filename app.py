from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from io import BytesIO


app = Flask(__name__)
app.secret_key = 'fashion'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'  
app.config['SQLALCHEMY_BINDS'] = {
    'artists_db': 'sqlite:///artists.db',
    'applications_db': 'sqlite:///applications.db',
    'login' : 'sqlite:///users.db'
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Flask-Mail Configuration (Use environment variables for security)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "questionmarkcreations143@gmail.com")  # Use env variable
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "cqqr towk lefs zerq")  # Use env variable
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]


mail = Mail(app)

# Apply Route
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            category = request.form['category']
            about = request.form['about']
            area = request.form['area']
            state = request.form['state']
            district = request.form['district']
            phone = request.form['phone']
            whatsapp = request.form.get('whatsapp', 'N/A')  # Optional
            email = request.form['email']
            pincode = request.form.get('pincode', 'N/A')  # Optional
            marriage_type = request.form['marriage_type']
            cost = request.form['cost']
            image = request.files.get('image')

            # Email subject & body
            subject = "New Artist Application Received"
            body = f"""
            New application received:

            Name: {name}
            Category: {category}
            About: {about}

            Address: {area}, {district}, {state} - {pincode}
            Phone: {phone}
            WhatsApp: {whatsapp}
            Email: {email}

            Marriage Type: {marriage_type}
            Work Rate: ₹{cost}/hour
            """

            # Send Email
            msg = Message(subject, recipients=[email])
            msg.body = body

            # Attach image if provided
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_bytes = BytesIO(image.read())  # Read the file in memory
                msg.attach(filename, image.content_type, image_bytes.getvalue())

            mail.send(msg)
            flash("Application submitted! Confirmation email sent.", "success")

        except Exception as e:
            flash(f"Error submitting application: {str(e)}", "danger")

        return redirect(url_for('apply'))

    return render_template('apply.html')



# user database 
class User(db.Model):  
    __bind_key__ = 'login'  # Bind to the correct database
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords





# class Application(db.Model):
#     __bind_key__ = 'applications_db'  # Binds to applications.db
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     category = db.Column(db.String(50), nullable=False)
#     about = db.Column(db.Text, nullable=False)
#     area = db.Column(db.String(150), nullable=False)
#     state = db.Column(db.String(50), nullable=False)
#     district = db.Column(db.String(50), nullable=False)
#     phone = db.Column(db.String(15), nullable=False)
#     whatsapp = db.Column(db.String(15), nullable=True)
#     email = db.Column(db.String(100), nullable=False, unique=True)
#     pincode = db.Column(db.String(10), nullable=False)
#     marriage_type = db.Column(db.String(50), nullable=False)
#     cost = db.Column(db.Integer, nullable=False)
#     image_filename = db.Column(db.String(200), nullable=False)
#     submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())




# Artist Model
class Artist(db.Model):
    __bind_key__ = 'artists_db'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    about = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    whatsapp = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)  # ✅ Added email field
    pincode = db.Column(db.String(10), nullable=True)
    cost = db.Column(db.Float, nullable=False)
    marriage_type = db.Column(db.String(20), nullable=False)  
    image_filename = db.Column(db.String(255), nullable=True)


# Route for Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered! Please log in.', 'danger')
            return redirect(url_for('login'))

        # Hash password and create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')



# Route for Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  
        else:
            flash('Invalid credentials. Try again!', 'danger')
    
    return render_template('login.html')

# Route for Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# @app.route('/application', methods=['GET', 'POST'])
# def application():
#     if request.method == 'POST':
#         name = request.form['name']
#         category = request.form['category']
#         about = request.form['about']
#         area = request.form['area']
#         state = request.form['state']
#         district = request.form['district']
#         phone = request.form['phone']
#         whatsapp = request.form['whatsapp']
#         email = request.form['email']
#         pincode = request.form['pincode']
#         marriage_type = request.form['marriage_type']
#         cost = request.form['cost']
        
#         # Handle Image Upload
#         if 'image' not in request.files:
#             flash('No image file found!', 'danger')
#             return redirect(request.url)

#         image = request.files['image']
#         if image.filename == '':
#             flash('No selected file!', 'danger')
#             return redirect(request.url)

#         filename = secure_filename(image.filename)
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         image.save(image_path)

#         # Check if email already exists
#         existing_application = Application.query.filter_by(email=email).first()
#         if existing_application:
#             flash("You have already applied!", "dangen"
#             "r")
#             return redirect(url_for('application'))

#         # Save the application
#         new_application = Application(
#             name=name, category=category, about=about, area=area, state=state,
#             district=district, phone=phone, whatsapp=whatsapp, email=email,
#             pincode=pincode, marriage_type=marriage_type, cost=cost, image_filename=filename
#         )
#         db.session.add(new_application)
#         db.session.commit()

#         flash("Application submitted successfully!", "success")
#         return redirect(url_for('application'))

#     return render_template('application.html')


@app.route('/applications')
def applications_list():
    applications = Application.query.all()
    return render_template('applications.html', applications=applications)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


# @app.route('/beauticians', methods=['GET', 'POST'])
# def beauticians():
#     query = Artist.query

#     # Handle search query from index.html
#     search_query = request.args.get('search')
#     if search_query:
#         query = query.filter(
#             Artist.name.ilike(f"%{search_query}%") | 
#             Artist.category.ilike(f"%{search_query}%")
#         )

#     # Use request.args for GET and request.form for POST
#     if request.method == 'POST':
#         state = request.form.get('state')
#         wedding_type = request.form.get('wedding_type')
#         district = request.form.get('district')
#         category = request.form.get('category')
#     else:  # GET method
#         state = request.args.get('state')
#         wedding_type = request.args.get('wedding_type')
#         district = request.args.get('district')
#         category = request.args.get('category')

#     # Apply filters if selected
#     if state:
#         query = query.filter_by(state=state)
#     if wedding_type:
#         query = query.filter_by(marriage_type=wedding_type)
#     if district:
#         query = query.filter_by(district=district)
#     if category:
#         query = query.filter_by(category=category)

#     artists = query.all()  
#     states = ["Tamil Nadu", "Kerala", "Karnataka"]
#     wedding_types = ["Hindu", "Muslim", "Christian"]
#     districts = [d[0] for d in Artist.query.with_entities(Artist.district).distinct().all()]
#     categories = [d[0] for d in Artist.query.with_entities(Artist.category).distinct().all()]

#     return render_template('beauticians.html', artists=artists, states=states, wedding_types=wedding_types, districts=districts, category=categories)



@app.route('/beauticians', methods=['GET', 'POST'])
def beauticians():
    query = Artist.query

    # Use request.args for GET and request.form for POST
    if request.method == 'POST':
        state = request.form.get('state')
        wedding_type = request.form.get('wedding_type')
        district = request.form.get('district')
        category = request.form.get('category')
    else:  # GET method
        state = request.args.get('state')
        wedding_type = request.args.get('wedding_type')
        district = request.args.get('district')
        category = request.args.get('category')

    # Apply filters if selected
    if state:
        query = query.filter_by(state=state)
    if wedding_type:
        query = query.filter_by(marriage_type=wedding_type)
    if district:
        query = query.filter_by(district=district)
    if category:
        query = query.filter_by(category=category)

    artists = query.all()  
    states = ["Tamil Nadu", "Kerala", "Karnataka"]
    wedding_types = ["Hindu", "Muslim", "Christian"]
    districts = [d[0] for d in Artist.query.with_entities(Artist.district).distinct().all()]
    category = [d[0] for d in Artist.query.with_entities(Artist.category).distinct().all()]
    return render_template('beauticians.html', artists=artists, states=states, wedding_types=wedding_types, districts=districts , category=category)





@app.route('/')
def home():
    artists = Artist.query.limit(3).all()  # Fetch first three artists
    categories = [c[0] for c in Artist.query.with_entities(Artist.category).distinct().all()]
    return render_template('index.html', artists=artists, categories=categories)



# @app.route('/apply')
# def apply():
#     return render_template('apply.html')



# Route to show the admin form
@app.route('/To_add_artist')
def admin_form():
    return render_template('To_add_artist.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Admin credentials (store in env variables or database for production use)
ADMIN_EMAIL = "ragav@gmail.com"
ADMIN_PASSWORD = "ragav12345678"

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['adminemail']
        password = request.form['adminpassword']

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True  # Store session
            flash("Admin login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid admin credentials!", "danger")

    return render_template('adminlogin.html')  # Render login page

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please login as admin first!", "warning")
        return redirect(url_for('adminlogin'))

    return "Welcome to Admin Dashboard!"  # Replace with your dashboard template

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin_login'))


@app.route('/stats')
def get_stats():
    data = {
        "total_logins": 120,
        "total_bookings": 85,
        "new_registrations": 30,
        "booking_trends": [5, 10, 15, 7, 12, 18, 25]
    }
    return jsonify(data)




@app.route('/admin', methods=['POST', 'GET'])
def add_artist():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        about = request.form['about']
        area = request.form['area']
        state = request.form['state']
        district = request.form['district']
        phone = request.form['phone']
        whatsapp = request.form.get('whatsapp', '')
        email = request.form['email']  # ✅ Get email
        pincode = request.form.get('pincode', '')
        cost = float(request.form['cost'])
        marriage_type = request.form['marriage_type']

        # ✅ Check if the email already exists
        existing_artist = Artist.query.filter_by(email=email).first()
        if existing_artist:
            flash("Email already exists! Please use a different email.", "danger")
            return redirect(url_for('admin_form'))  # ✅ Use correct route function name

        # Step 1: Create artist entry (without image) and commit to get ID
        try:
            new_artist = Artist(
                name=name, category=category, about=about, area=area, state=state,
                district=district, phone=phone, whatsapp=whatsapp, email=email,
                pincode=pincode, cost=cost, marriage_type=marriage_type, image_filename=None
            )
            db.session.add(new_artist)
            db.session.commit()  # ✅ Commit to get assigned ID
        except:
            db.session.rollback()  # Rollback in case of error
            flash("Error adding artist. Please try again.", "danger")
            return redirect(url_for('admin_form'))  # ✅ Redirect to admin form on error

        # Step 2: Handle file upload (rename to id.extension)
        image = request.files.get('image')
        if image and image.filename:
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)  # ✅ Ensure folder exists

            _, ext = os.path.splitext(image.filename)
            new_filename = f"{new_artist.id}{ext}"  # ✅ Rename as id.extension
            image_path = os.path.join(upload_folder, new_filename)

            image.save(image_path)  # ✅ Save the file

            # Step 3: Update artist entry with image filename
            new_artist.image_filename = new_filename
            db.session.commit()  # ✅ Update database

        return redirect(url_for('view_artist', artist_id=new_artist.id))




@app.route('/artist/<int:artist_id>')
def view_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return "Artist not found!", 404
    return render_template('artist_profile.html', artist=artist)






if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
