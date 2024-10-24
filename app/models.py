from datetime import datetime
from . import db, bcrypt
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Ajoute cet attribut

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)




class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    products = db.Column(db.Text, nullable=False)  # Stocker les ID des produits ou les détails
    total_amount = db.Column(db.Float, nullable=False)

class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(100), nullable=True)
    
    # Clé étrangère vers Product
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)






class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    
    # Relation vers le modèle Color
    colors = db.relationship('Color', backref='product',cascade="all, delete-orphan", lazy=True)
