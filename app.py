from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://4026b4397ea98000e7b309285c82:068f4026-b43a-7014-8000-68afb12126f7@db.fr-pari1.bengt.wasmernet.com:10272/db_ashique'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Category model
class Category(db.Model):  # type: ignore
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationship with products
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

# Product model
class Product(db.Model):  # type: ignore
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    def __repr__(self):
        return f'<Product {self.title}>'

# User model for admin
class User(UserMixin, db.Model):  # type: ignore
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Get all categories
    categories = Category.query.all()
    # Get all products
    products = Product.query.all()
    return render_template('index.html', products=products, categories=categories)

@app.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories, current_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin.html', products=products, categories=categories)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        image_url = request.form['image_url']
        category_id = request.form.get('category_id')
        
        product = Product(
            title=title, 
            description=description, 
            image_url=image_url,
            category_id=int(category_id) if category_id else None
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!')
        return redirect(url_for('admin'))
        
    return render_template('add_product.html', categories=categories)

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.title = request.form['title']
        product.description = request.form['description']
        product.image_url = request.form['image_url']
        category_id = request.form.get('category_id')
        product.category_id = int(category_id) if category_id else None
        
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('admin'))
        
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!')
        return redirect(url_for('admin_categories'))
        
    return render_template('add_category.html')

@app.route('/admin/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']
        
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('admin_categories'))
        
    return render_template('edit_category.html', category=category)

@app.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Check if category has products
    if category.products:
        flash('Cannot delete category with existing products!')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('admin_categories'))

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='ashique').first()
        if not admin_user:
            admin_user = User(username='ashique', password='ashique')
            db.session.add(admin_user)
            db.session.commit()
            
        # Create default categories if none exist
        if not Category.query.first():
            categories = [
                Category(name='Engagement Rings', description='Beautiful engagement rings for your special moment'),
                Category(name='Fine Jewelry', description='Elegant pieces for special occasions'),
                Category(name='Royal Collection', description='Exclusive pieces inspired by royal elegance'),
                Category(name='Gift Sets', description='Perfect curated gifts for your loved ones')
            ]
            for category in categories:
                db.session.add(category)
            db.session.commit()
    app.run(debug=True)