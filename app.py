import os
import json
import urllib.parse
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from werkzeug.utils import secure_filename
import database as db
import seed

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "thefragances_perfumes_secret_key_2026_x87b")
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Auto initialize and seed DB on start if needed (critical for Render / cloud deploy)
db.init_db()
seed.run_seed()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_global_data():
    settings = db.get_settings()
    all_brands = db.get_all_brands()
    
    current_user = None
    if 'user_id' in session:
        current_user = db.get_user_by_id(session['user_id'])
        
    is_admin = session.get('admin_logged_in', False) or (current_user and current_user.get('role') == 'admin')
    
    return dict(
        settings=settings,
        global_brands=all_brands,
        current_user=current_user,
        is_admin_logged_in=is_admin
    )

def is_admin():
    if session.get('admin_logged_in'):
        return True
    if 'user_id' in session:
        u = db.get_user_by_id(session['user_id'])
        return u and u.get('role') == 'admin'
    return False

# ----------------- CLIENT ROUTES ----------------- #

@app.route('/')
def index():
    # Only the actual 20 perfumes in real stock
    all_perfumes = db.get_perfumes(order_by='name', limit=50)
    men_perfumes = [p for p in all_perfumes if p['gender'] == 'Hombre']
    women_perfumes = [p for p in all_perfumes if p['gender'] == 'Mujer']
    unisex_perfumes = [p for p in all_perfumes if p['gender'] == 'Unisex']
    stats = db.get_stats()
    
    # Real reviews from database
    recent_reviews = db.get_recent_reviews(limit=5)

    # Spotlight Perfume for the Left Hero Banner (from actual stock)
    spotlight_perfume = db.get_perfume_by_slug("chanel-bleu-de-chanel") or (all_perfumes[0] if all_perfumes else None)
    
    return render_template(
        'index.html',
        all_perfumes=all_perfumes,
        men_perfumes=men_perfumes,
        women_perfumes=women_perfumes,
        unisex_perfumes=unisex_perfumes,
        stats=stats,
        recent_reviews=recent_reviews,
        spotlight_perfume=spotlight_perfume
    )

@app.route('/catalogo')
def catalog():
    search = request.args.get('q', '').strip()
    brand_id = request.args.get('marca', type=int)
    gender = request.args.get('genero', '').strip()
    accord = request.args.get('acorde', '').strip()
    in_stock_param = request.args.get('stock')
    in_stock_only = True if in_stock_param == '1' else False
    order_by = request.args.get('orden', 'featured')
    
    perfumes = db.get_perfumes(
        search=search if search else None,
        brand_id=brand_id,
        gender=gender if gender else None,
        in_stock_only=in_stock_only,
        accord=accord if accord else None,
        order_by=order_by,
        limit=100
    )
    
    total_count = db.get_perfumes_count(
        search=search if search else None,
        brand_id=brand_id,
        gender=gender if gender else None,
        in_stock_only=in_stock_only,
        accord=accord if accord else None
    )
    
    all_brands = db.get_all_brands()
    
    return render_template(
        'catalog.html',
        perfumes=perfumes,
        total_count=total_count,
        search=search,
        selected_brand=brand_id,
        selected_gender=gender,
        selected_accord=accord,
        in_stock_only=in_stock_only,
        selected_order=order_by,
        all_brands=all_brands
    )

@app.route('/perfume/<slug>')
def perfume_detail(slug):
    perfume = db.get_perfume_by_slug(slug)
    if not perfume:
        abort(404)
        
    related = db.get_related_perfumes(perfume['brand_id'], perfume['id'], limit=4)
    reviews = db.get_perfume_reviews(perfume['id'])
    
    settings = db.get_settings()
    phone = settings.get('whatsapp_number', '').replace('+', '').replace(' ', '').replace('-', '')
    
    price_str = f"${perfume['price']:.2f}"
    if perfume.get('price_range'):
        price_str += f" ({perfume['price_range']})"
        
    msg = (
        f"¡Hola! Vengo de su página web {settings.get('store_name', 'The Fragance´s')} y me interesa el perfume *{perfume['name']}* de *{perfume['brand_name']}* "
        f"({perfume.get('presentation', perfume.get('concentration', 'Perfume'))}).\n"
        f"Precio: {price_str}.\n"
        f"¿Tienen disponibilidad en stock para entrega o envío?"
    )
    whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
    
    return render_template(
        'detail.html',
        perfume=perfume,
        related=related,
        reviews=reviews,
        whatsapp_url=whatsapp_url
    )

# ----------------- REAL REVIEWS SUBMISSION ----------------- #

