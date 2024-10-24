from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from app import db, bcrypt
from app.models import User, Product, Order, Color
from app.forms import ProductForm, RegistrationForm, LoginForm, UpdateAccountForm
from werkzeug.utils import secure_filename
import os
from PIL import Image

# Définir le blueprint 'main' pour les routes générales
main = Blueprint('main', __name__)

# Route pour la page d'accueil
@main.route("/")
def home():
    return render_template('home.html')

# Route pour l'inscription
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

# Route pour la connexion
@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Route pour la déconnexion
@main.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# Route pour le profil utilisateur
@main.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', title='Account', form=form, orders=orders)

# Route pour la boutique (affichage des produits)
@main.route("/shop")
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

# Définir le blueprint 'admin' pour les routes d'administration
admin = Blueprint('admin', __name__)

# Route pour afficher tous les produits (Read)
@admin.route("/products")
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

# Route pour créer un nouveau produit (Create)
@admin.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Sauvegarde de l'image principale
        image_file = save_image(form.image.data) if form.image.data else 'default.jpg'
        
        # Création du produit
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            stock=form.stock.data,
            image_file=image_file
        )
        db.session.add(product)
        db.session.commit()
        
        # Ajout des couleurs
        if form.color1_name.data:
            color1_image = save_image(form.image_color1.data) if form.image_color1.data else None
            color1 = Color(name=form.color1_name.data, image_file=color1_image, product_id=product.id)
            db.session.add(color1)
        
        if form.color2_name.data:
            color2_image = save_image(form.image_color2.data) if form.image_color2.data else None
            color2 = Color(name=form.color2_name.data, image_file=color2_image, product_id=product.id)
            db.session.add(color2)
        
        if form.color3_name.data:
            color3_image = save_image(form.image_color3.data) if form.image_color3.data else None
            color3 = Color(name=form.color3_name.data, image_file=color3_image, product_id=product.id)
            db.session.add(color3)
        
        # Enregistrement des couleurs en base de données
        db.session.commit()

        flash('Product has been created with colors!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('create_product.html', form=form)



def save_image(image):
    if image:
        # Sécuriser le nom du fichier
        filename = secure_filename(image.filename)
        # Obtenir le chemin d'enregistrement complet
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        try:
            # Ouvrir l'image avec Pillow
            img = Image.open(image)
            # Convertir en format webp
            webp_filename = os.path.splitext(filename)[0] + '.webp'
            webp_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], webp_filename)
            img.save(webp_image_path, 'webp')

            # Retourner le nom du fichier webp
            return webp_filename
        except Exception as e:
            print(f"Erreur lors de la conversion en webp: {e}")
            return None
    return None




# Route pour mettre à jour un produit existant (Update)
@admin.route("/product/<int:product_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    
    if form.validate_on_submit():
        # Mettre à jour les informations du produit
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        product.stock = form.stock.data
        
        # Sauvegarder l'image principale
        if form.image.data:
            image_file = save_image(form.image.data)
            product.image_file = image_file
        
        # Mettre à jour les couleurs
        if product.colors:
            if len(product.colors) > 0:
                product.colors[0].name = form.color1_name.data
                if form.image_color1.data:
                    product.colors[0].image_file = save_image(form.image_color1.data)
            if len(product.colors) > 1:
                product.colors[1].name = form.color2_name.data
                if form.image_color2.data:
                    product.colors[1].image_file = save_image(form.image_color2.data)
            if len(product.colors) > 2:
                product.colors[2].name = form.color3_name.data
                if form.image_color3.data:
                    product.colors[2].image_file = save_image(form.image_color3.data)
        
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('admin.products'))
    
    # Pré-remplir les champs du formulaire avec les valeurs actuelles
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.description.data = product.description
        form.stock.data = product.stock
        
        if product.colors:
            if len(product.colors) > 0:
                form.color1_name.data = product.colors[0].name
                form.image_color1.data = product.colors[0].image_file
            if len(product.colors) > 1:
                form.color2_name.data = product.colors[1].name
                form.image_color2.data = product.colors[1].image_file
            if len(product.colors) > 2:
                form.color3_name.data = product.colors[2].name
                form.image_color3.data = product.colors[2].image_file

    return render_template('create_product.html', form=form, product=product)


# Route pour supprimer un produit (Delete)
@admin.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('admin.products'))


@main.route("/add_to_cart/<int:product_id>", methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    # Récupérer la couleur sélectionnée
    selected_color = request.form.get('color')
    if not selected_color:
        flash('Veuillez sélectionner une couleur avant d\'ajouter au panier.', 'danger')
        return redirect(url_for('main.shop'))

    # Trouver l'image de la couleur sélectionnée
    color_image = None
    for color in product.colors:
        if color.name == selected_color:
            color_image = color.image_file
            break

    if not color_image:
        flash('Erreur: cette couleur n\'est pas disponible.', 'danger')
        return redirect(url_for('main.shop'))

    # Vérifier si le panier existe déjà
    cart = session.get('cart', [])

    # Ajouter au panier
    for item in cart:
        if item['product_id'] == product.id and item['color'] == selected_color:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'product_id': product.id,
            'product_name': product.name,
            'price': product.price,
            'color': selected_color,
            'image_file': product.image_file,
            'color_image': color_image,
            'quantity': 1
        })

    # Mettre à jour la session
    session['cart'] = cart
    flash(f"{product.name} ({selected_color}) a été ajouté à votre panier.", 'success')
    
    return redirect(url_for('main.shop'))




# Route pour afficher le panier
@main.route("/cart")
@login_required
def cart():
    cart = session.get('cart', [])
    total= sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

# Route pour MaJ la quantite d'un produit
@main.route("/update_cart/<int:product_id>", methods=['POST'])
@login_required
def update_cart(product_id):
    cart = session.get('cart', [])
    new_quantity = int(request.form.get('quantity', 1))
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = new_quantity
            break
    
    session['cart'] = cart
    flash("The cart has been updated.", 'success')
    
    return redirect(url_for('main.cart'))

# Route pour supprimer un produit du panier
@main.route("/remove_from_cart/<int:product_id>", methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    
    session['cart'] = cart
    flash("The product has been removed from your cart.", 'success')
    
    return redirect(url_for('main.cart'))

