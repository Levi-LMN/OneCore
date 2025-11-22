"""
Excel Data Import Script for LiquorPro System - November 6, 2025
Imports stock data from the Excel sheet into the database
Date: November 6, 2025

IMPORTANT: Updates existing products with November 6th data
Each size (750ML, 250ML, etc.) is a SEPARATE PRODUCT
"""

from app import app, db
from models import (User, Category, Size, Product, ProductVariant,
                   Sale, DailyStock, StockPurchase, Expense, ExpenseCategory)
from datetime import datetime, date
import re

# Data from the Excel file (November 6, 2025)
IMPORT_DATE = date(2025, 11, 6)

# Excel data structure: [Product Name, Category, Opening Stock, Additions, Sales, Selling Price, Buying Price]
PRODUCTS_DATA = [
    # BEERS
    ("Snapp", "Beers", 0, 0, 0, 250, 181),
    ("Guarana", "Beers", 22, 0, 0, 250, 181),
    ("Black Ice", "Beers", 19, 0, 0, 250, 181),
    ("Pineapple Punch", "Beers", 19, 0, 0, 250, 181),
    ("Tusker Malt", "Beers", 0, 0, 0, 250, 247),
    ("Heineken", "Beers", 0, 0, 0, 350, 287),
    ("Tusker Lager", "Beers", 21, 0, 1, 280, 203),
    ("Faxe", "Beers", 0, 0, 0, 320, 263),
    ("Martens Beer", "Beers", 10, 0, 0, 350, 263),
    ("Tusker Lite", "Beers", 0, 0, 0, 250, 247),
    ("Guinness", "Beers", 22, 0, 0, 300, 220),
    ("Kingfisher", "Beers", 0, 0, 0, 250, 192),
    ("Hunters Gold", "Beers", 0, 0, 0, 250, 203),
    ("Balozi", "Beers", 21, 0, 0, 300, 203),
    ("Pilsner", "Beers", 0, 0, 0, 300, 203),
    ("Whitecap", "Beers", 18, 0, 0, 300, 220),
    ("Savannah", "Beers", 0, 0, 0, 200, 240),
    ("KO", "Beers", 10, 0, 0, 300, 220),
    ("Tusker Cider", "Beers", 16, 0, 1, 300, 241),
    ("Banana Beer", "Beers", 33, 0, 1, 130, 72),

    # SPIRITS - 1 LITRE
    ("Flirt Vodka 1L", "Spirits", 1, 0, 0, 1700, 1030),
    ("Ballantines 1L", "Spirits", 2, 0, 0, 3600, 2679),
    ("Double Black 1L", "Spirits", 2, 0, 0, 6800, 5550),
    ("J&B 1L", "Spirits", 2, 0, 0, 2700, 2017),
    ("Red Label 1L", "Spirits", 3, 0, 0, 2500, 2050),
    ("Black Label 1L", "Spirits", 5, 0, 0, 4500, 3810),
    ("Black & White 1L", "Spirits", 4, 0, 0, 2000, 1525),
    ("Jagermeister 1L", "Spirits", 2, 0, 0, 3700, 3100),
    ("Jameson 1L", "Spirits", 3, 0, 0, 3700, 3024),
    ("Gordons 1L", "Spirits", 0, 0, 0, 0, 2348),
    ("Jack Daniels 1L", "Spirits", 3, 0, 0, 4500, 3850),
    ("Baileys Original 1L", "Spirits", 0, 0, 0, 3600, 2720),
    ("Captain Morgan Spiced 1L", "Spirits", 5, 0, 0, 2800, 2184),
    ("Captain Morgan Gold 1L", "Spirits", 0, 0, 0, 2500, 2184),
    ("Malibu 1L", "Spirits", 2, 0, 0, 2500, 1575),
    ("Absolut Vodka 1L", "Spirits", 0, 0, 0, 0, 2577),
    ("4th Street 1.5L", "Spirits", 1, 0, 0, 2000, 1680),
    ("8PM 1L", "Spirits", 4, 0, 0, 1300, 1000),
    ("Jim Beam 1L", "Spirits", 2, 0, 0, 2600, 2415),

    # SPIRITS - 750ML
    ("Black & White 750ML", "Spirits", 3, 0, 0, 1500, 1155),
    ("Jim Beam 750ML", "Spirits", 2, 0, 0, 1700, 2195),
    ("Black Label 750ML", "Spirits", 3, 0, 0, 3600, 3077),
    ("Baileys Original 750ML", "Spirits", 0, 0, 0, 2600, 2225),
    ("Jameson 750ML", "Spirits", 4, 0, 0, 2750, 2268),
    ("Jagermeister 750ML", "Spirits", 2, 0, 0, 3200, 2365),
    ("Red Label 750ML", "Spirits", 3, 0, 0, 2000, 1648),
    ("Malibu 750ML", "Spirits", 3, 0, 0, 2200, 1563),
    ("4th Street 750ML", "Spirits", 3, 0, 0, 1200, 915),
    ("J&B 750ML", "Spirits", 1, 0, 0, 2400, 1932),
    ("Captain Morgan 750ML", "Spirits", 5, 0, 0, 1300, 948),
    ("Grants 750ML", "Spirits", 6, 0, 0, 2200, 1738),
    ("Kibao 750ML", "Spirits", 10, 0, 0, 850, 649),
    ("Kenya Cane 750ML", "Spirits", 1, 0, 1, 1000, 692),
    ("Kenya Cane Pineapple 750ML", "Spirits", 18, 0, 2, 1000, 692),
    ("Smirnoff 750ML", "Spirits", 10, 0, 0, 1600, 1277),
    ("Kenya King 750ML", "Spirits", 3, 0, 0, 800, 616),
    ("Jack Daniels 750ML", "Spirits", 4, 0, 0, 3500, 3100),
    ("Four Cousins 750ML", "Spirits", 6, 0, 0, 1200, 920),
    ("Famous Grouse 750ML", "Spirits", 2, 0, 0, 2500, 1875),
    ("Konyagi 750ML", "Spirits", 8, 0, 0, 1100, 803),
    ("Konyagi 500ML", "Spirits", 10, 0, 0, 700, 572),
    ("Chrome Gin 750ML", "Spirits", 8, 0, 0, 800, 577),
    ("Chrome Vodka 750ML", "Spirits", 8, 0, 0, 800, 577),
    ("Best Whisky 750ML", "Spirits", 6, 0, 0, 1100, 922),
    ("Best Gin 750ML", "Spirits", 12, 0, 0, 950, 743),
    ("Best Cream 750ML", "Spirits", 0, 0, 0, 1200, 999),
    ("Origin 750ML", "Spirits", 9, 0, 0, 850, 626),
    ("Kane Extra 750ML", "Spirits", 4, 0, 0, 800, 593),
    ("All Seasons 750ML", "Spirits", 8, 0, 0, 1300, 1050),
    ("VAT 69 750ML", "Spirits", 4, 0, 0, 1600, 1442),
    ("Chamdor 750ML", "Spirits", 0, 0, 0, 1000, 747),
    ("Hennessy 750ML", "Spirits", 1, 0, 0, 6200, 5200),
    ("Martell 750ML", "Spirits", 1, 0, 0, 5800, 4500),
    ("Amarula 750ML", "Spirits", 0, 0, 0, 2200, 2060),
    ("Chivas Regal 750ML", "Spirits", 1, 0, 0, 3850, 3682),
    ("Ballantines 750ML", "Spirits", 3, 0, 0, 2500, 2009),
    ("Bacardi 750ML", "Spirits", 3, 0, 0, 2000, 1700),
    ("Viceroy 750ML", "Spirits", 4, 0, 0, 1600, 1265),
    ("Drostdy Hof 750ML", "Spirits", 0, 0, 0, 1200, 930),
    ("Richot 750ML", "Spirits", 3, 0, 0, 1600, 1277),
    ("Gilbeys 750ML", "Spirits", 6, 0, 0, 1600, 1277),
    ("Bond 7 750ML", "Spirits", 3, 0, 0, 1600, 1277),
    ("Beefeaters Gin Pink 750ML", "Spirits", 2, 0, 0, 3000, 2733),
    ("Beefeaters Gin 750ML", "Spirits", 2, 0, 0, 3300, 2570),
    ("Gordons Gin Pink 750ML", "Spirits", 0, 0, 0, 2200, 1895),
    ("Gordons Gin 750ML", "Spirits", 2, 0, 0, 2300, 1977),
    ("Hunters Choice 750ML", "Spirits", 6, 0, 0, 1300, 922),
    ("8PM 750ML", "Spirits", 0, 0, 0, 1300, 922),
    ("Caprice White 750ML", "Wines", 4, 0, 0, 1000, 743),
    ("Caprice Red 750ML", "Wines", 2, 0, 0, 1000, 743),
    ("Casabuena White 750ML", "Wines", 0, 0, 0, 1000, 711),
    ("Casabuena Red 750ML", "Wines", 0, 0, 0, 1000, 711),
    ("Absolut Vodka 750ML", "Spirits", 2, 0, 0, 2400, 1853),
    ("County 750ML", "Spirits", 12, 0, 0, 850, 662),
    ("Old Monk 750ML", "Spirits", 3, 0, 0, 1200, 1050),
    ("Robertson Wine 750ML", "Wines", 2, 0, 0, 1200, 1050),
    ("General Meakins 750ML", "Spirits", 4, 0, 0, 850, 635),

    # SPIRITS - 350ML
    ("VAT 69 350ML", "Spirits", 4, 0, 0, 1000, 783),
    ("Amarula 350ML", "Spirits", 0, 0, 0, 1200, 1185),
    ("All Seasons 350ML", "Spirits", 4, 0, 0, 750, 535),
    ("Viceroy 350ML", "Spirits", 8, 0, 0, 900, 783),
    ("Grants 350ML", "Spirits", 0, 0, 0, 1000, 885),
    ("Richot 350ML", "Spirits", 5, 0, 0, 900, 593),
    ("William Lawson 350ML", "Spirits", 2, 0, 0, 1000, 759),
    ("Kibao 350ML", "Spirits", 10, 0, 0, 600, 350),
    ("Black & White 350ML", "Spirits", 5, 0, 0, 800, 593),
    ("Jack Daniels 350ML", "Spirits", 1, 0, 0, 2000, 1640),
    ("Gilbeys 350ML", "Spirits", 8, 0, 0, 800, 593),
    ("Smirnoff 350ML", "Spirits", 14, 0, 0, 700, 593),
    ("Kenya Cane Pineapple 350ML", "Spirits", 0, 0, 0, 450, 0),
    ("Kenya Cane 350ML", "Spirits", 10, 0, 0, 650, 363),
    ("Jameson 350ML", "Spirits", 7, 0, 1, 1400, 1133),
    ("Hunters Choice 350ML", "Spirits", 12, 0, 0, 650, 437),
    ("58 Gin 350ML", "Spirits", 8, 0, 0, 800, 366),

    # SPIRITS - 250ML
    ("All Seasons 250ML", "Spirits", 10, 0, 0, 500, 365),
    ("Kenya Cane 250ML", "Spirits", 64, 0, 10, 350, 264),
    ("Kenya Cane Pineapple 250ML", "Spirits", 0, 0, 0, 380, 264),
    ("Smirnoff 250ML", "Spirits", 15, 0, 0, 550, 429),
    ("Best Gin 250ML", "Spirits", 18, 0, 0, 350, 265),
    ("Best Whisky 250ML", "Spirits", 16, 0, 0, 400, 318),
    ("General Meakins 250ML", "Spirits", 62, 0, 0, 300, 217),
    ("Blue Ice 250ML", "Spirits", 135, 0, 12.5, 200, 155),
    ("Origin 250ML", "Spirits", 15, 0, 0, 300, 239),
    ("County 250ML", "Spirits", 53.5, 0, 2.5, 300, 239),
    ("Chrome Lemon 250ML", "Spirits", 15, 0, 0, 300, 239),
    ("Chrome Gin 250ML", "Spirits", 116.5, 0, 2, 300, 214),
    ("Best Cream 250ML", "Spirits", 3, 0, 0, 500, 326),
    ("Napoleon 250ML", "Spirits", 15, 0, 0, 300, 217),
    ("Konyagi 250ML", "Spirits", 13, 0, 0, 350, 286),
    ("Hunters Choice 250ML", "Spirits", 20, 0, 0, 400, 303),
    ("Gilbeys 250ML", "Spirits", 21, 0, 0, 550, 429),
    ("Triple Ace 250ML", "Spirits", 15.5, 0, 0, 300, 217),
    ("Viceroy 250ML", "Spirits", 8, 0, 1, 550, 443),
    ("VAT 69 250ML", "Spirits", 0, 0, 0, 600, 305),
    ("Richot 250ML", "Spirits", 9, 0, 0, 550, 429),
    ("Captain Morgan 250ML", "Spirits", 10, 0, 0, 450, 346),
    ("V&A 250ML", "Spirits", 10, 0, 0, 450, 305),
    ("White Pearl 250ML", "Spirits", 10, 0, 0, 300, 227),
    ("Caribia 250ML", "Spirits", 10, 0, 0, 350, 230),
    ("Liberty 250ML", "Spirits", 8, 0, 3.5, 300, 230),
    ("Kibao 250ML", "Spirits", 57, 0, 4.5, 300, 230),
    ("Kane Extra 250ML", "Spirits", 15, 0, 0, 300, 214),
    ("Bond 7 250ML", "Spirits", 5, 0, 0, 550, 429),

    # SOFT DRINKS
    ("Delmonte", "Soft Drinks", 12, 0, 0, 300, 252),
    ("Predator", "Soft Drinks", 19, 0, 4, 70, 27),
    ("Lemonade", "Soft Drinks", 31, 0, 1, 50, 11),
    ("Redbull", "Soft Drinks", 2, 0, 0, 250, 184),
    ("Powerplay", "Soft Drinks", 15, 0, 0, 70, 27),
    ("Monster", "Soft Drinks", 1, 0, 0, 300, 252),
    ("Soda 2L", "Soft Drinks", 0, 0, 0, 200, 158),
    ("Soda 1L", "Soft Drinks", 0, 0, 0, 100, 158),
    ("Soda 1.25L", "Soft Drinks", 20, 0, 0, 150, 58),
    ("Soda 500ML", "Soft Drinks", 0, 0, 0, 50, 38),
    ("Soda 350ML", "Soft Drinks", 80, 0, 3, 50, 41),
    ("Minute Maid 400ML", "Soft Drinks", 38, 0, 5, 80, 33),
    ("Minute Maid 1L", "Soft Drinks", 48, 0, 0, 150, 125),
    ("Water 1L", "Soft Drinks", 16, 0, 0, 100, 39),
    ("Water 500ML", "Soft Drinks", 15, 0, 0, 50, 22),
    ("Novida", "Soft Drinks", 2, 0, 0, 50, 38),
    ("Lime", "Soft Drinks", 0, 32, 1, 20, 10),
]