@app.route('/perfume/<slug>/resena', methods=['POST'])
def submit_review(slug):
    if 'user_id' not in session:
        flash("Debes iniciar sesión para publicar una reseña de compra.", "warning")
        return redirect(url_for('user_login'))
        
    perfume = db.get_perfume_by_slug(slug)
    if not perfume:
        abort(404)
        
    rating = request.form.get('rating', type=int) or 5
    comment = request.form.get('comment', '').strip()
    
    if not comment:
        flash("Por favor escribe tu opinión sobre el perfume.", "warning")
        return redirect(url_for('perfume_detail', slug=slug))
        
    db.add_review(perfume['id'], session['user_id'], rating, comment)
    flash("¡Gracias por tu reseña! Ha sido publicada exitosamente en el catálogo.", "success")
    return redirect(url_for('perfume_detail', slug=slug))

# ----------------- USER AUTH ROUTES ----------------- #

@app.route('/registro', methods=['GET', 'POST'])
def user_register():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email or not password:
            flash("Todos los campos con asterisco (*) son obligatorios.", "danger")
            return render_template('auth/register.html')
            
        user_id, err = db.create_user(name, email, password, phone)
        if err:
            flash(err, "danger")
            return render_template('auth/register.html')
            
        session['user_id'] = user_id
        flash(f"¡Bienvenido a The Fragance´s, {name}! Tu cuenta ha sido creada.", "success")
        return redirect(url_for('user_profile'))
        
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user = db.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            if user['role'] == 'admin':
                session['admin_logged_in'] = True
            flash(f"¡Hola de nuevo, {user['name']}!", "success")
            return redirect(url_for('user_profile'))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
            
    return render_template('auth/login.html')

@app.route('/logout')
def user_logout():
    session.pop('user_id', None)
    session.pop('admin_logged_in', None)
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('index'))

@app.route('/perfil')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    user = db.get_user_by_id(session['user_id'])
    reviews = db.get_user_reviews(session['user_id'])
    return render_template('auth/profile.html', user=user, reviews=reviews)

@app.route('/marcas')
def brands_list():
    brands = db.get_all_brands()
    return render_template('brands.html', brands=brands)

@app.route('/marca/<slug>')
def brand_detail(slug):
    brand = db.get_brand_by_slug(slug)
    if not brand:
        abort(404)
    perfumes = db.get_perfumes(brand_id=brand['id'], limit=100)
    collections = db.get_collections_by_brand(brand['id'])
    return render_template('brand_detail.html', brand=brand, perfumes=perfumes, collections=collections)

