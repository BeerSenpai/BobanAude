from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):
    # Informations sur le produit
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Product Description', validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    
    # Champ pour l'image principale du produit
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    
    # Champs pour les couleurs et leurs images
    color1_name = StringField('Color 1 Name', validators=[DataRequired()])
    image_color1 = FileField('Image Color 1', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    
    color2_name = StringField('Color 2 Name', validators=[DataRequired()])
    image_color2 = FileField('Image Color 2', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    
    color3_name = StringField('Color 3 Name', validators=[DataRequired()])
    image_color3 = FileField('Image Color 3', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    
    submit = SubmitField('Save Product')



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use.')
