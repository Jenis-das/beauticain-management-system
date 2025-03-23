from app import db

class FashionDesigner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    whatsapp = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(300), nullable=False)  # Store image path

    def __repr__(self):
        return f'FashionDesigner({self.name}, {self.phone})'