# Additional expenses from the document
EXPENSES_DATA = [
    ("Police", 0, "Security"),  # Amount not specified in PDF
    ("Tissue", 0, "General Expenses"),  # Amount not specified in PDF
    ("Stocksheet", 0, "Office Supplies"),  # Amount not specified in PDF
    ("Purchases", 0, "Stock Purchases"),  # Amount not specified in PDF
]

def get_or_create_category(name, description=None):
    """Get or create a category"""
    category = Category.query.filter_by(name=name).first()
    if not category:
        admin = User.query.filter_by(role='admin').first()
        category = Category(
            name=name,
            description=description,
            created_by=admin.id if admin else None
        )
        db.session.add(category)
        db.session.flush()
        print(f"  ✓ Created category: {name}")
    return category

def get_or_create_expense_category(name):
    """Get or create an expense category"""
    category = ExpenseCategory.query.filter_by(name=name).first()
    if not category:
        admin = User.query.filter_by(role='admin').first()
        category = ExpenseCategory(
            name=name,
            created_by=admin.id if admin else None
        )
        db.session.add(category)
        db.session.flush()
        print(f"  ✓ Created expense category: {name}")
    return category

def update_product_stock_for_nov6(name, category, opening_stock, additions,
                                   sales, selling_price, buying_price):
    """
    Update product stock for November 6th
    Follows the exact flow of the Flask app
    """
    admin = User.query.filter_by(role='admin').first()

    # Calculate closing stock
    closing_stock = opening_stock + additions - sales

    # Clean product name
    product_name = name.strip()

    # Find existing product
    product = Product.query.filter_by(name=product_name).first()

    if not product:
        # Product doesn't exist - create it
        product = Product(
            name=product_name,
            category_id=category.id,
            base_unit='bottle',
            base_buying_price=buying_price,
            current_stock=closing_stock,
            min_stock_level=5,
            created_by=admin.id if admin else None,
            last_stock_update=datetime.now()
        )
        db.session.add(product)
        db.session.flush()
        print(f"  ✓ Created NEW product: {product_name}")
    else:
        # Update existing product
        product.current_stock = closing_stock
        product.base_buying_price = buying_price
        product.last_stock_update = datetime.now()
        print(f"  ✓ Updated product: {product_name}")

    # Get or create "Full Bottle" size
    full_bottle_size = Size.query.filter_by(name="Full Bottle").first()
    if not full_bottle_size:
        full_bottle_size = Size(
            name="Full Bottle",
            description="Entire bottle/unit as purchased",
            sort_order=1,
            created_by=admin.id if admin else None
        )
        db.session.add(full_bottle_size)
        db.session.flush()

    # Get or create variant
    variant = ProductVariant.query.filter_by(
        product_id=product.id,
        size_id=full_bottle_size.id
    ).first()

    if not variant:
        variant = ProductVariant(
            product_id=product.id,
            size_id=full_bottle_size.id,
            selling_price=selling_price,
            conversion_factor=1.0,
            created_by=admin.id if admin else None
        )
        db.session.add(variant)
        db.session.flush()
        print(f"    → Created 'Full Bottle' variant (Price: KES {selling_price})")
    else:
        variant.selling_price = selling_price
        print(f"    → Updated 'Full Bottle' variant (Price: KES {selling_price})")

    # Create DailyStock record for November 6th
    daily_stock = DailyStock.query.filter_by(
        product_id=product.id,
        date=IMPORT_DATE
    ).first()

    if not daily_stock:
        daily_stock = DailyStock(
            product_id=product.id,
            date=IMPORT_DATE,
            opening_stock=opening_stock,
            additions=0,
            sales_quantity=0,
            closing_stock=opening_stock,
            updated_by=admin.id if admin else None,
            updated_at=datetime.now()
        )
        db.session.add(daily_stock)
        db.session.flush()
        print(f"    → Created daily stock record (Opening: {opening_stock})")

    # Create stock purchase if there were additions
    if additions > 0:
        purchase = StockPurchase(
            product_id=product.id,
            quantity=additions,
            unit_cost=buying_price,
            total_cost=additions * buying_price,
            purchase_date=IMPORT_DATE,
            notes="Stock addition - November 6, 2025",
            recorded_by=admin.id if admin else None,
            timestamp=datetime.now()
        )
        db.session.add(purchase)
        db.session.flush()
        print(f"    → Purchase: +{additions} bottles @ KES {buying_price} = KES {additions * buying_price}")
        daily_stock.additions = additions

    # Create sales if there were sales
    if sales > 0:
        cost_per_unit = buying_price * variant.conversion_factor
        total_cost = cost_per_unit * sales
        total_amount = sales * selling_price
        profit = total_amount - total_cost

        sale = Sale(
            variant_id=variant.id,
            attendant_id=admin.id if admin else None,
            quantity=sales,
            unit_price=selling_price,
            original_amount=total_amount,
            discount_type='none',
            discount_value=0,
            discount_amount=0,
            total_amount=total_amount,
            cash_amount=total_amount,
            mpesa_amount=0,
            credit_amount=0,
            payment_method='cash',
            sale_date=IMPORT_DATE,
            timestamp=datetime.now(),
            notes="Sale - November 6, 2025"
        )
        db.session.add(sale)
        db.session.flush()
        print(f"    → Sale: -{sales} bottles @ KES {selling_price} = KES {total_amount} (Profit: KES {profit:.2f})")
        daily_stock.sales_quantity = sales

    # Recalculate closing stock
    daily_stock.calculate_closing_stock()
    print(f"    → Daily Stock Summary: Open={daily_stock.opening_stock}, " +
          f"Add={daily_stock.additions}, Sales={daily_stock.sales_quantity}, " +
          f"Close={daily_stock.closing_stock}")

    # Verify sync
    if product.current_stock != daily_stock.closing_stock:
        print(f"    ⚠️  WARNING: Product stock ({product.current_stock}) != Daily closing ({daily_stock.closing_stock})")
        product.current_stock = daily_stock.closing_stock
        print(f"    ✓ Synced product stock to {daily_stock.closing_stock}")

    return product, variant

