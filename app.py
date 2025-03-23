from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artists.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Artist Model
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    about = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    whatsapp = db.Column(db.String(15), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    cost = db.Column(db.Float, nullable=False)
    marriage_type = db.Column(db.String(20), nullable=False)  
    image_filename = db.Column(db.String(255), nullable=True)

# Ensure database is created
with app.app_context():
    db.create_all()

# Route to show the admin form
@app.route('/To_add_artist')
def admin_form():
    return render_template('admin.html')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/stats')
def get_stats():
    data = {
        "total_logins": 120,
        "total_bookings": 85,
        "new_registrations": 30,
        "booking_trends": [5, 10, 15, 7, 12, 18, 25]
    }
    return jsonify(data)

@app.route('/admin', methods=['POST'])
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
        pincode = request.form.get('pincode', '')
        cost = float(request.form['cost'])  # Convert to float
        marriage_type = request.form['marriage_type']

        # Step 1: Create artist entry (without image) and commit to get ID
        new_artist = Artist(
            name=name, category=category, about=about, area=area, state=state,
            district=district, phone=phone, whatsapp=whatsapp, pincode=pincode,
            cost=cost, marriage_type=marriage_type, image_filename=None  # Initially None
        )
        db.session.add(new_artist)
        db.session.commit()  # Commit to get assigned ID

        # Step 2: Handle file upload (rename to id.extension)
        image = request.files.get('image')  
        if image and image.filename:
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists
            
            # Extract file extension (e.g., .jpg, .png)
            _, ext = os.path.splitext(image.filename)
            new_filename = f"{new_artist.id}{ext}"  # Rename as id.extension
            image_path = os.path.join(upload_folder, new_filename)
            
            image.save(image_path)  # Save the file
            
            # Step 3: Update artist entry with image filename
            new_artist.image_filename = new_filename
            db.session.commit()  # Update database
        return redirect(url_for('view_artist', artist_id=new_artist.id))


@app.route('/artist/<int:artist_id>')
def view_artist(artist_id):
    artist = Artist.query.get(artist_id)
    print(type(artist), artist)  # Debugging line
    if not artist:
        return "Artist not found!", 404
    return render_template('artist_profile.html', artist=artist)


if __name__ == '__main__':
    with app.app_context():
        artist = db.session.get(Artist, 1)
        if artist:
            print(artist)
        else:
            print("No artist found in the database.")
        db.create_all()
    app.run(debug=True)
