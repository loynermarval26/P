import json
from database import init_db, get_db_connection, create_brand, create_collection, save_perfume

def run_seed():
    print("Inicializando base de datos...")
    init_db()
    conn = get_db_connection()

    # Check if perfumes already exist
    existing = conn.execute("SELECT COUNT(*) FROM perfumes").fetchone()[0]
    if existing > 0:
        print(f"La base de datos ya contiene {existing} perfumes. Omitiendo seed inicial.")
        conn.close()
        return

    print("Creando marcas...")
    brands_data = [
        {"name": "Dior", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&auto=format&fit=crop&q=80", "description": "Casa de alta costura y perfumería francesa fundada por Christian Dior en 1946."},
        {"name": "Chanel", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400&auto=format&fit=crop&q=80", "description": "Lujo atemporal y elegancia parisina fundada por Gabrielle 'Coco' Chanel."},
        {"name": "Creed", "country": "Francia / Reino Unido", "logo_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=400&auto=format&fit=crop&q=80", "description": "Dinastía de perfumería artesanal de lujo fundada en Londres en 1760."},
        {"name": "Maison Francis Kurkdjian", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=400&auto=format&fit=crop&q=80", "description": "Casa parisina de perfumería nicho de altísima gama creada por el maestro perfumista Francis Kurkdjian."},
        {"name": "Tom Ford", "country": "Estados Unidos", "logo_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400&auto=format&fit=crop&q=80", "description": "Seducción, opulencia y modernidad con colecciones icónicas de Private Blend."},
        {"name": "Giorgio Armani", "country": "Italia", "logo_url": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=400&auto=format&fit=crop&q=80", "description": "Elegancia italiana contemporánea y frescura mediterránea inconfundible."},
        {"name": "Yves Saint Laurent", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=400&auto=format&fit=crop&q=80", "description": "Vanguardia, sensualidad y libertad audaz desde París."},
        {"name": "Jean Paul Gaultier", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=400&auto=format&fit=crop&q=80", "description": "Audacia, frascos icónicos y acordes gourmand magnéticos."},
        {"name": "Versace", "country": "Italia", "logo_url": "https://images.unsplash.com/photo-1615397349754-cfa2066a298e?w=400&auto=format&fit=crop&q=80", "description": "Mitología griega, glamour italiano y pasión vibrante."},
        {"name": "Parfums de Marly", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?w=400&auto=format&fit=crop&q=80", "description": "Reviviendo el esplendor de la corte real de Luis XV y el arte de la perfumería francesa."},
        {"name": "Kilian Paris", "country": "Francia", "logo_url": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?w=400&auto=format&fit=crop&q=80", "description": "Lujo eco-consciente inspirado en herencias de coñac y noches seductoras."}
    ]

    brand_ids = {}
    for b in brands_data:
        bid = create_brand(b['name'], b['country'], b['description'], b['logo_url'])
        brand_ids[b['name']] = bid

    print("Creando colecciones...")
    col_sauvage = create_collection(brand_ids["Dior"], "Sauvage Collection", "La línea masculina más aclamada del mundo.")
    col_bleu = create_collection(brand_ids["Chanel"], "Bleu de Chanel", "El elogio de la libertad masculina.")
    col_private_blend = create_collection(brand_ids["Tom Ford"], "Private Blend", "Fragancias artesanales sin límites de creatividad.")
    col_acquadigio = create_collection(brand_ids["Giorgio Armani"], "Acqua Di Giò", "La leyenda acuática por excelencia.")

    print("Cargando perfumes con pirámide olfativa y acordes estilo Fragrantica...")

    perfumes_catalog = [
        {
            "name": "Sauvage Eau de Parfum",
            "brand_id": brand_ids["Dior"],
            "brand_name": "Dior",
            "collection_id": col_sauvage,
            "gender": "Hombre",
            "concentration": "Eau de Parfum",
            "size_ml": 100,
            "price": 145.0,
            "discount_price": 130.0,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 8,
            "image_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Oriental Fougère",
            "year_released": 2018,
            "perfumer": "François Demachy",
            "description": "Una interpretación voluptuosa y sensual de Sauvage. La frescura jugosa de la bergamota de Calabria se une a la carnalidad de un acorde de absoluto de vainilla de Papúa Nueva Guinea.",
            "accords": [
                {"name": "Cítrico", "color": "#EAB308", "percent": 90},
                {"name": "Ámbar", "color": "#D97706", "percent": 82},
                {"name": "Especiado Fresco", "color": "#06B6D4", "percent": 78},
                {"name": "Aromático", "color": "#10B981", "percent": 74},
                {"name": "Avainillado", "color": "#EC4899", "percent": 65},
                {"name": "Amaderado", "color": "#78350F", "percent": 58}
            ],
            "top_notes": ["Bergamota de Calabria"],
            "heart_notes": ["Pimienta de Sichuan", "Lavanda", "Anís estrellado", "Nuez moscada"],
            "base_notes": ["Ambroxan", "Vainilla de Papúa Nueva Guinea"],
            "seasons": ["Primavera", "Otoño", "Verano", "Invierno"],
            "occasions": ["Día", "Noche", "Versátil", "Citas"],
            "longevity": "Muy Duradera (8-10h)",
            "sillage": "Pesada",
            "rating": 4.7,
            "is_featured": 1
        },
        {
            "name": "Bleu de Chanel Eau de Parfum",
            "brand_id": brand_ids["Chanel"],
            "brand_name": "Chanel",
            "collection_id": col_bleu,
            "gender": "Hombre",
            "concentration": "Eau de Parfum",
            "size_ml": 100,
            "price": 160.0,
            "discount_price": None,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 4,
            "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Amaderada Aromática",
            "year_released": 2014,
            "perfumer": "Jacques Polge",
            "description": "Un tributo a la libertad masculina en una fragancia amaderada aromática de estela cautivadora. Un aroma atemporal encerrado en un frasco de un azul profundo e impenetrable.",
            "accords": [
                {"name": "Cítrico", "color": "#EAB308", "percent": 88},
                {"name": "Ámbar", "color": "#D97706", "percent": 80},
                {"name": "Amaderado", "color": "#78350F", "percent": 75},
                {"name": "Aromático", "color": "#10B981", "percent": 70},
                {"name": "Especiado Cálido", "color": "#DC2626", "percent": 62},
                {"name": "Ahumado", "color": "#475569", "percent": 55}
            ],
            "top_notes": ["Pomelo", "Limón", "Menta", "Pimienta rosa", "Bergamota", "Aldehídos", "Cilantro"],
            "heart_notes": ["Jengibre", "Jazmín", "Nuez moscada", "Melón"],
            "base_notes": ["Incienso", "Ámbar", "Cedro", "Sándalo", "Pachulí", "Amberwood", "Ládano"],
            "seasons": ["Primavera", "Otoño", "Verano"],
            "occasions": ["Día", "Noche", "Oficina", "Elegante"],
            "longevity": "Duradera (7-9h)",
            "sillage": "Moderada",
            "rating": 4.8,
            "is_featured": 1
        },
        {
            "name": "Aventus",
            "brand_id": brand_ids["Creed"],
            "brand_name": "Creed",
            "collection_id": None,
            "gender": "Hombre",
            "concentration": "Eau de Parfum",
            "size_ml": 100,
            "price": 385.0,
            "discount_price": 350.0,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 3,
            "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Chipre Frutal",
            "year_released": 2010,
            "perfumer": "Jean-Christophe Hérault & Erwin Creed",
            "description": "Inspirado en la vida dramática de un emperador histórico, celebrando la fuerza, el poder y el éxito. Es el perfume nicho más influyente de la perfumería moderna.",
            "accords": [
                {"name": "Frutal", "color": "#F97316", "percent": 95},
                {"name": "Ahumado", "color": "#475569", "percent": 82},
                {"name": "Amaderado", "color": "#78350F", "percent": 75},
                {"name": "Dulce", "color": "#EC4899", "percent": 68},
                {"name": "Cuero", "color": "#713F12", "percent": 60}
            ],
            "top_notes": ["Piña", "Bergamota", "Grosellas negras", "Manzana"],
            "heart_notes": ["Abedul", "Pachulí", "Jazmín de Marruecos", "Rosa"],
            "base_notes": ["Almizcle", "Musgo de roble", "Ámbar gris", "Vainilla"],
            "seasons": ["Primavera", "Verano", "Otoño"],
            "occasions": ["Día", "Noche", "Especial", "Firma"],
            "longevity": "Muy Duradera (8-10h)",
            "sillage": "Moderada a Fuerte",
            "rating": 4.9,
            "is_featured": 1
        },
        {
            "name": "Baccarat Rouge 540",
            "brand_id": brand_ids["Maison Francis Kurkdjian"],
            "brand_name": "Maison Francis Kurkdjian",
            "collection_id": None,
            "gender": "Unisex",
            "concentration": "Eau de Parfum",
            "size_ml": 70,
            "price": 320.0,
            "discount_price": None,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 2,
            "image_url": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Ámbar Floral",
            "year_released": 2015,
            "perfumer": "Francis Kurkdjian",
            "description": "Luminoso y sofisticado, Baccarat Rouge 540 se posa sobre la piel como una brisa floral, ambarina y amaderada. Una alquimia poética creada para celebrar el 250 aniversario del célebre cristalero.",
            "accords": [
                {"name": "Ámbar", "color": "#D97706", "percent": 96},
                {"name": "Amaderado", "color": "#78350F", "percent": 84},
                {"name": "Especiado Cálido", "color": "#DC2626", "percent": 76},
                {"name": "Aromático", "color": "#10B981", "percent": 65},
                {"name": "Metálico / Dulce", "color": "#F43F5E", "percent": 62}
            ],
            "top_notes": ["Azafrán", "Jazmín"],
            "heart_notes": ["Amberwood", "Ámbar gris"],
            "base_notes": ["Resina de abeto", "Cedro"],
            "seasons": ["Otoño", "Invierno", "Primavera"],
            "occasions": ["Noche", "Citas", "Eventos Exclusivos"],
            "longevity": "Eterna (+12h)",
            "sillage": "Enorme",
            "rating": 4.8,
            "is_featured": 1
        },
        {
            "name": "Tobacco Vanille",
            "brand_id": brand_ids["Tom Ford"],
            "brand_name": "Tom Ford",
            "collection_id": col_private_blend,
            "gender": "Unisex",
            "concentration": "Eau de Parfum",
            "size_ml": 50,
            "price": 295.0,
            "discount_price": 270.0,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 5,
            "image_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Ámbar Especiada",
            "year_released": 2007,
            "perfumer": "Olivier Gillotin",
            "description": "La opulencia, la calidez y las especias de un club de caballeros londinense reinventado con haba tonka cremosa, vainilla, cacao y frutos secos.",
            "accords": [
                {"name": "Avainillado", "color": "#EC4899", "percent": 95},
                {"name": "Tabaco", "color": "#78350F", "percent": 90},
                {"name": "Dulce", "color": "#F43F5E", "percent": 85},
                {"name": "Especiado Cálido", "color": "#DC2626", "percent": 80},
                {"name": "Frutos Secos", "color": "#D97706", "percent": 65}
            ],
            "top_notes": ["Hoja de tabaco", "Notas especiadas"],
            "heart_notes": ["Vainilla", "Cacao", "Haba tonka", "Flor del tabaco"],
            "base_notes": ["Frutos secos", "Notas amaderadas"],
            "seasons": ["Otoño", "Invierno"],
            "occasions": ["Noche", "Citas", "Clima Frío"],
            "longevity": "Eterna (+12h)",
            "sillage": "Pesada",
            "rating": 4.9,
            "is_featured": 1
        },
        {
            "name": "Acqua Di Giò Parfum",
            "brand_id": brand_ids["Giorgio Armani"],
            "brand_name": "Giorgio Armani",
            "collection_id": col_acquadigio,
            "gender": "Hombre",
            "concentration": "Parfum",
            "size_ml": 100,
            "price": 155.0,
            "discount_price": None,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 6,
            "image_url": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Acuática Amaderada",
            "year_released": 2023,
            "perfumer": "Alberto Morillas",
            "description": "Una intensa y vibrante interpretación de la legendaria fragancia marina, enriquecida con incienso místico y notas minerales de las costas de Pantelleria.",
            "accords": [
                {"name": "Marino", "color": "#0284C7", "percent": 92},
                {"name": "Aromático", "color": "#10B981", "percent": 86},
                {"name": "Ahumado", "color": "#475569", "percent": 75},
                {"name": "Cítrico", "color": "#EAB308", "percent": 70},
                {"name": "Amaderado", "color": "#78350F", "percent": 64}
            ],
            "top_notes": ["Notas marinas", "Bergamota"],
            "heart_notes": ["Romero", "Salvia esclarea", "Geranio"],
            "base_notes": ["Incienso", "Pachulí"],
            "seasons": ["Primavera", "Verano", "Otoño"],
            "occasions": ["Día", "Noche", "Firma", "Oficina"],
            "longevity": "Duradera (7-9h)",
            "sillage": "Moderada",
            "rating": 4.7,
            "is_featured": 0
        },
        {
            "name": "Libre Eau de Parfum",
            "brand_id": brand_ids["Yves Saint Laurent"],
            "brand_name": "Yves Saint Laurent",
            "collection_id": None,
            "gender": "Mujer",
            "concentration": "Eau de Parfum",
            "size_ml": 90,
            "price": 140.0,
            "discount_price": 125.0,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 7,
            "image_url": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Ámbar Fougère",
            "year_released": 2019,
            "perfumer": "Anne Flipo & Carlos Benaïm",
            "description": "La fragancia de la libertad absoluta. La sensualidad ardiente del azahar de Marruecos combinada con la audacia de la lavanda francesa en un giro puramente femenino.",
            "accords": [
                {"name": "Floral Blanco", "color": "#EC4899", "percent": 90},
                {"name": "Cítrico", "color": "#EAB308", "percent": 82},
                {"name": "Lavanda", "color": "#8B5CF6", "percent": 78},
                {"name": "Avainillado", "color": "#F43F5E", "percent": 72},
                {"name": "Ámbar", "color": "#D97706", "percent": 65}
            ],
            "top_notes": ["Lavanda", "Mandarina", "Grosellas negras", "Petit grain"],
            "heart_notes": ["Lavanda", "Flor de azahar del naranjo", "Jazmín"],
            "base_notes": ["Vainilla de Madagascar", "Almizcle", "Cedro", "Ámbar gris"],
            "seasons": ["Otoño", "Primavera", "Invierno"],
            "occasions": ["Día", "Noche", "Elegante", "Citas"],
            "longevity": "Muy Duradera (8-10h)",
            "sillage": "Moderada a Fuerte",
            "rating": 4.6,
            "is_featured": 1
        },
        {
            "name": "Le Male Elixir",
            "brand_id": brand_ids["Jean Paul Gaultier"],
            "brand_name": "Jean Paul Gaultier",
            "collection_id": None,
            "gender": "Hombre",
            "concentration": "Parfum",
            "size_ml": 125,
            "price": 150.0,
            "discount_price": None,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 5,
            "image_url": "https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Ámbar Fougère",
            "year_released": 2023,
            "perfumer": "Quentin Bisch",
            "description": "¡Un marinero que enciende la pasión al rojo vivo! Una fragancia incandescente que mezcla miel dorada, haba tonka fundente y lavanda carnal.",
            "accords": [
                {"name": "Avainillado", "color": "#EC4899", "percent": 94},
                {"name": "Dulce", "color": "#F43F5E", "percent": 90},
                {"name": "Miel", "color": "#D97706", "percent": 84},
                {"name": "Lavanda", "color": "#8B5CF6", "percent": 76},
                {"name": "Ámbar", "color": "#B45309", "percent": 70}
            ],
            "top_notes": ["Lavanda", "Menta"],
            "heart_notes": ["Vainilla", "Benjuí"],
            "base_notes": ["Miel", "Haba tonka", "Tabaco"],
            "seasons": ["Otoño", "Invierno"],
            "occasions": ["Noche", "Fiesta", "Citas"],
            "longevity": "Eterna (+12h)",
            "sillage": "Enorme",
            "rating": 4.9,
            "is_featured": 1
        },
        {
            "name": "Eros Flame",
            "brand_id": brand_ids["Versace"],
            "brand_name": "Versace",
            "collection_id": None,
            "gender": "Hombre",
            "concentration": "Eau de Parfum",
            "size_ml": 100,
            "price": 110.0,
            "discount_price": 95.0,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 10,
            "image_url": "https://images.unsplash.com/photo-1615397349754-cfa2066a298e?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Amaderada Especiada",
            "year_released": 2018,
            "perfumer": "Olivier Pescheux",
            "description": "Para un hombre fuerte, apasionado y seguro de sí mismo. Toca las emociones profundas mediante el contraste entre notas cítricas luminosas y un fondo amaderado y avainillado.",
            "accords": [
                {"name": "Cítrico", "color": "#EAB308", "percent": 88},
                {"name": "Especiado Cálido", "color": "#DC2626", "percent": 84},
                {"name": "Avainillado", "color": "#EC4899", "percent": 76},
                {"name": "Amaderado", "color": "#78350F", "percent": 70},
                {"name": "Aromático", "color": "#10B981", "percent": 65}
            ],
            "top_notes": ["Mandarina", "Pimienta de Madagascar", "Limón", "Chinotto", "Romero"],
            "heart_notes": ["Pimienta", "Geranio", "Rosa"],
            "base_notes": ["Vainilla", "Haba tonka", "Sándalo", "Cedro de Texas", "Pachulí", "Musgo de roble"],
            "seasons": ["Otoño", "Invierno", "Primavera"],
            "occasions": ["Noche", "Citas", "Salidas"],
            "longevity": "Muy Duradera (8-10h)",
            "sillage": "Pesada",
            "rating": 4.6,
            "is_featured": 0
        },
        {
            "name": "Delina Eau de Parfum",
            "brand_id": brand_ids["Parfums de Marly"],
            "brand_name": "Parfums de Marly",
            "collection_id": None,
            "gender": "Mujer",
            "concentration": "Eau de Parfum",
            "size_ml": 75,
            "price": 340.0,
            "discount_price": None,
            "in_stock": 1,
            "stock_status": "en_stock",
            "stock_quantity": 3,
            "image_url": "https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Floral Frutal",
            "year_released": 2017,
            "perfumer": "Quentin Bisch",
            "description": "Una escultura floral moderna compuesta por una sobredosis de rosa turca combinada con facetas de lirio de los valles y peonía, envuelta en ruibarbo crujiente y madera de cachemira.",
            "accords": [
                {"name": "Rosas", "color": "#EC4899", "percent": 98},
                {"name": "Frutal", "color": "#F97316", "percent": 85},
                {"name": "Floral", "color": "#F43F5E", "percent": 80},
                {"name": "Fresco", "color": "#06B6D4", "percent": 72},
                {"name": "Almizclado", "color": "#64748B", "percent": 65}
            ],
            "top_notes": ["Lichi", "Ruibarbo", "Bergamota", "Nuez moscada"],
            "heart_notes": ["Rosa turca", "Peonía", "Almizcle", "Petalia", "Vainilla"],
            "base_notes": ["Cashmeran", "Cedro", "Incienso", "Vetiver de Haití"],
            "seasons": ["Primavera", "Verano"],
            "occasions": ["Día", "Elegante", "Citas", "Bodas"],
            "longevity": "Muy Duradera (9-11h)",
            "sillage": "Pesada",
            "rating": 4.8,
            "is_featured": 1
        },
        {
            "name": "Angels' Share",
            "brand_id": brand_ids["Kilian Paris"],
            "brand_name": "Kilian Paris",
            "collection_id": None,
            "gender": "Unisex",
            "concentration": "Eau de Parfum",
            "size_ml": 50,
            "price": 245.0,
            "discount_price": 225.0,
            "in_stock": 0,
            "stock_status": "agotado",
            "stock_quantity": 0,
            "image_url": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?w=600&auto=format&fit=crop&q=80",
            "olfactory_family": "Ámbar Vainilla",
            "year_released": 2020,
            "perfumer": "Benoist Lapouza",
            "description": "Inspirado en la herencia de octava generación del coñac Hennessy. Angels' Share contiene esencia de coñac derivada del licor para darle un color caramelo natural.",
            "accords": [
                {"name": "Licoroso", "color": "#D97706", "percent": 96},
                {"name": "Canela", "color": "#DC2626", "percent": 88},
                {"name": "Avainillado", "color": "#EC4899", "percent": 82},
                {"name": "Amaderado", "color": "#78350F", "percent": 75},
                {"name": "Dulce", "color": "#F43F5E", "percent": 70}
            ],
            "top_notes": ["Coñac"],
            "heart_notes": ["Canela", "Haba tonka", "Roble"],
            "base_notes": ["Praliné", "Vainilla", "Sándalo"],
            "seasons": ["Otoño", "Invierno"],
            "occasions": ["Noche", "Citas", "Fiestas de Lujo"],
            "longevity": "Muy Duradera (8-10h)",
            "sillage": "Moderada a Fuerte",
            "rating": 4.9,
            "is_featured": 1
        }
    ]

    for p in perfumes_catalog:
        save_perfume(p)

    conn.close()
    print("Seed completado exitosamente con 11 perfumes icónicos y marcas!")

if __name__ == "__main__":
    run_seed()