# ----------------- ADMIN ROUTES ----------------- #

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
        
    settings = db.get_settings()
    correct_pin = settings.get('admin_pin', '1234')
    
    if request.method == 'POST':
        pin = request.form.get('pin', '').strip()
        if pin == correct_pin:
            session['admin_logged_in'] = True
            flash('¡Bienvenido al Panel de Administración!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('PIN incorrecto. Inténtalo de nuevo.', 'danger')
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Sesión de administrador cerrada.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    stats = db.get_stats()
    recent_perfumes = db.get_perfumes(order_by='newest', limit=6)
    return render_template('admin/dashboard.html', stats=stats, recent_perfumes=recent_perfumes)

@app.route('/admin/usuarios')
def admin_users():
    if not is_admin():
        return redirect(url_for('admin_login'))
    users = db.get_all_users()
    return render_template('admin/users_list.html', users=users)

@app.route('/admin/resenas')
def admin_reviews():
    if not is_admin():
        return redirect(url_for('admin_login'))
    reviews = db.get_recent_reviews(limit=100)
    return render_template('admin/reviews_list.html', reviews=reviews)

@app.route('/admin/resenas/eliminar/<int:id>', methods=['POST'])
def admin_review_delete(id):
    if not is_admin():
        flash("Acción no autorizada.", "danger")
        return redirect(url_for('user_login'))
    db.delete_review(id)
    flash("Reseña eliminada del sistema.", "info")
    return redirect(request.referrer or url_for('admin_reviews'))

@app.route('/admin/perfumes')
def admin_perfumes():
    if not is_admin():
        return redirect(url_for('admin_login'))
    search = request.args.get('q', '').strip()
    brand_id = request.args.get('marca', type=int)
    perfumes = db.get_perfumes(search=search if search else None, brand_id=brand_id, limit=200)
    brands = db.get_all_brands()
    return render_template('admin/perfumes_list.html', perfumes=perfumes, brands=brands, search=search, selected_brand=brand_id)

@app.route('/admin/perfumes/nuevo', methods=['GET', 'POST'])
def admin_perfume_new():
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    brands = db.get_all_brands()
    collections = db.get_all_collections()
    
    if request.method == 'POST':
        try:
            image_url = request.form.get('image_url', '').strip()
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = f"/static/uploads/{filename}"

            accords_raw = request.form.get('accords_json', '[]')
            try:
                accords = json.loads(accords_raw)
            except Exception:
                accords = []

            def parse_csv_list(text):
                return [item.strip() for item in text.split(',') if item.strip()]

            top_notes = parse_csv_list(request.form.get('top_notes', ''))
            heart_notes = parse_csv_list(request.form.get('heart_notes', ''))
            base_notes = parse_csv_list(request.form.get('base_notes', ''))
            seasons = request.form.getlist('seasons')
            occasions = request.form.getlist('occasions')

            brand_id = int(request.form.get('brand_id'))
            brand = db.get_brand_by_id(brand_id)

            data = {
                'name': request.form.get('name'),
                'brand_id': brand_id,
                'brand_name': brand['name'] if brand else '',
                'collection_id': int(request.form.get('collection_id')) if request.form.get('collection_id') else None,
                'gender': request.form.get('gender', 'Unisex'),
                'concentration': request.form.get('concentration', 'Eau de Parfum'),
                'size_ml': int(request.form.get('size_ml', 100)),
                'presentation': request.form.get('presentation', ''),
                'price': float(request.form.get('price', 0.0)),
                'price_range': request.form.get('price_range', ''),
                'discount_price': float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
                'in_stock': 1 if request.form.get('in_stock') == '1' else 0,
                'stock_status': request.form.get('stock_status', 'en_stock'),
                'stock_quantity': int(request.form.get('stock_quantity', 1)),
                'image_url': image_url or 'https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=600&auto=format&fit=crop&q=80',
                'olfactory_family': request.form.get('olfactory_family', ''),
                'year_released': int(request.form.get('year_released')) if request.form.get('year_released') else None,
                'perfumer': request.form.get('perfumer', ''),
                'description': request.form.get('description', ''),
                'accords': accords,
                'top_notes': top_notes,
                'heart_notes': heart_notes,
                'base_notes': base_notes,
                'seasons': seasons,
                'occasions': occasions,
                'longevity': request.form.get('longevity', 'Moderada (6-8h)'),
                'sillage': request.form.get('sillage', 'Moderada'),
                'rating': float(request.form.get('rating', 4.8)),
                'is_featured': 1 if request.form.get('is_featured') == '1' else 0
            }

            db.save_perfume(data)
            flash(f"¡Perfume '{data['name']}' creado con éxito!", 'success')
            return redirect(url_for('admin_perfumes'))
        except Exception as e:
            flash(f"Error al guardar el perfume: {str(e)}", 'danger')

    return render_template(
        'admin/perfume_form.html',
        perfume=None,
        brands=brands,
        collections=collections
    )

@app.route('/admin/perfumes/editar/<int:id>', methods=['GET', 'POST'])
def admin_perfume_edit(id):
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    perfume = db.get_perfume_by_id(id)
    if not perfume:
        flash("Perfume no encontrado.", 'warning')
        return redirect(url_for('admin_perfumes'))
        
    brands = db.get_all_brands()
    collections = db.get_all_collections()

    if request.method == 'POST':
        try:
            image_url = request.form.get('image_url', '').strip()
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = f"/static/uploads/{filename}"

            if not image_url:
                image_url = perfume.get('image_url', '')

            accords_raw = request.form.get('accords_json', '[]')
            try:
                accords = json.loads(accords_raw)
            except Exception:
                accords = perfume.get('accords', [])

            def parse_csv_list(text):
                return [item.strip() for item in text.split(',') if item.strip()]

            top_notes = parse_csv_list(request.form.get('top_notes', ''))
            heart_notes = parse_csv_list(request.form.get('heart_notes', ''))
            base_notes = parse_csv_list(request.form.get('base_notes', ''))
            seasons = request.form.getlist('seasons')
            occasions = request.form.getlist('occasions')

            brand_id = int(request.form.get('brand_id'))
            brand = db.get_brand_by_id(brand_id)

            data = {
                'name': request.form.get('name'),
                'brand_id': brand_id,
                'brand_name': brand['name'] if brand else '',
                'collection_id': int(request.form.get('collection_id')) if request.form.get('collection_id') else None,
                'gender': request.form.get('gender', 'Unisex'),
                'concentration': request.form.get('concentration', 'Eau de Parfum'),
                'size_ml': int(request.form.get('size_ml', 100)),
                'presentation': request.form.get('presentation', ''),
                'price': float(request.form.get('price', 0.0)),
                'price_range': request.form.get('price_range', ''),
                'discount_price': float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
                'in_stock': 1 if request.form.get('in_stock') == '1' else 0,
                'stock_status': request.form.get('stock_status', 'en_stock'),
                'stock_quantity': int(request.form.get('stock_quantity', 1)),
                'image_url': image_url,
                'olfactory_family': request.form.get('olfactory_family', ''),
                'year_released': int(request.form.get('year_released')) if request.form.get('year_released') else None,
                'perfumer': request.form.get('perfumer', ''),
                'description': request.form.get('description', ''),
                'accords': accords,
                'top_notes': top_notes,
                'heart_notes': heart_notes,
                'base_notes': base_notes,
                'seasons': seasons,
                'occasions': occasions,
                'longevity': request.form.get('longevity', 'Moderada (6-8h)'),
                'sillage': request.form.get('sillage', 'Moderada'),
                'rating': float(request.form.get('rating', 4.8)),
                'is_featured': 1 if request.form.get('is_featured') == '1' else 0
            }

            db.save_perfume(data, perfume_id=id)
            flash(f"¡Perfume '{data['name']}' actualizado con éxito!", 'success')
            return redirect(url_for('admin_perfumes'))
        except Exception as e:
            flash(f"Error al actualizar el perfume: {str(e)}", 'danger')

    return render_template(
        'admin/perfume_form.html',
        perfume=perfume,
        brands=brands,
        collections=collections
    )

@app.route('/admin/perfumes/eliminar/<int:id>', methods=['POST'])
def admin_perfume_delete(id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    db.delete_perfume(id)
    flash("Perfume eliminado del catálogo.", 'info')
    return redirect(url_for('admin_perfumes'))

@app.route('/api/toggle-stock/<int:id>', methods=['POST'])
def api_toggle_stock(id):
    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 401
    result = db.toggle_perfume_stock(id)
    if not result:
        return jsonify({'error': 'Perfume no encontrado'}), 404
    return jsonify({'success': True, 'data': result})

@app.route('/admin/marcas', methods=['GET', 'POST'])
def admin_brands():
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_brand':
            name = request.form.get('name', '').strip()
            country = request.form.get('country', '').strip()
            description = request.form.get('description', '').strip()
            logo_url = request.form.get('logo_url', '').strip()
            
            if 'logo_file' in request.files:
                file = request.files['logo_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"brand_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    logo_url = f"/static/uploads/{filename}"
                    
            if name:
                db.create_brand(name, country, description, logo_url)
                flash(f"Marca '{name}' agregada con éxito.", 'success')
            else:
                flash("El nombre de la marca es obligatorio.", 'danger')
                
        elif action == 'create_collection':
            brand_id = request.form.get('brand_id', type=int)
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            if brand_id and name:
                db.create_collection(brand_id, name, description)
                flash(f"Colección '{name}' creada con éxito.", 'success')
            else:
                flash("Selecciona una marca y escribe el nombre de la colección.", 'danger')
                
        return redirect(url_for('admin_brands'))
        
    brands = db.get_all_brands()
    collections = db.get_all_collections()
    return render_template('admin/brands_list.html', brands=brands, collections=collections)

@app.route('/admin/marcas/eliminar/<int:id>', methods=['POST'])
def admin_brand_delete(id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    success, msg = db.delete_brand(id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin_brands'))

@app.route('/admin/colecciones/eliminar/<int:id>', methods=['POST'])
def admin_collection_delete(id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    db.delete_collection(id)
    flash("Colección eliminada.", 'info')
    return redirect(url_for('admin_brands'))

@app.route('/admin/ajustes', methods=['GET', 'POST'])
def admin_settings():
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        store_name = request.form.get('store_name', '').strip()
        store_tagline = request.form.get('store_tagline', '').strip()
        whatsapp_number = request.form.get('whatsapp_number', '').strip()
        announcement_bar = request.form.get('announcement_bar', '').strip()
        currency_symbol = request.form.get('currency_symbol', '$').strip()
        admin_pin = request.form.get('admin_pin', '').strip()
        
        if store_name:
            db.update_setting('store_name', store_name)
        if store_tagline:
            db.update_setting('store_tagline', store_tagline)
        if whatsapp_number:
            db.update_setting('whatsapp_number', whatsapp_number)
        db.update_setting('announcement_bar', announcement_bar)
        if currency_symbol:
            db.update_setting('currency_symbol', currency_symbol)
        if admin_pin:
            db.update_setting('admin_pin', admin_pin)
            
        flash("Ajustes actualizados correctamente.", 'success')
        return redirect(url_for('admin_settings'))
        
    settings = db.get_settings()
    return render_template('admin/settings.html', current_settings=settings)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Servidor activo en el puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