def import_data():
    """Main import function for November 6th"""
    with app.app_context():
        try:
            print("="*70)
            print("IMPORTING DATA FOR NOVEMBER 6, 2025")
            print("Updating existing products with November 6th stock data")
            print("="*70)

            # Get admin user
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                print("❌ Error: Admin user not found!")
                return

            print(f"\n✓ Using admin user: {admin.full_name}")

            # Get or create categories
            print("\n📁 Getting Categories...")
            categories = {}
            for cat_name in ["Beers", "Spirits", "Wines", "Soft Drinks"]:
                categories[cat_name] = get_or_create_category(cat_name)

            db.session.commit()

            # Import all products for November 6th
            print("\n📦 Importing November 6th Stock Data...")
            print("-" * 70)

            products_updated = 0
            purchases_created = 0
            sales_created = 0

            for product_data in PRODUCTS_DATA:
                name, category_name, opening, additions, sales, selling, buying = product_data

                category = categories[category_name]
                product, variant = update_product_stock_for_nov6(
                    name, category, opening, additions, sales, selling, buying
                )

                products_updated += 1
                if additions > 0:
                    purchases_created += 1
                if sales > 0:
                    sales_created += 1

                print()  # Blank line between products

            # Update DailySummary for November 6th
            print("\n📊 Creating Daily Summary for November 6, 2025...")
            print("-" * 70)

            from models import DailySummary

            # Calculate totals from actual records
            total_sales = db.session.query(
                db.func.coalesce(db.func.sum(Sale.total_amount), 0)
            ).filter(Sale.sale_date == IMPORT_DATE).scalar()

            total_expenses = db.session.query(
                db.func.coalesce(db.func.sum(Expense.amount), 0)
            ).filter(Expense.expense_date == IMPORT_DATE).scalar()

            # Calculate profit from sales
            sales_with_profit = db.session.query(
                db.func.coalesce(db.func.sum(
                    Sale.total_amount - (Product.base_buying_price * ProductVariant.conversion_factor * Sale.quantity)
                ), 0)
            ).join(ProductVariant).join(Product).filter(
                Sale.sale_date == IMPORT_DATE
            ).scalar()

            # Calculate payment breakdown
            payment_breakdown = db.session.query(
                db.func.coalesce(db.func.sum(Sale.cash_amount), 0).label('cash'),
                db.func.coalesce(db.func.sum(Sale.mpesa_amount), 0).label('mpesa'),
                db.func.coalesce(db.func.sum(Sale.credit_amount), 0).label('credit')
            ).filter(Sale.sale_date == IMPORT_DATE).first()

            transaction_count = Sale.query.filter_by(sale_date=IMPORT_DATE).count()
            expense_count = Expense.query.filter_by(expense_date=IMPORT_DATE).count()

            # Create or update daily summary
            summary = DailySummary.query.filter_by(date=IMPORT_DATE).first()
            if not summary:
                summary = DailySummary(date=IMPORT_DATE)
                db.session.add(summary)

            summary.total_sales = total_sales or 0
            summary.total_profit = sales_with_profit or 0
            summary.total_expenses = total_expenses or 0
            summary.net_profit = (sales_with_profit or 0) - (total_expenses or 0)
            summary.total_transactions = transaction_count
            summary.expense_count = expense_count
            summary.cash_amount = payment_breakdown.cash or 0
            summary.paybill_amount = payment_breakdown.mpesa or 0
            summary.credit_amount = payment_breakdown.credit or 0
            summary.last_updated_by = admin.id
            summary.last_updated_at = datetime.now()

            print(f"  ✓ Daily Summary Created:")
            print(f"    - Total Sales: KES {summary.total_sales:,.2f}")
            print(f"    - Gross Profit: KES {summary.total_profit:,.2f}")
            print(f"    - Total Expenses: KES {summary.total_expenses:,.2f}")
            print(f"    - Net Profit: KES {summary.net_profit:,.2f}")
            print(f"    - Transactions: {summary.total_transactions}")
            print(f"    - Cash: KES {summary.cash_amount:,.2f} (Expected: KES 3,100)")
            print(f"    - M-Pesa: KES {summary.paybill_amount:,.2f} (Expected: KES 13,210)")
            print(f"    - Credit: KES {summary.credit_amount:,.2f}")
            print(f"    - Total Expected Sales: KES 16,310")

            # Import expenses (amounts not specified in PDF)
            print("\n💰 Expense Categories (amounts not specified in PDF)...")
            print("-" * 70)
            for description, amount, category_name in EXPENSES_DATA:
                expense_cat = get_or_create_expense_category(category_name)
                print(f"  • {description} - Category: {category_name}")

            # Commit all changes
            db.session.commit()

            print("\n" + "="*70)
            print("✅ NOVEMBER 6TH DATA IMPORT COMPLETED SUCCESSFULLY!")
            print("="*70)

            # Print summary
            print("\n📊 IMPORT SUMMARY:")
            print("-" * 70)
            print(f"  Products in Database: {Product.query.count()}")
            print(f"  Product Variants: {ProductVariant.query.count()}")
            print(f"  Sales Records (Nov 6): {Sale.query.filter_by(sale_date=IMPORT_DATE).count()}")
            print(f"  Purchase Records (Nov 6): {StockPurchase.query.filter_by(purchase_date=IMPORT_DATE).count()}")
            print(f"  Daily Stock Records (Nov 6): {DailyStock.query.filter_by(date=IMPORT_DATE).count()}")

            # Print sales breakdown
            print("\n💰 SALES BREAKDOWN (November 6th):")
            print("-" * 70)

            # From the PDF: Total Sales = 16,310
            # Paybill: 13,210
            # Cash: 3,100
            # Credit: 0

            print(f"  Expected Total Sales: KES 16,310")
            print(f"  Expected Paybill (M-Pesa): KES 13,210")
            print(f"  Expected Cash: KES 3,100")
            print(f"  Expected Credit: KES 0")
            print()
            print(f"  Actual Total Sales: KES {summary.total_sales:,.2f}")
            print(f"  Difference: KES {summary.total_sales - 16310:,.2f}")

            # Verify data integrity
            print("\n🔍 DATA INTEGRITY CHECK:")
            print("-" * 70)
            products_with_issues = 0
            for product in Product.query.all():
                daily = DailyStock.query.filter_by(product_id=product.id, date=IMPORT_DATE).first()
                if daily:
                    if abs(product.current_stock - daily.closing_stock) > 0.01:
                        print(f"  ⚠️  {product.name}: Stock mismatch (Product: {product.current_stock}, Daily: {daily.closing_stock})")
                        products_with_issues += 1

            if products_with_issues == 0:
                print(f"  ✅ All products synchronized correctly!")
            else:
                print(f"  ⚠️  {products_with_issues} product(s) with stock mismatches")

            # Notable items from November 6th
            print("\n📝 NOTABLE ITEMS (November 6th):")
            print("-" * 70)
            print("  • New item added: 'Lime' - 32 units added, 1 sold")
            print("  • Kenya Cane 750ML - Down to 0 units (was 1, sold 1)")
            print("  • Kenya Cane 250ML - High sales: 10 units sold")
            print("  • Blue Ice 250ML - 12.5 units sold (partial bottles)")
            print("  • Chrome Gin 250ML - High volume: 116.5 units in stock")
            print("  • Liberty 250ML - 3.5 units sold (partial bottles)")
            print("  • Kibao 250ML - 4.5 units sold")
            print("  • County 250ML - 2.5 units sold")

            print("\n⚠️  IMPORTANT NOTES:")
            print("-" * 70)
            print("  1. Expense amounts were not specified in the PDF")
            print("     You'll need to add these manually with actual amounts:")
            print("     - Police (Security)")
            print("     - Tissue (General Expenses)")
            print("     - Stocksheet (Office Supplies)")
            print("     - Purchases (Stock Purchases)")
            print()
            print("  2. Payment breakdown from PDF:")
            print("     - Paybill: KES 13,210")
            print("     - Cash: KES 3,100")
            print("     - Total: KES 16,310")
            print()
            print("  3. All sales were recorded as CASH payment method")
            print("     You may need to adjust payment methods to match:")
            print("     - Update sales to reflect M-Pesa vs Cash split")

            print("\n📝 NEXT STEPS:")
            print("-" * 70)
            print("  1. Login and verify November 6th data on the Daily Stock page")
            print("  2. Add expense amounts for: Police, Tissue, Stocksheet, Purchases")
            print("  3. Review and adjust payment methods for sales if needed")
            print("  4. Verify the sales total matches KES 16,310")
            print("  5. Check products with 0 stock for reordering")
            print("  6. Continue normal operations for November 7th onwards")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will import November 6th data into the database.")
    print("   This will update existing products with Nov 6th stock levels.")
    print("   Make sure November 1st data has been imported first.\n")

    response = input("Do you want to continue? (yes/no): ")
    if response.lower() == 'yes':
        import_data()
    else:
        print("Import cancelled.")