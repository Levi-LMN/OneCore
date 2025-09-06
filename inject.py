#!/usr/bin/env python3
"""
Data injection script for MoseVines Liquor Store
Injects stock sheet data from PDF into Flask application database
Date: 7/8/2025 Stock Sheet
"""

from datetime import datetime, date
import sys
import os

# Import your models
from models import (
    db, User, Category, Size, Product, ProductVariant,
    DailyStock, ExpenseCategory, Sale
)

# Import your Flask app
from app import create_app  # Adjust based on your app structure


def inject_stock_data():
    """Main function to inject all the stock data"""

    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@mosevines.com',
            full_name='System Administrator',
            role='manager'
        )
        admin.set_password('admin123')  # Change this password!
        db.session.add(admin)
        db.session.commit()
        print("✓ Created admin user")

    # Create categories
    categories_data = [
        ('Beers', 'All types of beer'),
        ('Spirits 1L', 'Spirits in 1 liter bottles'),
        ('Spirits 750ML', 'Spirits in 750ml bottles'),
        ('Spirits 500ML', 'Spirits in 500ml bottles'),
        ('Spirits 350ML', 'Spirits in 350ml bottles'),
        ('Spirits 250ML', 'Spirits in 250ml bottles'),
        ('Soft Drinks', 'Non-alcoholic beverages'),
        ('Wine', 'Wine products'),
        ('Miscellaneous', 'Other items like limes, purchases, etc'),
    ]

    category_map = {}
    for name, description in categories_data:
        category = Category.query.filter_by(name=name).first()
        if not category:
            category = Category(name=name, description=description, created_by=admin.id)
            db.session.add(category)
        category_map[name] = category

    db.session.commit()
    print(f"✓ Created/verified {len(categories_data)} categories")

    # Create sizes
    sizes_data = [
        ('Full Bottle', 'Full bottle/can', 1),
        ('Tot', 'Single tot serving', 2),
    ]

    size_map = {}
    for name, description, sort_order in sizes_data:
        size = Size.query.filter_by(name=name).first()
        if not size:
            size = Size(name=name, description=description, sort_order=sort_order, created_by=admin.id)
            db.session.add(size)
        size_map[name] = size

    db.session.commit()
    print(f"✓ Created/verified {len(sizes_data)} sizes")

    # Stock data from the PDF (7/8/2025)
    stock_date = date(2025, 8, 7)

    # Products data extracted from the PDF
    products_data = [
        # Format: (name, category, base_unit, buying_price, current_stock, min_stock, selling_price)

        # BEERS (from PDF)
        ('Snapp', 'Beers', 'bottle', 181, 0, 5, 250),
        ('Guarana', 'Beers', 'bottle', 181, 23, 5, 250),
        ('Black Ice', 'Beers', 'bottle', 181, 22, 5, 250),
        ('Pineapple Punch', 'Beers', 'bottle', 181, 19, 5, 250),
        ('Tusker Malt', 'Beers', 'bottle', 247, 0, 5, 250),
        ('Heineken', 'Beers', 'bottle', 287, 0, 5, 350),
        ('Tusker Lager', 'Beers', 'bottle', 203, 21, 5, 300),
        ('Faxe', 'Beers', 'bottle', 263, 9, 5, 320),
        ('Martens Beer', 'Beers', 'bottle', 263, 5, 5, 320),
        ('Tusker Lite', 'Beers', 'bottle', 247, 0, 5, 250),
        ('Guinness', 'Beers', 'bottle', 220, 22, 5, 300),  # 23-1 sale = 22
        ('Kingfisher', 'Beers', 'bottle', 192, 0, 5, 250),
        ('Hunters Gold', 'Beers', 'bottle', 203, 0, 5, 250),
        ('Balozi', 'Beers', 'bottle', 203, 18, 5, 300),
        ('Pilsner', 'Beers', 'bottle', 203, 0, 5, 300),
        ('Whitecap', 'Beers', 'bottle', 220, 17, 5, 300),
        ('Savannah', 'Beers', 'bottle', 240, 0, 5, 200),
        ('KO', 'Beers', 'bottle', 220, 3, 5, 300),
        ('Tusker Cider', 'Beers', 'bottle', 241, 19, 5, 300),
        ('Banana Beer', 'Beers', 'bottle', 72, 43, 5, 150),

        # 1 LITRE SPIRITS
        ('Flirt Vodka', 'Spirits 1L', 'bottle', 1030, 1, 2, 1700),
        ('Ballantines', 'Spirits 1L', 'bottle', 2679, 2, 2, 3600),
        ('Double Black', 'Spirits 1L', 'bottle', 5550, 2, 2, 6800),
        ('J & B', 'Spirits 1L', 'bottle', 2017, 2, 2, 2700),
        ('Red Label', 'Spirits 1L', 'bottle', 2050, 3, 2, 2700),
        ('Black Label', 'Spirits 1L', 'bottle', 3810, 4, 2, 4500),
        ('Black & White', 'Spirits 1L', 'bottle', 1525, 4, 2, 2000),
        ('Jagermeister', 'Spirits 1L', 'bottle', 3100, 2, 2, 3700),
        ('Jameson', 'Spirits 1L', 'bottle', 3024, 3, 2, 3350),
        ('Gordons', 'Spirits 1L', 'bottle', 2348, 0, 2, 2348),
        ('Jack Daniels', 'Spirits 1L', 'bottle', 3850, 3, 2, 4500),
        ('Baileys Original', 'Spirits 1L', 'bottle', 2720, 0, 2, 3600),
        ('Captain Morgan Spiced', 'Spirits 1L', 'bottle', 2184, 6, 2, 2500),
        ('Captain Morgan Gold', 'Spirits 1L', 'bottle', 2184, 0, 2, 2500),
        ('Malibu', 'Spirits 1L', 'bottle', 1575, 2, 2, 2500),
        ('Absolut Vodka', 'Spirits 1L', 'bottle', 2577, 0, 2, 2577),
        ('4th Street 1.5L', 'Spirits 1L', 'bottle', 1680, 1, 2, 2000),
        ('Jim Beam', 'Spirits 1L', 'bottle', 2415, 2, 2, 2600),

        # 750ML SPIRITS
        ('Black & White 750ML', 'Spirits 750ML', 'bottle', 1155, 3, 2, 1500),
        ('Jim Beam 750ML', 'Spirits 750ML', 'bottle', 2195, 2, 2, 1700),
        ('Black Label 750ML', 'Spirits 750ML', 'bottle', 3077, 3, 2, 3600),
        ('Baileys Original 750ML', 'Spirits 750ML', 'bottle', 2225, 0, 2, 2600),
        ('Jameson 750ML', 'Spirits 750ML', 'bottle', 2268, 4, 2, 2750),
        ('Jagermeister 750ML', 'Spirits 750ML', 'bottle', 2365, 2, 2, 3200),
        ('Red Label 750ML', 'Spirits 750ML', 'bottle', 1648, 3, 2, 2700),
        ('Malibu 750ML', 'Spirits 750ML', 'bottle', 1563, 3, 2, 2200),
        ('4th Street 750ML', 'Spirits 750ML', 'bottle', 915, 3, 2, 1200),
        ('J & B 750ML', 'Spirits 750ML', 'bottle', 1932, 1, 2, 2400),
        ('Captain Morgan 750ML', 'Spirits 750ML', 'bottle', 948, 5, 2, 1300),
        ('Grants 750ML', 'Spirits 750ML', 'bottle', 1738, 6, 2, 2200),
        ('Kibao 750ML', 'Spirits 750ML', 'bottle', 649, 9, 2, 850),
        ('Kenya Cane 750ML', 'Spirits 750ML', 'bottle', 692, 5, 2, 1000),
        ('Kenya Cane Pineapple 750ML', 'Spirits 750ML', 'bottle', 692, 17, 2, 1000),
        ('Smirnoff 750ML', 'Spirits 750ML', 'bottle', 1277, 10, 2, 1600),
        ('Kenya King', 'Spirits 750ML', 'bottle', 616, 3, 2, 800),
        ('Jack Daniels 750ML', 'Spirits 750ML', 'bottle', 3100, 4, 2, 3500),
        ('Four Cousins', 'Wine', 'bottle', 920, 6, 2, 1200),
        ('Famous Grouse', 'Spirits 750ML', 'bottle', 1875, 2, 2, 2500),
        ('Konyagi 750ML', 'Spirits 750ML', 'bottle', 803, 8, 2, 1100),

        # 500ML SPIRITS
        ('Konyagi 500ML', 'Spirits 500ML', 'bottle', 572, 9, 2, 700),
        ('Chrome Gin 500ML', 'Spirits 500ML', 'bottle', 577, 8, 2, 850),
        ('Chrome Vodka 500ML', 'Spirits 500ML', 'bottle', 577, 8, 2, 800),
        ('Best Whisky 500ML', 'Spirits 500ML', 'bottle', 922, 8, 2, 1100),
        ('Best Gin 500ML', 'Spirits 500ML', 'bottle', 743, 12, 2, 950),
        ('Best Cream 500ML', 'Spirits 500ML', 'bottle', 999, 0, 2, 1200),
        ('Origin 500ML', 'Spirits 500ML', 'bottle', 626, 7, 2, 850),
        ('Kane Extra 500ML', 'Spirits 500ML', 'bottle', 593, 4, 2, 850),
        ('All Seasons 500ML', 'Spirits 500ML', 'bottle', 1050, 8, 2, 1300),
        ('VAT 69 500ML', 'Spirits 500ML', 'bottle', 1442, 4, 2, 1600),
        ('Chamdor', 'Wine', 'bottle', 747, 0, 2, 1000),
        ('Hennessy', 'Spirits 500ML', 'bottle', 5200, 1, 1, 6000),
        ('Martell', 'Spirits 500ML', 'bottle', 4500, 1, 1, 5800),
        ('Amarulla 500ML', 'Spirits 500ML', 'bottle', 2060, 0, 2, 2200),
        ('Chivas Regal', 'Spirits 500ML', 'bottle', 3682, 1, 1, 3850),
        ('Ballantines 500ML', 'Spirits 500ML', 'bottle', 2009, 3, 2, 2500),
        ('Bacardi', 'Spirits 500ML', 'bottle', 1700, 3, 2, 2000),
        ('Viceroy 500ML', 'Spirits 500ML', 'bottle', 1265, 4, 2, 1600),
        ('Drostdy Hof', 'Wine', 'bottle', 930, 2, 2, 1200),
        ('Richot 500ML', 'Spirits 500ML', 'bottle', 1277, 2, 2, 1600),
        ('Gilbeys 500ML', 'Spirits 500ML', 'bottle', 1277, 7, 2, 1600),
        ('Bond 7 500ML', 'Spirits 500ML', 'bottle', 1277, 3, 2, 1600),
        ('Beefeaters Gin Pink', 'Spirits 500ML', 'bottle', 2733, 2, 1, 3000),
        ('Beefeaters Gin', 'Spirits 500ML', 'bottle', 2570, 2, 1, 3300),
        ('Gordons Gin Pink', 'Spirits 500ML', 'bottle', 1895, 0, 2, 2200),
        ('Gordons Gin 500ML', 'Spirits 500ML', 'bottle', 1977, 2, 2, 2300),
        ('Hunters Choice 500ML', 'Spirits 500ML', 'bottle', 922, 6, 2, 1300),
        ('Caprice White', 'Wine', 'bottle', 743, 4, 2, 1000),
        ('Caprice Red', 'Wine', 'bottle', 743, 2, 2, 1000),
        ('Casabuena White', 'Wine', 'bottle', 711, 0, 2, 1000),
        ('Casabuena Red', 'Wine', 'bottle', 711, 0, 2, 1000),
        ('Absolut Vodka 500ML', 'Spirits 500ML', 'bottle', 1853, 2, 2, 2400),
        ('County 500ML', 'Spirits 500ML', 'bottle', 662, 13, 5, 850),
        ('Old Munk 500ML', 'Spirits 500ML', 'bottle', 1050, 3, 2, 1200),
        ('Robertson Wine', 'Wine', 'bottle', 1050, 2, 2, 1200),
        ('General Meakins 500ML', 'Spirits 500ML', 'bottle', 635, 5, 5, 850),

        # 350ML SPIRITS
        ('VAT 69 350ML', 'Spirits 350ML', 'bottle', 783, 5, 5, 1000),
        ('Amarulla 350ML', 'Spirits 350ML', 'bottle', 1185, 0, 2, 1200),
        ('All Seasons 350ML', 'Spirits 350ML', 'bottle', 535, 4, 5, 750),
        ('Viceroy 350ML', 'Spirits 350ML', 'bottle', 783, 7, 5, 900),
        ('Grants 350ML', 'Spirits 350ML', 'bottle', 885, 0, 2, 1000),
        ('Richot 350ML', 'Spirits 350ML', 'bottle', 593, 5, 5, 900),
        ('William Lawson', 'Spirits 350ML', 'bottle', 759, 2, 2, 1000),
        ('Kibao 350ML', 'Spirits 350ML', 'bottle', 350, 10, 10, 600),
        ('Black & White 350ML', 'Spirits 350ML', 'bottle', 593, 5, 5, 800),
        ('Jack Daniels 350ML', 'Spirits 350ML', 'bottle', 1640, 1, 1, 2000),
        ('Gilbeys 350ML', 'Spirits 350ML', 'bottle', 593, 8, 5, 800),
        ('Smirnoff 350ML', 'Spirits 350ML', 'bottle', 593, 14, 5, 700),
        ('Kenya Cane Pineapple 350ML', 'Spirits 350ML', 'bottle', 450, 0, 5, 450),
        ('Kenya Cane 350ML', 'Spirits 350ML', 'bottle', 363, 10, 10, 600),
        ('Jameson 350ML', 'Spirits 350ML', 'bottle', 1133, 7, 2, 1400),
        ('Hunters Choice 350ML', 'Spirits 350ML', 'bottle', 437, 12, 5, 650),
        ('58 Gin', 'Spirits 350ML', 'bottle', 366, 8, 5, 800),

        # 250ML SPIRITS - These have detailed stock from PDF
        ('All Seasons 250ML', 'Spirits 250ML', 'bottle', 365, 10, 10, 500),
        ('Kenya Cane 250ML', 'Spirits 250ML', 'bottle', 264, 59, 20, 350),  # 62-3 sales = 59
        ('Kenya Cane Pineapple 250ML', 'Spirits 250ML', 'bottle', 264, 0, 10, 380),
        ('Smirnoff 250ML', 'Spirits 250ML', 'bottle', 429, 15, 10, 550),
        ('Best Gin 250ML', 'Spirits 250ML', 'bottle', 265, 18, 10, 350),
        ('Best Whisky 250ML', 'Spirits 250ML', 'bottle', 318, 16, 10, 450),  # 17-1 sale = 16
        ('General Meakins 250ML', 'Spirits 250ML', 'bottle', 217, 62, 20, 300),  # 62.5-0.5 sale = 62
        ('Blue Ice 250ML', 'Spirits 250ML', 'bottle', 155, 124.5, 30, 200),  # 138.5-14 sales = 124.5
        ('Origin 250ML', 'Spirits 250ML', 'bottle', 239, 9, 10, 300),  # 9.5-0.5 sale = 9
        ('County 250ML', 'Spirits 250ML', 'bottle', 239, 29, 20, 300),  # 44.5-15.5 sales = 29
        ('Chrome Lemon', 'Spirits 250ML', 'bottle', 239, 15, 10, 300),
        ('Chrome Gin 250ML', 'Spirits 250ML', 'bottle', 214, 111.5, 30, 300),  # 116-4.5 sales = 111.5
        ('Best Cream 250ML', 'Spirits 250ML', 'bottle', 326, 4, 5, 500),
        ('Napoleon', 'Spirits 250ML', 'bottle', 217, 15.5, 10, 300),
        ('Konyagi 250ML', 'Spirits 250ML', 'bottle', 286, 16, 10, 350),
        ('Hunters Choice 250ML', 'Spirits 250ML', 'bottle', 303, 20, 10, 400),
        ('Gilbeys 250ML', 'Spirits 250ML', 'bottle', 429, 21, 10, 550),
        ('Triple Ace', 'Spirits 250ML', 'bottle', 217, 13.5, 10, 300),
        ('Viceroy 250ML', 'Spirits 250ML', 'bottle', 443, 7, 5, 550),
        ('VAT 69 250ML', 'Spirits 250ML', 'bottle', 305, 0, 5, 600),
        ('Richot 250ML', 'Spirits 250ML', 'bottle', 429, 4, 5, 550),
        ('Captain Morgan 250ML', 'Spirits 250ML', 'bottle', 346, 10, 5, 450),
        ('V&A', 'Spirits 250ML', 'bottle', 305, 10, 5, 450),
        ('White Pearl', 'Spirits 250ML', 'bottle', 227, 6.5, 10, 300),  # 7-0.5 sale = 6.5
        ('Kibao 250ML', 'Spirits 250ML', 'bottle', 230, 57.5, 20, 300),  # 62-4.5 sales = 57.5
        ('Kane Extra 250ML', 'Spirits 250ML', 'bottle', 214, 20.5, 10, 300),
        ('Bond 7 250ML', 'Spirits 250ML', 'bottle', 429, 3, 5, 550),

        # SOFT DRINKS
        ('Delmonte', 'Soft Drinks', 'bottle', 252, 14, 10, 350),
        ('Predator', 'Soft Drinks', 'bottle', 27, 30, 20, 70),  # 31-1 sale = 30
        ('Lemonade', 'Soft Drinks', 'bottle', 11, 28, 20, 50),  # 29-1 sale = 28
        ('Redbull', 'Soft Drinks', 'can', 184, 5, 5, 250),
        ('Powerplay', 'Soft Drinks', 'bottle', 27, 21, 20, 70),  # 23-2 sales = 21
        ('Monster', 'Soft Drinks', 'can', 252, 3, 5, 300),
        ('Soda 2L', 'Soft Drinks', 'bottle', 158, 0, 5, 200),
        ('Soda 1L', 'Soft Drinks', 'bottle', 158, 0, 10, 100),
        ('Soda 1.25L', 'Soft Drinks', 'bottle', 58, 26, 20, 150),
        ('Soda 500ML', 'Soft Drinks', 'bottle', 38, 0, 20, 50),
        ('Soda 350ML', 'Soft Drinks', 'bottle', 41, 53, 30, 50),
        ('Minute Maid 400ML', 'Soft Drinks', 'bottle', 33, 38, 30, 80),
        ('Minute Maid 1L', 'Soft Drinks', 'bottle', 125, 39, 20, 150),
        ('Water 1L', 'Soft Drinks', 'bottle', 39, 20, 20, 100),
        ('Water 500ML', 'Soft Drinks', 'bottle', 22, 25, 30, 50),
        ('Novida', 'Soft Drinks', 'bottle', 38, 1, 10, 50),
        ('Lime', 'Miscellaneous', 'piece', 10, 29, 20, 20),  # Started 32, sold 3 first, then more later

        # THE MISSING ITEMS - "tots" section and other items
        ('County 750ML', 'Spirits 750ML', 'bottle', 662, 3, 5, 850),  # This is where the tots came from
        ('Old Munk Purchase', 'Miscellaneous', 'bottle', 1100, 3, 2, 1200),  # The purchase entry
    ]

    # Create products and variants
    product_count = 0
    variant_count = 0

    for product_data in products_data:
        name, category_name, base_unit, buying_price, current_stock, min_stock, selling_price = product_data

        # Get or create product
        product = Product.query.filter_by(name=name).first()
        if not product:
            product = Product(
                name=name,
                category_id=category_map[category_name].id,
                base_unit=base_unit,
                base_buying_price=buying_price,
                current_stock=current_stock,
                min_stock_level=min_stock,
                created_by=admin.id
            )
            db.session.add(product)
            product_count += 1
        else:
            # Update stock if product exists
            product.current_stock = current_stock
            product.base_buying_price = buying_price

        db.session.flush()  # Flush to get the product ID

        # Create product variant for full bottle/can/piece
        existing_variant = ProductVariant.query.filter_by(
            product_id=product.id,
            size_id=size_map['Full Bottle'].id
        ).first()

        if not existing_variant:
            full_bottle_variant = ProductVariant(
                product_id=product.id,
                size_id=size_map['Full Bottle'].id,
                selling_price=selling_price,
                conversion_factor=1.0,  # 1 variant = 1 base unit
                created_by=admin.id
            )
            db.session.add(full_bottle_variant)
            variant_count += 1
        else:
            existing_variant.selling_price = selling_price

    db.session.commit()

    # NOW ADD THE TOTS - County 750ML should have tots available
    county_750ml = Product.query.filter_by(name='County 750ML').first()
    if county_750ml:
        # Check if tot variant already exists
        existing_tot_variant = ProductVariant.query.filter_by(
            product_id=county_750ml.id,
            size_id=size_map['Tot'].id
        ).first()

        if not existing_tot_variant:
            # Create tot variant for County 750ML
            tot_variant = ProductVariant(
                product_id=county_750ml.id,
                size_id=size_map['Tot'].id,
                selling_price=10,  # Based on PDF tots pricing
                conversion_factor=0.04,  # 1 tot = 1/25 of bottle (25 tots per bottle approx)
                created_by=admin.id
            )
            db.session.add(tot_variant)
            variant_count += 1
            db.session.commit()

    print(f"✓ Created/updated {product_count} products")
    print(f"✓ Created/updated {variant_count} product variants")
    print("✓ Added tots variant for County 750ML")

    # Record the sales that happened on 7/8/2025
    sales_data = [
        # (product_name, size_name, quantity, unit_price, attendant_name)
        ('Guinness', 'Full Bottle', 1, 300, 'Shop Attendant'),
        ('Kenya Cane 250ML', 'Full Bottle', 3, 350, 'Shop Attendant'),
        ('Best Whisky 250ML', 'Full Bottle', 1, 450, 'Shop Attendant'),
        ('General Meakins 250ML', 'Full Bottle', 0.5, 300, 'Shop Attendant'),
        ('Blue Ice 250ML', 'Full Bottle', 14, 200, 'Shop Attendant'),
        ('Origin 250ML', 'Full Bottle', 0.5, 300, 'Shop Attendant'),
        ('County 250ML', 'Full Bottle', 15.5, 300, 'Shop Attendant'),
        ('Chrome Gin 250ML', 'Full Bottle', 4.5, 300, 'Shop Attendant'),
        ('White Pearl', 'Full Bottle', 0.5, 300, 'Shop Attendant'),
        ('Kibao 250ML', 'Full Bottle', 4.5, 300, 'Shop Attendant'),
        ('Predator', 'Full Bottle', 1, 70, 'Shop Attendant'),
        ('Lemonade', 'Full Bottle', 1, 50, 'Shop Attendant'),
        ('Powerplay', 'Full Bottle', 2, 70, 'Shop Attendant'),
        ('Lime', 'Full Bottle', 3, 20, 'Shop Attendant'),  # First 3 sold
        # The tots sales - 50 tots sold from County 750ML
        ('County 750ML', 'Tot', 50, 10, 'Shop Attendant'),  # 50 tots sold
    ]

    sales_count = 0
    total_sales_amount = 0

    for product_name, size_name, quantity, unit_price, attendant_name in sales_data:
        # Find variant
        product = Product.query.filter_by(name=product_name).first()
        size = Size.query.filter_by(name=size_name).first()

        if product and size:
            variant = ProductVariant.query.filter_by(
                product_id=product.id,
                size_id=size.id
            ).first()

            if variant:
                sale_amount = quantity * unit_price
                sale = Sale(
                    variant_id=variant.id,
                    attendant_id=admin.id,  # Using admin as default attendant
                    quantity=quantity,
                    unit_price=unit_price,
                    original_amount=sale_amount,
                    discount_type='none',
                    discount_value=0,
                    discount_amount=0,
                    total_amount=sale_amount,
                    cash_amount=sale_amount,
                    mpesa_amount=0,
                    credit_amount=0,
                    sale_date=stock_date,
                    payment_method='cash'
                )
                sale.calculate_discount()
                db.session.add(sale)
                sales_count += 1
                total_sales_amount += sale_amount

                # Update product stock
                product.reduce_stock(quantity * variant.conversion_factor)
            else:
                print(f"⚠️  Warning: Could not find variant for {product_name} - {size_name}")
        else:
            print(f"⚠️  Warning: Could not find product '{product_name}' or size '{size_name}'")

    db.session.commit()
    print(f"✓ Created {sales_count} sales records")
    print(f"✓ Total sales amount: KES {total_sales_amount:,.2f}")

    # Create daily stock records for all products
    products = Product.query.all()
    daily_stock_count = 0

    for product in products:
        existing_daily_stock = DailyStock.query.filter_by(
            product_id=product.id,
            date=stock_date
        ).first()

        if not existing_daily_stock:
            # Calculate sales for this product on this date
            product_sales_query = db.session.query(db.func.sum(Sale.quantity * ProductVariant.conversion_factor)) \
                .join(ProductVariant, Sale.variant_id == ProductVariant.id) \
                .filter(
                ProductVariant.product_id == product.id,
                Sale.sale_date == stock_date
            )
            product_sales = product_sales_query.scalar() or 0

            daily_stock = DailyStock(
                product_id=product.id,
                date=stock_date,
                opening_stock=product.current_stock + product_sales,  # Back-calculate opening stock
                additions=0,
                sales_quantity=product_sales,
                closing_stock=product.current_stock,
                updated_by=admin.id
            )
            db.session.add(daily_stock)
            daily_stock_count += 1

    db.session.commit()
    print(f"✓ Created {daily_stock_count} daily stock records")

    # Create default expense category
    expense_cat = ExpenseCategory.query.filter_by(name='General').first()
    if not expense_cat:
        expense_cat = ExpenseCategory(
            name='General',
            description='General business expenses',
            created_by=admin.id
        )
        db.session.add(expense_cat)
        db.session.commit()
        print("✓ Created expense category")

    # Add some key summary info from the PDF
    print("\n" + "=" * 60)
    print("📊 STOCK SHEET SUMMARY (7/8/2025)")
    print("=" * 60)

    # Total inventory value
    total_buying_value = db.session.query(
        db.func.sum(Product.current_stock * Product.base_buying_price)
    ).scalar() or 0

    # Calculate selling value properly
    selling_value_query = db.session.query(
        db.func.sum(Product.current_stock * ProductVariant.selling_price)
    ).join(ProductVariant, Product.id == ProductVariant.product_id) \
        .filter(ProductVariant.conversion_factor == 1.0)
    total_selling_value = selling_value_query.scalar() or 0

    print(f"Total Buying Value: KES {total_buying_value:,.2f}")
    print(f"Total Selling Value: KES {total_selling_value:,.2f}")
    if total_selling_value > 0:
        print(f"Potential Profit: KES {total_selling_value - total_buying_value:,.2f}")

    # Sales summary from PDF
    print(f"\nSALES RECORDED: KES {total_sales_amount:,.2f}")
    print("PAYBILL: 8,970")  # From PDF
    print("CASH: 4,000")  # From PDF
    print("CREDIT: -")  # From PDF
    print("TOTAL: 12,970")  # From PDF - this doesn't match our calculated sales

    # Stock status
    total_products = Product.query.count()
    zero_stock = Product.query.filter(Product.current_stock <= 0).count()
    low_stock = Product.query.filter(
        Product.current_stock > 0,
        Product.current_stock <= Product.min_stock_level
    ).count()

    print(f"\nSTOCK STATUS:")
    print(f"Total Products: {total_products}")
    print(f"Out of Stock: {zero_stock}")
    print(f"Low Stock: {low_stock}")
    print(f"Good Stock: {total_products - zero_stock - low_stock}")

    # Show some low stock items
    low_stock_items = Product.query.filter(
        Product.current_stock > 0,
        Product.current_stock <= Product.min_stock_level
    ).limit(10).all()

    if low_stock_items:
        print(f"\nLOW STOCK ALERTS:")
        for item in low_stock_items:
            print(f"⚠️  {item.name}: {item.current_stock} {item.base_unit}s (min: {item.min_stock_level})")

    # Show out of stock items
    out_of_stock = Product.query.filter(Product.current_stock <= 0).limit(10).all()
    if out_of_stock:
        print(f"\nOUT OF STOCK:")
        for item in out_of_stock:
            print(f"❌ {item.name}")

    print("\n" + "=" * 60)
    print("✅ DATA INJECTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n🔐 Default Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   ⚠️  CHANGE THE PASSWORD IMMEDIATELY!")

    print("\n📝 Notes from PDF:")
    print("- Sales total in PDF shows 12,970 but individual sales don't add up")
    print("- Paybill: 8,970, Cash: 4,000 from PDF")
    print("- Some items like tissue, police, tumbler mentioned as purchases")
    print("- County 750ML was used to make tots (50 tots sold)")
    print("- Lime stock calculations: complex due to multiple transactions")
    print(f"- Script recorded {sales_count} individual sales totaling KES {total_sales_amount:,.2f}")


if __name__ == '__main__':
    # Create Flask app and database tables
    app = create_app()

    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✓ Database tables created/verified")

        try:
            # Inject the data
            inject_stock_data()

        except Exception as e:
            print(f"❌ Error during data injection: {str(e)}")
            import traceback

            traceback.print_exc()
            db.session.rollback()
            raise
        finally:
            db.session.close()