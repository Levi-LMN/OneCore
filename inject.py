"""
Import November Stock Data into Liquor Store System
This script imports products with their base bottle size as the variant.
Each product size (e.g., County 750ml, County 250ml) is a separate product.
Tots/glasses will be added manually later as additional variants.
"""

from app import app, db
from models import Category, Size, Product, ProductVariant, User
from datetime import datetime, date

# Product data extracted from November stocks PDF
# Each size is a separate product (e.g., "Black & White 1L" and "Black & White 750ML" are different products)
PRODUCTS = [
    # BEERS
    {"name": "Snapp", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 181, "opening_stock": 0},
    {"name": "Guarana", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 181, "opening_stock": 15},
    {"name": "Black Ice", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 181, "opening_stock": 19},
    {"name": "Pineapple Punch", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 181, "opening_stock": 19},
    {"name": "Tusker Malt", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 247, "opening_stock": 0},
    {"name": "Heineken", "category": "Beers", "size": "Can/Bottle", "selling_price": 350, "buying_price": 287, "opening_stock": 0},
    {"name": "Tusker Lager", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 203, "opening_stock": 19},
    {"name": "Faxe", "category": "Beers", "size": "Can/Bottle", "selling_price": 320, "buying_price": 263, "opening_stock": 0},
    {"name": "Martens Beer", "category": "Beers", "size": "Can/Bottle", "selling_price": 350, "buying_price": 263, "opening_stock": 10},
    {"name": "Tusker Lite", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 247, "opening_stock": 0},
    {"name": "Guinness", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 220, "opening_stock": 22},
    {"name": "Kingfisher", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 192, "opening_stock": 0},
    {"name": "Hunters Gold", "category": "Beers", "size": "Can/Bottle", "selling_price": 250, "buying_price": 203, "opening_stock": 0},
    {"name": "Balozi", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 203, "opening_stock": 15},
    {"name": "Pilsner", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 203, "opening_stock": 0},
    {"name": "Whitecap", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 220, "opening_stock": 18},
    {"name": "Savannah", "category": "Beers", "size": "Can/Bottle", "selling_price": 200, "buying_price": 240, "opening_stock": 0},
    {"name": "KO", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 220, "opening_stock": 10},
    {"name": "Tusker Cider", "category": "Beers", "size": "Can/Bottle", "selling_price": 300, "buying_price": 241, "opening_stock": 14},
    {"name": "Banana Beer", "category": "Beers", "size": "Can/Bottle", "selling_price": 130, "buying_price": 72, "opening_stock": 33},

    # SPIRITS - 1 LITRE
    {"name": "Flirt Vodka 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 1700, "buying_price": 1030, "opening_stock": 1},
    {"name": "Ballantines 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 3600, "buying_price": 2679, "opening_stock": 2},
    {"name": "Double Black 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 6800, "buying_price": 5550, "opening_stock": 2},
    {"name": "J & B 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2700, "buying_price": 2017, "opening_stock": 2},
    {"name": "Red Label 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2500, "buying_price": 2050, "opening_stock": 3},
    {"name": "Black Label 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 4500, "buying_price": 3810, "opening_stock": 5},
    {"name": "Black & White 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2000, "buying_price": 1525, "opening_stock": 4},
    {"name": "Jagermeister 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 3700, "buying_price": 3100, "opening_stock": 2},
    {"name": "Jameson 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 3700, "buying_price": 3024, "opening_stock": 3},
    {"name": "Jack Daniels 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 4500, "buying_price": 3850, "opening_stock": 3},
    {"name": "Captain Morgan Spiced 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2800, "buying_price": 2184, "opening_stock": 5},
    {"name": "Malibu 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2500, "buying_price": 1575, "opening_stock": 2},
    {"name": "4th Street 1.5L", "category": "Spirits", "size": "1 Litre", "selling_price": 2000, "buying_price": 1680, "opening_stock": 1},
    {"name": "8PM 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 1300, "buying_price": 1000, "opening_stock": 4},
    {"name": "Jim Beam 1L", "category": "Spirits", "size": "1 Litre", "selling_price": 2600, "buying_price": 2415, "opening_stock": 2},

    # SPIRITS - 750ML
    {"name": "Black & White 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1500, "buying_price": 1155, "opening_stock": 3},
    {"name": "Jim Beam 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1700, "buying_price": 2195, "opening_stock": 2},
    {"name": "Black Label 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3600, "buying_price": 3077, "opening_stock": 3},
    {"name": "Jameson 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2750, "buying_price": 2268, "opening_stock": 4},
    {"name": "Jagermeister 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3200, "buying_price": 2365, "opening_stock": 2},
    {"name": "Red Label 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2000, "buying_price": 1648, "opening_stock": 3},
    {"name": "Malibu 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2200, "buying_price": 1563, "opening_stock": 3},
    {"name": "4th Street 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1200, "buying_price": 915, "opening_stock": 3},
    {"name": "J & B 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2400, "buying_price": 1932, "opening_stock": 1},
    {"name": "Captain Morgan 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1300, "buying_price": 948, "opening_stock": 5},
    {"name": "Grants 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2200, "buying_price": 1738, "opening_stock": 6},
    {"name": "Kibao 750ML", "category": "Spirits", "size": "750ML", "selling_price": 850, "buying_price": 649, "opening_stock": 10},
    {"name": "Kenya Cane 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1000, "buying_price": 692, "opening_stock": 6},
    {"name": "Kenya Cane Pineapple 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1000, "buying_price": 692, "opening_stock": 15},
    {"name": "Smirnoff 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1277, "opening_stock": 10},
    {"name": "Kenya King 750ML", "category": "Spirits", "size": "750ML", "selling_price": 800, "buying_price": 616, "opening_stock": 3},
    {"name": "Jack Daniels 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3500, "buying_price": 3100, "opening_stock": 4},
    {"name": "Four Cousins 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1200, "buying_price": 920, "opening_stock": 6},
    {"name": "Famous Grouse 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2500, "buying_price": 1875, "opening_stock": 2},
    {"name": "Konyagi 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1100, "buying_price": 803, "opening_stock": 8},
    {"name": "Konyagi 500ML", "category": "Spirits", "size": "500ML", "selling_price": 700, "buying_price": 572, "opening_stock": 10},
    {"name": "Chrome Gin 750ML", "category": "Spirits", "size": "750ML", "selling_price": 800, "buying_price": 577, "opening_stock": 8},
    {"name": "Chrome Vodka 750ML", "category": "Spirits", "size": "750ML", "selling_price": 850, "buying_price": 577, "opening_stock": 11},
    {"name": "Best Whisky 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1100, "buying_price": 922, "opening_stock": 7},
    {"name": "Best Gin 750ML", "category": "Spirits", "size": "750ML", "selling_price": 950, "buying_price": 743, "opening_stock": 12},
    {"name": "Origin 750ML", "category": "Spirits", "size": "750ML", "selling_price": 850, "buying_price": 626, "opening_stock": 9},
    {"name": "Kane Extra 750ML", "category": "Spirits", "size": "750ML", "selling_price": 800, "buying_price": 593, "opening_stock": 4},
    {"name": "All Seasons 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1300, "buying_price": 1050, "opening_stock": 8},
    {"name": "VAT 69 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1442, "opening_stock": 4},
    {"name": "Hennessy 750ML", "category": "Spirits", "size": "750ML", "selling_price": 6200, "buying_price": 5200, "opening_stock": 1},
    {"name": "Martell 750ML", "category": "Spirits", "size": "750ML", "selling_price": 5800, "buying_price": 4500, "opening_stock": 1},
    {"name": "Chivas Regal 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3850, "buying_price": 3682, "opening_stock": 1},
    {"name": "Ballantines 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2500, "buying_price": 2009, "opening_stock": 3},
    {"name": "Bacardi 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2000, "buying_price": 1700, "opening_stock": 3},
    {"name": "Viceroy 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1265, "opening_stock": 4},
    {"name": "Richot 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1277, "opening_stock": 3},
    {"name": "Gilbeys 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1277, "opening_stock": 6},
    {"name": "Bond 7 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1600, "buying_price": 1277, "opening_stock": 3},
    {"name": "Beefeaters Gin Pink 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3000, "buying_price": 2733, "opening_stock": 2},
    {"name": "Beefeaters Gin 750ML", "category": "Spirits", "size": "750ML", "selling_price": 3300, "buying_price": 2570, "opening_stock": 2},
    {"name": "Gordons Gin 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2300, "buying_price": 1977, "opening_stock": 2},
    {"name": "Hunters Choice 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1300, "buying_price": 922, "opening_stock": 6},
    {"name": "Caprice White 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1000, "buying_price": 743, "opening_stock": 4},
    {"name": "Caprice Red 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1000, "buying_price": 743, "opening_stock": 2},
    {"name": "Absolut Vodka 750ML", "category": "Spirits", "size": "750ML", "selling_price": 2400, "buying_price": 1853, "opening_stock": 2},
    {"name": "County 750ML", "category": "Spirits", "size": "750ML", "selling_price": 850, "buying_price": 662, "opening_stock": 11},
    {"name": "Old Monk 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1200, "buying_price": 1050, "opening_stock": 3},
    {"name": "Robertson Wine 750ML", "category": "Spirits", "size": "750ML", "selling_price": 1200, "buying_price": 1050, "opening_stock": 2},
    {"name": "General Meakins 750ML", "category": "Spirits", "size": "750ML", "selling_price": 850, "buying_price": 635, "opening_stock": 4},

    # SPIRITS - 350ML
    {"name": "VAT 69 350ML", "category": "Spirits", "size": "350ML", "selling_price": 1000, "buying_price": 783, "opening_stock": 5},
    {"name": "All Seasons 350ML", "category": "Spirits", "size": "350ML", "selling_price": 750, "buying_price": 535, "opening_stock": 4},
    {"name": "Viceroy 350ML", "category": "Spirits", "size": "350ML", "selling_price": 900, "buying_price": 783, "opening_stock": 8},
    {"name": "Richot 350ML", "category": "Spirits", "size": "350ML", "selling_price": 900, "buying_price": 593, "opening_stock": 5},
    {"name": "William Lawson 350ML", "category": "Spirits", "size": "350ML", "selling_price": 1000, "buying_price": 759, "opening_stock": 2},
    {"name": "Kibao 350ML", "category": "Spirits", "size": "350ML", "selling_price": 600, "buying_price": 350, "opening_stock": 10},
    {"name": "Black & White 350ML", "category": "Spirits", "size": "350ML", "selling_price": 800, "buying_price": 593, "opening_stock": 5},
    {"name": "Jack Daniels 350ML", "category": "Spirits", "size": "350ML", "selling_price": 2000, "buying_price": 1640, "opening_stock": 1},
    {"name": "Gilbeys 350ML", "category": "Spirits", "size": "350ML", "selling_price": 800, "buying_price": 593, "opening_stock": 8},
    {"name": "Smirnoff 350ML", "category": "Spirits", "size": "350ML", "selling_price": 700, "buying_price": 593, "opening_stock": 14},
    {"name": "Kenya Cane 350ML", "category": "Spirits", "size": "350ML", "selling_price": 650, "buying_price": 363, "opening_stock": 10},
    {"name": "Jameson 350ML", "category": "Spirits", "size": "350ML", "selling_price": 1500, "buying_price": 1133, "opening_stock": 7},
    {"name": "Hunters Choice 350ML", "category": "Spirits", "size": "350ML", "selling_price": 650, "buying_price": 437, "opening_stock": 11},
    {"name": "58 Gin 350ML", "category": "Spirits", "size": "350ML", "selling_price": 800, "buying_price": 366, "opening_stock": 8},

    # SPIRITS - 250ML
    {"name": "All Seasons 250ML", "category": "Spirits", "size": "250ML", "selling_price": 500, "buying_price": 365, "opening_stock": 10},
    {"name": "Kenya Cane 250ML", "category": "Spirits", "size": "250ML", "selling_price": 350, "buying_price": 264, "opening_stock": 47},
    {"name": "Smirnoff 250ML", "category": "Spirits", "size": "250ML", "selling_price": 550, "buying_price": 429, "opening_stock": 15},
    {"name": "Best Gin 250ML", "category": "Spirits", "size": "250ML", "selling_price": 400, "buying_price": 265, "opening_stock": 18},
    {"name": "Best Whisky 250ML", "category": "Spirits", "size": "250ML", "selling_price": 450, "buying_price": 318, "opening_stock": 17},
    {"name": "General Meakins 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 217, "opening_stock": 62},
    {"name": "Blue Ice 250ML", "category": "Spirits", "size": "250ML", "selling_price": 200, "buying_price": 155, "opening_stock": 91.5},
    {"name": "Origin 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 239, "opening_stock": 15.5},
    {"name": "County 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 239, "opening_stock": 65.5},
    {"name": "Chrome Lemon 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 239, "opening_stock": 15},
    {"name": "Chrome Gin 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 214, "opening_stock": 100},
    {"name": "Best Cream 250ML", "category": "Spirits", "size": "250ML", "selling_price": 500, "buying_price": 326, "opening_stock": 3},
    {"name": "Napoleon 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 217, "opening_stock": 15},
    {"name": "Konyagi 250ML", "category": "Spirits", "size": "250ML", "selling_price": 350, "buying_price": 286, "opening_stock": 13},
    {"name": "Hunters Choice 250ML", "category": "Spirits", "size": "250ML", "selling_price": 400, "buying_price": 303, "opening_stock": 19},
    {"name": "Gilbeys 250ML", "category": "Spirits", "size": "250ML", "selling_price": 550, "buying_price": 429, "opening_stock": 21},
    {"name": "Triple Ace 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 217, "opening_stock": 13.5},
    {"name": "Viceroy 250ML", "category": "Spirits", "size": "250ML", "selling_price": 550, "buying_price": 443, "opening_stock": 8},
    {"name": "Richot 250ML", "category": "Spirits", "size": "250ML", "selling_price": 550, "buying_price": 429, "opening_stock": 9},
    {"name": "Captain Morgan 250ML", "category": "Spirits", "size": "250ML", "selling_price": 450, "buying_price": 346, "opening_stock": 10},
    {"name": "V&A 250ML", "category": "Spirits", "size": "250ML", "selling_price": 450, "buying_price": 305, "opening_stock": 10},
    {"name": "White Pearl 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 227, "opening_stock": 10},
    {"name": "Caribia 250ML", "category": "Spirits", "size": "250ML", "selling_price": 350, "buying_price": 230, "opening_stock": 10},
    {"name": "Liberty 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 230, "opening_stock": 6},
    {"name": "Kibao 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 230, "opening_stock": 63.5},
    {"name": "Kane Extra 250ML", "category": "Spirits", "size": "250ML", "selling_price": 300, "buying_price": 214, "opening_stock": 19},
    {"name": "Bond 7 250ML", "category": "Spirits", "size": "250ML", "selling_price": 550, "buying_price": 429, "opening_stock": 4},

    # SOFT DRINKS
    {"name": "Delmonte", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 300, "buying_price": 252, "opening_stock": 12},
    {"name": "Predator", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 70, "buying_price": 27, "opening_stock": 31},
    {"name": "Lemonade", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 50, "buying_price": 11, "opening_stock": 22},
    {"name": "Red Bull", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 250, "buying_price": 184, "opening_stock": 2},
    {"name": "Powerplay", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 70, "buying_price": 27, "opening_stock": 25},
    {"name": "Monster", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 300, "buying_price": 252, "opening_stock": 1},
    {"name": "Soda 1.25L", "category": "Soft Drinks", "size": "1 Litre", "selling_price": 150, "buying_price": 58, "opening_stock": 27},
    {"name": "Soda 350ML", "category": "Soft Drinks", "size": "350ML", "selling_price": 50, "buying_price": 41, "opening_stock": 102},
    {"name": "Minute Maid 400ML", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 80, "buying_price": 33, "opening_stock": 49},
    {"name": "Minute Maid 1L", "category": "Soft Drinks", "size": "1 Litre", "selling_price": 150, "buying_price": 125, "opening_stock": 51},
    {"name": "Water 1L", "category": "Soft Drinks", "size": "1 Litre", "selling_price": 100, "buying_price": 39, "opening_stock": 16},
    {"name": "Water 500ML", "category": "Soft Drinks", "size": "500ML", "selling_price": 50, "buying_price": 22, "opening_stock": 20},
    {"name": "Novida", "category": "Soft Drinks", "size": "Can/Bottle", "selling_price": 50, "buying_price": 38, "opening_stock": 2},
]

# Size definitions
SIZES = [
    {"name": "1 Litre", "description": "1 Litre bottles", "sort_order": 1},
    {"name": "750ML", "description": "750ml bottles", "sort_order": 2},
    {"name": "500ML", "description": "500ml bottles", "sort_order": 3},
    {"name": "350ML", "description": "350ml bottles", "sort_order": 4},
    {"name": "250ML", "description": "250ml bottles/tots", "sort_order": 5},
    {"name": "Can/Bottle", "description": "Standard can or bottle", "sort_order": 6},
]


def create_categories():
    """Create product categories"""
    print("\n=== Creating Categories ===")
    categories = {}

    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        print("ERROR: No admin user found!")
        return categories

    category_names = set(product['category'] for product in PRODUCTS)

    for cat_name in category_names:
        existing = Category.query.filter_by(name=cat_name).first()
        if existing:
            print(f"✓ Category '{cat_name}' already exists")
            categories[cat_name] = existing
        else:
            category = Category(
                name=cat_name,
                description=f"{cat_name} products",
                is_active=True,
                created_by=admin_user.id
            )
            db.session.add(category)
            db.session.flush()
            categories[cat_name] = category
            print(f"✓ Created category: {cat_name}")

    db.session.commit()
    return categories


def create_sizes():
    """Create product sizes"""
    print("\n=== Creating Sizes ===")
    sizes = {}

    admin_user = User.query.filter_by(role='admin').first()

    for size_data in SIZES:
        existing = Size.query.filter_by(name=size_data['name']).first()
        if existing:
            print(f"✓ Size '{size_data['name']}' already exists")
            sizes[size_data['name']] = existing
        else:
            size = Size(
                name=size_data['name'],
                description=size_data['description'],
                sort_order=size_data['sort_order'],
                is_active=True,
                created_by=admin_user.id
            )
            db.session.add(size)
            db.session.flush()
            sizes[size_data['name']] = size
            print(f"✓ Created size: {size_data['name']}")

    db.session.commit()
    return sizes


def import_products(categories, sizes):
    """Import all products with one variant each (the bottle itself)"""
    print("\n=== Importing Products ===")

    admin_user = User.query.filter_by(role='admin').first()
    stats = {
        'products_created': 0,
        'products_skipped': 0,
        'variants_created': 0,
        'variants_skipped': 0
    }

    for product_data in PRODUCTS:
        product_name = product_data['name']
        category = categories[product_data['category']]
        size = sizes[product_data['size']]

        # Check if product exists
        existing_product = Product.query.filter_by(name=product_name).first()

        if existing_product:
            print(f"  ⊘ Product '{product_name}' already exists")
            product = existing_product
            stats['products_skipped'] += 1
        else:
            # Create new product
            product = Product(
                name=product_name,
                category_id=category.id,
                base_unit='bottle',
                base_buying_price=product_data['buying_price'],
                current_stock=product_data['opening_stock'],
                min_stock_level=5,  # Default minimum stock
                created_by=admin_user.id
            )
            db.session.add(product)
            db.session.flush()  # Get product ID
            stats['products_created'] += 1
            print(f"  ✓ Created product: {product_name} (Stock: {product_data['opening_stock']})")

        # Create ONE variant for the bottle itself (1 bottle = 1 unit)
        existing_variant = ProductVariant.query.filter_by(
            product_id=product.id,
            size_id=size.id
        ).first()

        if existing_variant:
            print(f"    ⊘ Bottle variant already exists")
            stats['variants_skipped'] += 1
        else:
            variant = ProductVariant(
                product_id=product.id,
                size_id=size.id,
                selling_price=product_data['selling_price'],
                conversion_factor=1.0,  # 1 bottle = 1 bottle (base unit)
                is_active=True,
                created_by=admin_user.id
            )
            db.session.add(variant)
            stats['variants_created'] += 1
            print(f"    ✓ Created bottle variant: {size.name} @ KES {product_data['selling_price']}")

    db.session.commit()
    return stats


def print_summary(stats):
    """Print import summary"""
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Products Created:  {stats['products_created']}")
    print(f"Products Skipped:  {stats['products_skipped']}")
    print(f"Variants Created:  {stats['variants_created']} (bottle variants only)")
    print(f"Variants Skipped:  {stats['variants_skipped']}")
    print("="*60)
    print("\n📝 NOTE: Only bottle variants have been created.")
    print("   You can now manually add tot/glass variants as needed.")
    print("="*60)


def main():
    """Main import function"""
    print("="*60)
    print("MOSEVINES LIQUOR STORE - STOCK IMPORT")
    print("="*60)
    print("\nThis script will:")
    print("- Create categories (Beers, Spirits, Soft Drinks)")
    print("- Create sizes (1L, 750ML, 500ML, 350ML, 250ML, Can/Bottle)")
    print("- Import all products with their bottle size as separate products")
    print("- Create ONE variant per product (the bottle itself)")
    print("- You can add tot/glass variants manually later")
    print("="*60)

    with app.app_context():
        try:
            # Create categories
            categories = create_categories()

            # Create sizes
            sizes = create_sizes()

            # Import products and variants
            stats = import_products(categories, sizes)

            # Print summary
            print_summary(stats)

            print("\n✅ Import completed successfully!")
            print("\n💡 Next steps:")
            print("   1. Login to the system")
            print("   2. Go to Products → Product Variants")
            print("   3. Add tot/glass variants for spirits as needed")
            print("   4. Set conversion factors (e.g., 1 bottle = 40 tots)")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during import: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()