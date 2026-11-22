import sqlite3
import json
import re
import unicodedata
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path(__file__).parent / "perfumes.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        slug TEXT NOT NULL UNIQUE,
        country TEXT,
        website TEXT,
        description TEXT,
        logo_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        slug TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (brand_id) REFERENCES brands (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS perfumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        brand_id INTEGER NOT NULL,
        collection_id INTEGER,
        gender TEXT NOT NULL DEFAULT 'Unisex',
        concentration TEXT DEFAULT 'Eau de Parfum',
        size_ml INTEGER DEFAULT 100,
        presentation TEXT,
        price REAL NOT NULL DEFAULT 0.0,
        price_range TEXT,
        discount_price REAL,
        in_stock INTEGER DEFAULT 1,
        stock_status TEXT DEFAULT 'en_stock',
        stock_quantity INTEGER DEFAULT 5,
        image_url TEXT,
        olfactory_family TEXT,
        year_released INTEGER,
        perfumer TEXT,
        description TEXT,
        accords TEXT,
        top_notes TEXT,
        heart_notes TEXT,
        base_notes TEXT,
        seasons TEXT,
        occasions TEXT,
        longevity TEXT DEFAULT 'Moderada (6-8h)',
        sillage TEXT DEFAULT 'Moderada',
        rating REAL DEFAULT 4.8,
        is_featured INTEGER DEFAULT 0,
        views_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (brand_id) REFERENCES brands (id) ON DELETE RESTRICT,
        FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        perfume_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL DEFAULT 5,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (perfume_id) REFERENCES perfumes (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_perfumes_brand ON perfumes(brand_id);
    CREATE INDEX IF NOT EXISTS idx_perfumes_gender ON perfumes(gender);
    CREATE INDEX IF NOT EXISTS idx_perfumes_stock ON perfumes(in_stock);
    CREATE INDEX IF NOT EXISTS idx_reviews_perfume ON reviews(perfume_id);
    CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);
    """)

    # Ensure default admin user exists
    admin_user = cursor.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
    if not admin_user:
        hashed = generate_password_hash('1234')
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, phone, role)
            VALUES (?, ?, ?, ?, ?)
        """, ('Administrador', 'admin@thefragances.com', hashed, '584121234567', 'admin'))

    # Default settings
    default_settings = [
        ('store_name', 'The Fragance´s'),
        ('store_tagline', 'Alta perfumería, notas olfativas y catálogo exclusivo con atención directa por WhatsApp'),
        ('whatsapp_number', '584121234567'),
        ('currency_symbol', '$'),
        ('admin_pin', '1234'),
        ('announcement_bar', '✨ The Fragance´s | Fragancias 100% Originales & Decants | Pide directamente por WhatsApp sin carritos'),
    ]

    for k, v in default_settings:
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()

# ----------------- USERS & AUTH HELPERS ----------------- #

def create_user(name, email, password, phone=''):
    conn = get_db_connection()
    email_clean = email.strip().lower()
    
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,)).fetchone()
    if existing:
        conn.close()
        return None, "Este correo electrónico ya está registrado."

    hashed = generate_password_hash(password)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, phone, role)
        VALUES (?, ?, ?, ?, 'user')
    """, (name.strip(), email_clean, hashed, phone.strip()))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id, None

def authenticate_user(email, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT id, name, email, phone, role, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_db_connection()
    users = conn.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.created_at, COUNT(r.id) AS review_count
        FROM users u
        LEFT JOIN reviews r ON u.id = r.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(u) for u in users]

# ----------------- REVIEWS HELPERS (REAL SYSTEM) ----------------- #

def add_review(perfume_id, user_id, rating, comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (perfume_id, user_id, rating, comment)
        VALUES (?, ?, ?, ?)
    """, (perfume_id, user_id, rating, comment.strip()))
    conn.commit()
    
    # Recalculate average perfume rating based on real reviews
    avg_row = conn.execute("SELECT AVG(rating) as avg_r FROM reviews WHERE perfume_id = ?", (perfume_id,)).fetchone()
    if avg_row and avg_row['avg_r']:
        new_rating = round(float(avg_row['avg_r']), 1)
        conn.execute("UPDATE perfumes SET rating = ? WHERE id = ?", (new_rating, perfume_id))
        conn.commit()
        
    conn.close()
    return True

