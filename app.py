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
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aromaluxe_perfume_secret_key_2026_x87b")
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
    return dict(
        settings=settings,
        global_brands=all_brands,
        is_admin_logged_in=session.get('admin_logged_in', False)
    )

def is_admin():
    return session.get('admin_logged_in', False)

# ----------------- CLIENT ROUTES ----------------- #

@app.route('/')
def index():
    featured_perfumes = db.get_featured_perfumes(limit=8)
    recent_perfumes = db.get_perfumes(order_by='newest', limit=12)
    brands = db.get_all_brands()
    stats = db.get_stats()
    
    # Community / Editorial reviews for the right sidebar (Fragrantica style)
    sidebar_reviews = [
        {
            "brand": "Prada",
            "perfume": "Prada Paradoxe Virtual Flower",
            "author": "Mariabi",
            "image": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=120&auto=format&fit=crop&q=80",
            "slug": "libre-eau-de-parfum"
        },
        {
            "brand": "Fragrance World",
            "perfume": "Nudo Green Iris Exclusif",
            "author": "Brenngal",
            "image": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=120&auto=format&fit=crop&q=80",
            "slug": "tobacco-vanille"
        },
        {
            "brand": "Armani",
            "perfume": "Acqua Di Giò Parfum",
            "author": "nneestorr",
            "image": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=120&auto=format&fit=crop&q=80",
            "slug": "acqua-di-gio-parfum"
        },
        {
            "brand": "Yves Saint Laurent",
            "perfume": "Opium Eau de Toilette (2026)",
            "author": "Horacio G",
            "image": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=120&auto=format&fit=crop&q=80",
            "slug": "baccarat-rouge-540"
        },
        {
            "brand": "Zara",
            "perfume": "Vetiver Pamplemousse Elixir",
            "author": "naso_en_ciernes",
            "image": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=120&auto=format&fit=crop&q=80",
            "slug": "sauvage-eau-de-parfum"
        }
    ]

    # Fragram community lifestyle photos
    fragram_photos = [
        {"title": "Colección de Otoño", "author": "Sofia_Perfumes", "img": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400&auto=format&fit=crop&q=80"},
        {"title": "Noche de Baccarat", "author": "Carlos_Scent", "img": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=400&auto=format&fit=crop&q=80"},
        {"title": "Frasco icónico JPG", "author": "Elena_Fragrance", "img": "https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=400&auto=format&fit=crop&q=80"},
        {"title": "Marly & Rosas", "author": "NicheLover", "img": "https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?w=400&auto=format&fit=crop&q=80"},
        {"title": "Aventus en mano", "author": "KingOfScents", "img": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&auto=format&fit=crop&q=80"}
    ]

    # Fragrantica Category Pills list
    category_pills = [
        "Reseñas Editoriales de Fragancia", "Nuevas Fragancias", "Columnas", "Fragancias Nicho",
        "Noticias de Fragancias", "Fragancias Vintage", "Arte, Libros y Eventos", "Anuncios de Perfumes",
        "Materias primas", "Ahora en Tiendas", "Fragancias y Culturas", "Bath & Body",
        "ENTREVISTAS", "1001 Relatos del Pasado", "Aromas para el Hogar", "Best in Show",
        "Jardín Fragante", "Fragmentos Perfumísticos", "Fragancias Económicas", "Alimentos y Bebidas",
        "Perfumes Naturales", "Charlas de Fragrantica", "Fusiones de Sabores", "Perfumistas",
        "Comprando tu guardarropa de frag", "Guardarropa de fragancias"
    ]

    # Popular 24 perfumes list (as in Fragrantica footer/home)
    popular_24 = [
        "Liquid Brun French Avenue", "Emporio Armani Stronger", "Khamrah Lattafa", "Supremacy Collector's Edition",
        "Imagination Louis Vuitton", "Le Male Le Parfum Jean Paul Gaultier", "Khamrah Qahwa Lattafa", "Y Eau de Parfum Yves Saint Laurent",
        "Club de Nuit Intense Armaf", "Vulcan Feu French Avenue", "Hawas Ice Rasasi", "XJ 1861 Naxos Xerjoff",
        "Le Male Elixir Jean Paul Gaultier", "Angels' Share By Kilian", "Bois Impérial Essential Parfums", "By the Fireplace Maison Margiela",
        "MYSLF Eau de Parfum YSL", "Bleu de Chanel Eau de Parfum", "Le Beau Le Parfum Jean Paul Gaultier", "Jazz Club Maison Margiela",
        "Valentino Uomo Born In Roma", "Tobacco Vanille Tom Ford", "Vibrato Sospiro Perfumes", "Aventus Creed"
    ]

    # Popular 60 brands list (as in Fragrantica footer/home)
    popular_60_brands = [
        "Lattafa Perfumes", "Dior", "Yves Saint Laurent", "Guerlain", "Giorgio Armani",
        "French Avenue", "Tom Ford", "Armaf", "Jean Paul Gaultier", "Chanel",
        "Amouage", "Zara", "Afnan", "Parfums de Marly", "Xerjoff",
        "Versace", "Dolce&Gabbana", "Maison Alhambra", "Louis Vuitton", "By Kilian",
        "Rabanne", "Maison Martin Margiela", "PARIS CORNER", "Byredo", "Rasasi",
        "Carolina Herrera", "Valentino", "Creed", "Diptyque", "Prada",
        "Givenchy", "Rayhaan", "Natura", "Maison Francis Kurkdjian", "Hermès",
        "Mancera", "O Boticário", "Bath & Body Works", "Gucci", "Khadlaj Perfumes",
        "Hugo Boss", "Nishane", "Jo Malone London", "Victoria's Secret", "Lancôme",
        "Initio Parfums Prives", "Burberry", "Mugler", "Montale", "Kayali Fragrances",
        "Etat Libre d'Orange", "Ex Nihilo", "Serge Lutens", "Penhaligon's", "Calvin Klein",
        "Fragrance World", "Bvlgari", "Le Labo", "Azzaro", "Juliette Has A Gun"
    ]

    # Spotlight Perfume for the Left Hero Banner
    spotlight_perfume = db.get_perfume_by_slug("baccarat-rouge-540") or (featured_perfumes[0] if featured_perfumes else None)
    
    return render_template(
        'index.html',
        featured_perfumes=featured_perfumes,
        recent_perfumes=recent_perfumes,
        brands=brands,
        stats=stats,
        sidebar_reviews=sidebar_reviews,
        fragram_photos=fragram_photos,
        category_pills=category_pills,
        popular_24=popular_24,
        popular_60_brands=popular_60_brands,
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
    
    # Build WhatsApp URL
    settings = db.get_settings()
    phone = settings.get('whatsapp_number', '').replace('+', '').replace(' ', '').replace('-', '')
    
    price_str = f"${perfume['price']:.2f}"
    if perfume.get('discount_price'):
        price_str = f"${perfume['discount_price']:.2f} (Antes ${perfume['price']:.2f})"
        
    msg = (
        f"¡Hola! Vengo de su página web y me interesa el perfume *{perfume['name']}* de *{perfume['brand_name']}* "
        f"({perfume.get('concentration', 'Perfume')} - {perfume.get('size_ml', 100)}ml).\n"
        f"Precio: {price_str}.\n"
        f"¿Tienen disponibilidad en stock para entrega o envío?"
    )
    whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
    
    return render_template(
        'detail.html',
        perfume=perfume,
        related=related,
        whatsapp_url=whatsapp_url
    )

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
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    stats = db.get_stats()
    recent_perfumes = db.get_perfumes(order_by='newest', limit=6)
    return render_template('admin/dashboard.html', stats=stats, recent_perfumes=recent_perfumes)

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
                'price': float(request.form.get('price', 0.0)),
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
                'rating': float(request.form.get('rating', 4.5)),
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
                'price': float(request.form.get('price', 0.0)),
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
                'rating': float(request.form.get('rating', 4.5)),
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