def get_perfume_reviews(perfume_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT r.*, u.name as user_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.perfume_id = ?
        ORDER BY r.created_at DESC
    """, (perfume_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_reviews(limit=5):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT r.*, u.name as user_name, p.name as perfume_name, p.slug as perfume_slug, 
               p.image_url, b.name as brand_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN perfumes p ON r.perfume_id = p.id
        JOIN brands b ON p.brand_id = b.id
        ORDER BY r.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_reviews(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT r.*, p.name as perfume_name, p.slug as perfume_slug, b.name as brand_name
        FROM reviews r
        JOIN perfumes p ON r.perfume_id = p.id
        JOIN brands b ON p.brand_id = b.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_review(review_id):
    conn = get_db_connection()
    row = conn.execute("SELECT perfume_id FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if row:
        perfume_id = row['perfume_id']
        conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        # Recalculate
        avg_row = conn.execute("SELECT AVG(rating) as avg_r FROM reviews WHERE perfume_id = ?", (perfume_id,)).fetchone()
        new_rating = round(float(avg_row['avg_r']), 1) if avg_row and avg_row['avg_r'] else 4.8
        conn.execute("UPDATE perfumes SET rating = ? WHERE id = ?", (new_rating, perfume_id))
        conn.commit()
    conn.close()

# ----------------- SETTINGS & BRANDS ----------------- #

def get_settings():
    conn = get_db_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def update_setting(key, value):
    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_all_brands():
    conn = get_db_connection()
    brands = conn.execute("""
        SELECT b.*, COUNT(p.id) AS perfume_count 
        FROM brands b 
        LEFT JOIN perfumes p ON b.id = p.brand_id 
        GROUP BY b.id 
        ORDER BY b.name ASC
    """).fetchall()
    conn.close()
    return [dict(b) for b in brands]

def get_brand_by_id(brand_id):
    conn = get_db_connection()
    brand = conn.execute("SELECT * FROM brands WHERE id = ?", (brand_id,)).fetchone()
    conn.close()
    return dict(brand) if brand else None

def get_brand_by_slug(slug):
    conn = get_db_connection()
    brand = conn.execute("SELECT * FROM brands WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return dict(brand) if brand else None

def create_brand(name, country='', description='', logo_url='', website=''):
    conn = get_db_connection()
    base_slug = slugify(name)
    slug = base_slug
    
    counter = 1
    while True:
        existing = conn.execute("SELECT id FROM brands WHERE slug = ?", (slug,)).fetchone()
        if not existing:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO brands (name, slug, country, description, logo_url, website) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name.strip(), slug, country.strip(), description.strip(), logo_url.strip(), website.strip()))
    conn.commit()
    
    b = conn.execute("SELECT id FROM brands WHERE name = ?", (name.strip(),)).fetchone()
    brand_id = b['id'] if b else cursor.lastrowid
    conn.close()
    return brand_id

def delete_brand(brand_id):
    conn = get_db_connection()
    perfume = conn.execute("SELECT id FROM perfumes WHERE brand_id = ?", (brand_id,)).fetchone()
    if perfume:
        conn.close()
        return False, "No puedes eliminar una marca que tiene perfumes asignados."
    conn.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
    conn.commit()
    conn.close()
    return True, "Marca eliminada con éxito."

# ----------------- COLLECTIONS ----------------- #

def get_collections_by_brand(brand_id):
    conn = get_db_connection()
    cols = conn.execute("SELECT * FROM collections WHERE brand_id = ? ORDER BY name ASC", (brand_id,)).fetchall()
    conn.close()
    return [dict(c) for c in cols]

def get_all_collections():
    conn = get_db_connection()
    cols = conn.execute("""
        SELECT c.*, b.name as brand_name 
        FROM collections c 
        JOIN brands b ON c.brand_id = b.id 
        ORDER BY b.name ASC, c.name ASC
    """).fetchall()
    conn.close()
    return [dict(c) for c in cols]

def create_collection(brand_id, name, description=''):
    conn = get_db_connection()
    slug = slugify(name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO collections (brand_id, name, slug, description) VALUES (?, ?, ?, ?)",
                   (brand_id, name.strip(), slug, description.strip()))
    conn.commit()
    col_id = cursor.lastrowid
    conn.close()
    return col_id

def delete_collection(collection_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    conn.commit()
    conn.close()

# ----------------- PERFUMES ----------------- #

def parse_perfume_row(row):
    if not row:
        return None
    d = dict(row)
    for field in ['accords', 'top_notes', 'heart_notes', 'base_notes', 'seasons', 'occasions']:
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
        else:
            d[field] = []
    return d

def get_perfumes(search=None, brand_id=None, gender=None, in_stock_only=False, accord=None, order_by='featured', limit=50, offset=0):
    conn = get_db_connection()
    query = """
        SELECT p.*, b.name AS brand_name, b.slug AS brand_slug, c.name AS collection_name
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        LEFT JOIN collections c ON p.collection_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        s = f"%{search.strip()}%"
        query += """ AND (
            p.name LIKE ? OR 
            b.name LIKE ? OR 
            p.olfactory_family LIKE ? OR 
            p.top_notes LIKE ? OR 
            p.heart_notes LIKE ? OR 
            p.base_notes LIKE ? OR 
            p.accords LIKE ?
        )"""
        params.extend([s, s, s, s, s, s, s])

    if brand_id:
        query += " AND p.brand_id = ?"
        params.append(brand_id)

    if gender and gender.lower() != 'todos':
        if gender.lower() in ['hombre', 'masculino']:
            query += " AND (LOWER(p.gender) = 'hombre' OR LOWER(p.gender) = 'masculino')"
        elif gender.lower() in ['mujer', 'femenino']:
            query += " AND (LOWER(p.gender) = 'mujer' OR LOWER(p.gender) = 'femenino')"
        else:
            query += " AND LOWER(p.gender) = LOWER(?)"
            params.append(gender)

    if in_stock_only:
        query += " AND p.in_stock = 1"

    if accord:
        query += " AND p.accords LIKE ?"
        params.append(f"%{accord}%")

    if order_by == 'price_asc':
        query += " ORDER BY p.price ASC"
    elif order_by == 'price_desc':
        query += " ORDER BY p.price DESC"
    elif order_by == 'name_asc':
        query += " ORDER BY p.name ASC"
    elif order_by == 'newest':
        query += " ORDER BY p.created_at DESC"
    elif order_by == 'rating':
        query += " ORDER BY p.rating DESC"
    else:
        query += " ORDER BY p.is_featured DESC, p.in_stock DESC, p.id ASC"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [parse_perfume_row(r) for r in rows]

def get_perfumes_count(search=None, brand_id=None, gender=None, in_stock_only=False, accord=None):
    conn = get_db_connection()
    query = """
        SELECT COUNT(p.id) as count
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        WHERE 1=1
    """
    params = []

    if search:
        s = f"%{search.strip()}%"
        query += """ AND (
            p.name LIKE ? OR 
            b.name LIKE ? OR 
            p.olfactory_family LIKE ? OR 
            p.top_notes LIKE ? OR 
            p.heart_notes LIKE ? OR 
            p.base_notes LIKE ? OR 
            p.accords LIKE ?
        )"""
        params.extend([s, s, s, s, s, s, s])

    if brand_id:
        query += " AND p.brand_id = ?"
        params.append(brand_id)

    if gender and gender.lower() != 'todos':
        if gender.lower() in ['hombre', 'masculino']:
            query += " AND (LOWER(p.gender) = 'hombre' OR LOWER(p.gender) = 'masculino')"
        elif gender.lower() in ['mujer', 'femenino']:
            query += " AND (LOWER(p.gender) = 'mujer' OR LOWER(p.gender) = 'femenino')"
        else:
            query += " AND LOWER(p.gender) = LOWER(?)"
            params.append(gender)

    if in_stock_only:
        query += " AND p.in_stock = 1"

    if accord:
        query += " AND p.accords LIKE ?"
        params.append(f"%{accord}%")

    row = conn.execute(query, params).fetchone()
    conn.close()
    return row['count'] if row else 0

def get_featured_perfumes(limit=8):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.*, b.name AS brand_name, b.slug AS brand_slug
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        WHERE p.is_featured = 1
        ORDER BY p.in_stock DESC, p.id ASC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [parse_perfume_row(r) for r in rows]

def get_perfume_by_id(perfume_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT p.*, b.name AS brand_name, b.slug AS brand_slug, b.country AS brand_country, c.name AS collection_name
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        LEFT JOIN collections c ON p.collection_id = c.id
        WHERE p.id = ?
    """, (perfume_id,)).fetchone()
    conn.close()
    return parse_perfume_row(row)

def get_perfume_by_slug(slug):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT p.*, b.name AS brand_name, b.slug AS brand_slug, b.country AS brand_country, c.name AS collection_name
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        LEFT JOIN collections c ON p.collection_id = c.id
        WHERE p.slug = ?
    """, (slug,)).fetchone()
    
    if row:
        conn.execute("UPDATE perfumes SET views_count = views_count + 1 WHERE slug = ?", (slug,))
        conn.commit()

    conn.close()
    return parse_perfume_row(row)

def get_related_perfumes(brand_id, exclude_id, limit=4):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.*, b.name AS brand_name, b.slug AS brand_slug
        FROM perfumes p
        JOIN brands b ON p.brand_id = b.id
        WHERE p.brand_id = ? AND p.id != ?
        ORDER BY p.in_stock DESC, p.rating DESC
        LIMIT ?
    """, (brand_id, exclude_id, limit)).fetchall()
    conn.close()
    return [parse_perfume_row(r) for r in rows]

def toggle_perfume_stock(perfume_id):
    conn = get_db_connection()
    row = conn.execute("SELECT in_stock, stock_status FROM perfumes WHERE id = ?", (perfume_id,)).fetchone()
    if not row:
        conn.close()
        return None
    new_in_stock = 0 if row['in_stock'] == 1 else 1
    new_status = 'en_stock' if new_in_stock == 1 else 'agotado'
    conn.execute("UPDATE perfumes SET in_stock = ?, stock_status = ? WHERE id = ?", (new_in_stock, new_status, perfume_id))
    conn.commit()
    conn.close()
    return {"id": perfume_id, "in_stock": new_in_stock, "stock_status": new_status}

def save_perfume(data, perfume_id=None):
    conn = get_db_connection()
    name = data['name'].strip()
    slug = slugify(f"{data.get('brand_name', '')}-{name}" if data.get('brand_name') else name)

    if perfume_id:
        slug_check = conn.execute("SELECT id FROM perfumes WHERE slug = ? AND id != ?", (slug, perfume_id)).fetchone()
    else:
        slug_check = conn.execute("SELECT id FROM perfumes WHERE slug = ?", (slug,)).fetchone()
    if slug_check:
        slug = f"{slug}-{int(data.get('size_ml', 100))}"

    accords_json = json.dumps(data.get('accords', []))
    top_notes_json = json.dumps(data.get('top_notes', []))
    heart_notes_json = json.dumps(data.get('heart_notes', []))
    base_notes_json = json.dumps(data.get('base_notes', []))
    seasons_json = json.dumps(data.get('seasons', []))
    occasions_json = json.dumps(data.get('occasions', []))

    in_stock = int(data.get('in_stock', 1))
    stock_status = data.get('stock_status', 'en_stock' if in_stock == 1 else 'agotado')

    cursor = conn.cursor()
    if perfume_id:
        cursor.execute("""
            UPDATE perfumes SET
                name = ?, slug = ?, brand_id = ?, collection_id = ?, gender = ?,
                concentration = ?, size_ml = ?, presentation = ?, price = ?, price_range = ?,
                discount_price = ?, in_stock = ?, stock_status = ?, stock_quantity = ?, image_url = ?,
                olfactory_family = ?, year_released = ?, perfumer = ?, description = ?,
                accords = ?, top_notes = ?, heart_notes = ?, base_notes = ?,
                seasons = ?, occasions = ?, longevity = ?, sillage = ?,
                rating = ?, is_featured = ?
            WHERE id = ?
        """, (
            name, slug, data['brand_id'], data.get('collection_id') or None, data.get('gender', 'Unisex'),
            data.get('concentration', 'Eau de Parfum'), data.get('size_ml', 100), data.get('presentation', ''),
            data.get('price', 0.0), data.get('price_range', ''), data.get('discount_price') or None,
            in_stock, stock_status, data.get('stock_quantity', 5),
            data.get('image_url', ''), data.get('olfactory_family', ''), data.get('year_released') or None,
            data.get('perfumer', ''), data.get('description', ''),
            accords_json, top_notes_json, heart_notes_json, base_notes_json,
            seasons_json, occasions_json, data.get('longevity', 'Moderada (6-8h)'),
            data.get('sillage', 'Moderada'), data.get('rating', 4.8), int(data.get('is_featured', 0)),
            perfume_id
        ))
        result_id = perfume_id
    else:
        cursor.execute("""
            INSERT INTO perfumes (
                name, slug, brand_id, collection_id, gender, concentration, size_ml, presentation,
                price, price_range, discount_price, in_stock, stock_status, stock_quantity, image_url,
                olfactory_family, year_released, perfumer, description, accords,
                top_notes, heart_notes, base_notes, seasons, occasions, longevity,
                sillage, rating, is_featured
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, slug, data['brand_id'], data.get('collection_id') or None, data.get('gender', 'Unisex'),
            data.get('concentration', 'Eau de Parfum'), data.get('size_ml', 100), data.get('presentation', ''),
            data.get('price', 0.0), data.get('price_range', ''), data.get('discount_price') or None,
            in_stock, stock_status, data.get('stock_quantity', 5),
            data.get('image_url', ''), data.get('olfactory_family', ''), data.get('year_released') or None,
            data.get('perfumer', ''), data.get('description', ''),
            accords_json, top_notes_json, heart_notes_json, base_notes_json,
            seasons_json, occasions_json, data.get('longevity', 'Moderada (6-8h)'),
            data.get('sillage', 'Moderada'), data.get('rating', 4.8), int(data.get('is_featured', 0))
        ))
        result_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return result_id

def delete_perfume(perfume_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM perfumes WHERE id = ?", (perfume_id,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db_connection()
    total_perfumes = conn.execute("SELECT COUNT(*) FROM perfumes").fetchone()[0]
    total_in_stock = conn.execute("SELECT COUNT(*) FROM perfumes WHERE in_stock = 1").fetchone()[0]
    total_out_of_stock = conn.execute("SELECT COUNT(*) FROM perfumes WHERE in_stock = 0").fetchone()[0]
    total_brands = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role != 'admin'").fetchone()[0]
    total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    conn.close()
    return {
        "total_perfumes": total_perfumes,
        "in_stock": total_in_stock,
        "out_of_stock": total_out_of_stock,
        "total_brands": total_brands,
        "total_users": total_users,
        "total_reviews": total_reviews
    }
