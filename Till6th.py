"""
Complete November Data Import Script for LiquorPro System
Imports stock data from November 1-6, 2025
Accurately reflects all data from the PDF including:
- Fractional quantities
- Variable selling prices
- All missing products
- Correct tots handling
Date: November 22, 2025
"""

from app import app, db
from models import (User, Category, Size, Product, ProductVariant,
                   Sale, DailyStock, StockPurchase, Expense, ExpenseCategory, DailySummary)
from datetime import datetime, date
from decimal import Decimal

# Import dates
IMPORT_DATES = [
    date(2025, 11, 1),
    date(2025, 11, 2),
    date(2025, 11, 3),
    date(2025, 11, 4),
    date(2025, 11, 5),
    date(2025, 11, 6),
]

# Structure: Product Name -> (Category, Buying Price, Daily Data)
# Daily Data: [(opening, additions, sales, selling_price), ...]
# selling_price can be None to use default price
PRODUCTS_DATA = {
    # BEERS
    "Snapp": ("Beers", 181, 250, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Guarana": ("Beers", 181, 250, [
        (15, 0, 3, None), (12, 0, 0, None), (12, 24, 2, None), (22, 0, 0, None), (22, 0, 0, None), (22, 0, 0, None)
    ]),
    "Black Ice": ("Beers", 181, 250, [
        (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None)
    ]),
    "Pineapple Punch": ("Beers", 181, 250, [
        (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None), (19, 0, 0, None)
    ]),
    "Tusker Malt": ("Beers", 247, 250, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Heineken": ("Beers", 287, 350, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Tusker Lager": ("Beers", 203, 300, [
        (19, 0, 0, None), (19, 0, 4, None), (15, 6, 0, None), (21, 0, 0, None), (21, 0, 0, None), (21, 0, 1, 280)
    ]),
    "Faxe": ("Beers", 263, 320, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Martens Beer": ("Beers", 263, 350, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Tusker Lite": ("Beers", 247, 250, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Guinness": ("Beers", 220, 300, [
        (22, 0, 0, None), (22, 0, 0, None), (22, 0, 0, None), (22, 0, 0, None), (22, 0, 0, None), (22, 0, 0, None)
    ]),
    "Kingfisher": ("Beers", 192, 250, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Hunters Gold": ("Beers", 203, 250, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Balozi": ("Beers", 203, 300, [
        (15, 0, 0, None), (15, 0, 0, None), (15, 6, 0, None), (21, 0, 0, None), (21, 0, 0, None), (21, 0, 0, None)
    ]),
    "Pilsner": ("Beers", 203, 300, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Whitecap": ("Beers", 220, 300, [
        (18, 0, 0, None), (18, 0, 0, None), (18, 0, 0, None), (18, 0, 0, None), (18, 0, 0, None), (18, 0, 0, None)
    ]),
    "Savannah": ("Beers", 240, 200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "KO": ("Beers", 220, 300, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Tusker Cider": ("Beers", 241, 300, [
        (14, 0, 1, None), (13, 0, 1, None), (12, 6, 0, None), (18, 0, 1, None), (17, 0, 1, None), (16, 0, 1, None)
    ]),
    "Banana Beer": ("Beers", 72, 130, [
        (33, 0, 0, None), (33, 0, 0, None), (33, 0, 0, None), (33, 0, 0, None), (33, 0, 0, None), (33, 0, 1, None)
    ]),

    # SPIRITS - 1 LITRE
    "Flirt Vodka 1L": ("Spirits", 1030, 1700, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Ballantines 1L": ("Spirits", 2679, 3600, [
        (2, 0, 0, None), (3, 0, 1, None), (1, 1, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Double Black 1L": ("Spirits", 5550, 6800, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "J&B 1L": ("Spirits", 2017, 2700, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Red Label 1L": ("Spirits", 2050, 2500, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Black Label 1L": ("Spirits", 3810, 4500, [
        (5, 0, 0, None), (5, 0, 1, None), (4, 1, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),
    "Black & White 1L": ("Spirits", 1525, 2000, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Jagermeister 1L": ("Spirits", 3100, 3700, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Jameson 1L": ("Spirits", 3024, 3700, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Gordons 1L": ("Spirits", 2348, 0, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Jack Daniels 1L": ("Spirits", 3850, 4500, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Baileys Original 1L": ("Spirits", 2720, 3600, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Captain Morgan Spiced 1L": ("Spirits", 2184, 2800, [
        (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),
    "Captain Morgan Gold 1L": ("Spirits", 2184, 2500, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Malibu 1L": ("Spirits", 1575, 2500, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Absolut Vodka 1L": ("Spirits", 2577, 0, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "4th Street 1.5L": ("Spirits", 1680, 2000, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "8PM 1L": ("Spirits", 1000, 1300, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Jim Beam 1L": ("Spirits", 2415, 2600, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),

    # SPIRITS - 750ML
    "Black & White 750ML": ("Spirits", 1155, 1500, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Jim Beam 750ML": ("Spirits", 2195, 1700, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Black Label 750ML": ("Spirits", 3077, 3600, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Baileys Original 750ML": ("Spirits", 2225, 2600, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Jameson 750ML": ("Spirits", 2268, 2750, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Jagermeister 750ML": ("Spirits", 2365, 3200, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Red Label 750ML": ("Spirits", 1648, 2000, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Malibu 750ML": ("Spirits", 1563, 2200, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "4th Street 750ML": ("Spirits", 915, 1200, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "J&B 750ML": ("Spirits", 1932, 2400, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Captain Morgan 750ML": ("Spirits", 948, 1300, [
        (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),
    "Grants 750ML": ("Spirits", 1738, 2200, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None)
    ]),
    "Kibao 750ML": ("Spirits", 649, 850, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Kenya Cane 750ML": ("Spirits", 692, 1000, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 5, 5, None), (1, 1, 1, None)
    ]),
    "Kenya Cane Pineapple 750ML": ("Spirits", 692, 1000, [
        (15, 0, 4, None), (11, 0, 0, None), (11, 7, 0, None), (18, 0, 0, None), (18, 0, 0, None), (18, 0, 2, None)
    ]),
    "Smirnoff 750ML": ("Spirits", 1277, 1600, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Kenya King 750ML": ("Spirits", 616, 800, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Jack Daniels 750ML": ("Spirits", 3100, 3500, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Four Cousins 750ML": ("Spirits", 920, 1200, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None)
    ]),
    "Famous Grouse 750ML": ("Spirits", 1875, 2500, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Konyagi 750ML": ("Spirits", 803, 1100, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),
    "Konyagi 500ML": ("Spirits", 572, 700, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Chrome Gin 750ML": ("Spirits", 577, 800, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),
    "Chrome Vodka 750ML": ("Spirits", 577, 850, [
        (11, 0, 0, None), (11, 0, 1, None), (10, 2, 0, None), (12, 0, 1, None), (11, 0, 3, 800), (8, 0, 0, None)
    ]),
    "Best Whisky 750ML": ("Spirits", 922, 1100, [
        (7, 0, 0, None), (7, 0, 1, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None)
    ]),
    "Best Gin 750ML": ("Spirits", 743, 950, [
        (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None)
    ]),
    "Best Cream 750ML": ("Spirits", 999, 1200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Origin 750ML": ("Spirits", 626, 850, [
        (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None)
    ]),
    "Kane Extra 750ML": ("Spirits", 593, 800, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "All Seasons 750ML": ("Spirits", 1050, 1300, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),
    "VAT 69 750ML": ("Spirits", 1442, 1600, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Chamdor 750ML": ("Spirits", 747, 1000, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Hennessy 750ML": ("Spirits", 5200, 6200, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Martell 750ML": ("Spirits", 4500, 5800, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Amarula 750ML": ("Spirits", 2060, 2200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Chivas Regal 750ML": ("Spirits", 3682, 3850, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Ballantines 750ML": ("Spirits", 2009, 2500, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Bacardi 750ML": ("Spirits", 1700, 2000, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Viceroy 750ML": ("Spirits", 1265, 1600, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Drostdy Hof 750ML": ("Spirits", 930, 1200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Richot 750ML": ("Spirits", 1277, 1600, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Gilbeys 750ML": ("Spirits", 1277, 1600, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None)
    ]),
    "Bond 7 750ML": ("Spirits", 1277, 1600, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Beefeaters Gin Pink 750ML": ("Spirits", 2733, 3000, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Beefeaters Gin 750ML": ("Spirits", 2570, 3300, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Gordons Gin Pink 750ML": ("Spirits", 1895, 2200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Gordons Gin 750ML": ("Spirits", 1977, 2300, [
        (2, 0, 1, None), (1, 2, 1, None), (1, 1, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Hunters Choice 750ML": ("Spirits", 922, 1300, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None), (6, 0, 0, None)
    ]),
    "8PM 750ML": ("Spirits", 922, 1300, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Caprice White 750ML": ("Wines", 743, 1000, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Caprice Red 750ML": ("Wines", 743, 1000, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Casabuena White 750ML": ("Wines", 711, 1000, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Casabuena Red 750ML": ("Wines", 711, 1000, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Absolut Vodka 750ML": ("Spirits", 1853, 2400, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "County 750ML": ("Spirits", 662, 850, [
        (11, 0, 2, None), (9, 0, 0, None), (9, 3, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None)
    ]),
    "Old Monk 750ML": ("Spirits", 1050, 1200, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Robertson Wine 750ML": ("Wines", 1050, 1200, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "General Meakins 750ML": ("Spirits", 635, 800, [
        (4, 0, 0, None), (4, 0, 1, 850), (3, 1, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),

    # SPIRITS - 350ML
    "VAT 69 350ML": ("Spirits", 783, 1000, [
        (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 1, None), (4, 0, 0, None)
    ]),
    "Amarula 350ML": ("Spirits", 1185, 1200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "All Seasons 350ML": ("Spirits", 535, 750, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None), (4, 0, 0, None)
    ]),
    "Viceroy 350ML": ("Spirits", 783, 900, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),
    "Grants 350ML": ("Spirits", 885, 1000, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Richot 350ML": ("Spirits", 593, 900, [
        (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),
    "William Lawson 350ML": ("Spirits", 759, 1000, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Kibao 350ML": ("Spirits", 350, 600, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Black & White 350ML": ("Spirits", 593, 800, [
        (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),
    "Jack Daniels 350ML": ("Spirits", 1640, 2000, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Gilbeys 350ML": ("Spirits", 593, 800, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),
    "Smirnoff 350ML": ("Spirits", 593, 700, [
        (14, 0, 0, None), (14, 0, 0, None), (14, 0, 0, None), (14, 0, 0, None), (14, 0, 0, None), (14, 0, 0, None)
    ]),
    "Kenya Cane Pineapple 350ML": ("Spirits", 0, 450, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Kenya Cane 350ML": ("Spirits", 363, 650, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Jameson 350ML": ("Spirits", 1133, 1500, [
        (7, 0, 0, None), (7, 0, 0, None), (7, 0, 0, None), (7, 0, 0, None), (7, 0, 0, None), (7, 0, 1, 1400)
    ]),
    "Hunters Choice 350ML": ("Spirits", 437, 650, [
        (11, 0, 0, None), (11, 0, 0, None), (11, 1, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None)
    ]),
    "58 Gin 350ML": ("Spirits", 366, 800, [
        (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 0, None)
    ]),

    # SPIRITS - 250ML
    "All Seasons 250ML": ("Spirits", 365, 500, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Kenya Cane 250ML": ("Spirits", 264, 350, [
        (47, 0, 8, None), (39, 0, 13, None), (26, 37, 11, None), (52, 25, 1, None), (76, 0, 12, None), (64, 0, 10, None)
    ]),
    "Kenya Cane Pineapple 250ML": ("Spirits", 264, 380, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Smirnoff 250ML": ("Spirits", 429, 550, [
        (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Best Gin 250ML": ("Spirits", 265, 400, [
        (18, 0, 0, None), (18, 0, 4, 350), (14, 4, 0, None), (18, 0, 0, None), (18, 0, 0, None), (18, 0, 0, None)
    ]),
    "Best Whisky 250ML": ("Spirits", 318, 450, [
        (17, 0, 0, None), (17, 0, 1, 400), (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None)
    ]),
    "General Meakins 250ML": ("Spirits", 217, 300, [
        (62, 0, 1, None), (61, 0, 2.5, None), (58.5, 5, 0.5, None), (63, 0, 1, None), (62, 0, 0, None), (62, 0, 0, None)
    ]),
    "Blue Ice 250ML": ("Spirits", 155, 200, [
        (91.5, 0, 15.75, None), (75.75, 0, 7.75, None), (68, 100, 16.75, None), (151.25, 0, 7.25, None), (144, 0, 9, None), (135, 0, 12.5, None)
    ]),
    "Origin 250ML": ("Spirits", 239, 300, [
        (15.5, 0, 0, None), (15.5, 0, 0, None), (15.5, 0, 0.5, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "County 250ML": ("Spirits", 239, 300, [
        (65.5, 0, 2.5, None), (63, 0, 0.5, None), (62.5, 0, 4.5, None), (58, 0, 2, None), (56, 0, 2.5, None), (53.5, 0, 2.5, None)
    ]),
    "Chrome Lemon 250ML": ("Spirits", 239, 300, [
        (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Chrome Gin 250ML": ("Spirits", 214, 300, [
        (100, 0, 4, None), (96, 0, 6.5, None), (89.5, 41, 4, None), (126.5, 0, 1.5, None), (125, 0, 8.5, None), (116.5, 0, 2, None)
    ]),
    "Best Cream 250ML": ("Spirits", 326, 500, [
        (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None), (3, 0, 0, None)
    ]),
    "Napoleon 250ML": ("Spirits", 217, 300, [
        (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Konyagi 250ML": ("Spirits", 286, 350, [
        (13, 0, 0, None), (13, 0, 0, None), (13, 1, 1, None), (13, 0, 0, None), (13, 0, 0, None), (13, 0, 0, None)
    ]),
    "Hunters Choice 250ML": ("Spirits", 303, 400, [
        (19, 0, 0, None), (19, 0, 1, None), (18, 2, 0, None), (20, 0, 0, None), (20, 0, 0, None), (20, 0, 0, None)
    ]),
    "Gilbeys 250ML": ("Spirits", 429, 550, [
        (21, 0, 0, None), (21, 0, 0, None), (21, 0, 0, None), (21, 0, 0, None), (21, 0, 0, None), (21, 0, 0, None)
    ]),
    "Triple Ace 250ML": ("Spirits", 217, 300, [
        (13.5, 0, 0, None), (13.5, 0, 0, None), (13.5, 2, 0, None), (15.5, 0, 0, None), (15.5, 0, 0, None), (15.5, 0, 0, None)
    ]),
    "Viceroy 250ML": ("Spirits", 443, 550, [
        (8, 0, 0, None), (8, 0, 1, None), (7, 1, 0, None), (8, 0, 0, None), (8, 0, 0, None), (8, 0, 1, None)
    ]),
    "VAT 69 250ML": ("Spirits", 305, 600, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Richot 250ML": ("Spirits", 429, 550, [
        (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None), (9, 0, 0, None)
    ]),
    "Captain Morgan 250ML": ("Spirits", 346, 450, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "V&A 250ML": ("Spirits", 305, 450, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "White Pearl 250ML": ("Spirits", 227, 300, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Caribia 250ML": ("Spirits", 230, 350, [
        (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None), (10, 0, 0, None)
    ]),
    "Liberty 250ML": ("Spirits", 230, 300, [
        (6, 0, 0, None), (6, 0, 0, None), (6, 4, 0, None), (10, 0, 0.5, None), (9.5, 0, 1.5, None), (8, 0, 3.5, None)
    ]),
    "Kibao 250ML": ("Spirits", 230, 300, [
        (63.5, 0, 2, None), (61.5, 0, 0, None), (61.5, 0, 1.5, None), (60, 0, 1.5, None), (58.5, 0, 1.5, None), (57, 0, 4.5, None)
    ]),
    "Kane Extra 250ML": ("Spirits", 214, 300, [
        (19, 0, 0, None), (19, 0, 4, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Bond 7 250ML": ("Spirits", 429, 550, [
        (4, 0, 0, None), (4, 0, 0, None), (4, 1, 0, None), (5, 0, 0, None), (5, 0, 0, None), (5, 0, 0, None)
    ]),

    # SOFT DRINKS
    "Delmonte": ("Soft Drinks", 252, 300, [
        (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None), (12, 0, 0, None)
    ]),
    "Predator": ("Soft Drinks", 27, 70, [
        (31, 0, 4, None), (27, 0, 4, None), (23, 0, 0, None), (26, 0, 5, None), (21, 0, 2, None), (19, 0, 4, None)
    ]),
    "Lemonade": ("Soft Drinks", 11, 50, [
        (22, 0, 0, None), (22, 0, 1, None), (21, 12, 0, None), (33, 0, 0, None), (33, 0, 2, None), (31, 0, 1, None)
    ]),
    "Redbull": ("Soft Drinks", 184, 250, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Powerplay": ("Soft Drinks", 27, 70, [
        (25, 0, 3, None), (22, 0, 5, None), (17, 0, 1, None), (16, 0, 1, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Monster": ("Soft Drinks", 252, 300, [
        (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None), (1, 0, 0, None)
    ]),
    "Soda 2L": ("Soft Drinks", 158, 200, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Soda 1L": ("Soft Drinks", 158, 100, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Soda 1.25L": ("Soft Drinks", 58, 150, [
        (27, 0, 0, None), (27, 0, 5, None), (22, 0, 0, None), (22, 0, 0, None), (22, 0, 2, None), (20, 0, 0, None)
    ]),
    "Soda 500ML": ("Soft Drinks", 38, 50, [
        (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None), (0, 0, 0, None)
    ]),
    "Soda 350ML": ("Soft Drinks", 41, 50, [
        (102, 0, 6, None), (96, 0, 6, None), (90, 0, 2, None), (88, 0, 5, None), (83, 0, 3, None), (80, 0, 3, None)
    ]),
    "Minute Maid 400ML": ("Soft Drinks", 33, 80, [
        (49, 0, 0, None), (49, 0, 3, None), (46, 0, 2, None), (44, 0, 2, None), (42, 0, 4, None), (38, 0, 5, None)
    ]),
    "Minute Maid 1L": ("Soft Drinks", 125, 150, [
        (51, 0, 0, None), (51, 0, 3, None), (48, 0, 0, None), (48, 0, 0, None), (48, 0, 0, None), (48, 0, 0, None)
    ]),
    "Water 1L": ("Soft Drinks", 39, 100, [
        (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None), (16, 0, 0, None)
    ]),
    "Water 500ML": ("Soft Drinks", 22, 50, [
        (20, 0, 2, None), (18, 0, 2, None), (16, 0, 1, None), (15, 0, 0, None), (15, 0, 0, None), (15, 0, 0, None)
    ]),
    "Novida": ("Soft Drinks", 38, 50, [
        (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None), (2, 0, 0, None)
    ]),
    "Lime": ("Soft Drinks", 10, 10, [
        (0, 32, 0, None), (0, 32, 0, None), (0, 32, 2, 20), (0, 32, 3, 20), (0, 32, 2, 20), (0, 32, 1, 20)
    ]),
}

# Tots sales data - these are sold from County 750ML bottle at 50 KES per tot
# Format: (date_index, quantity_sold)
TOTS_SALES = [
    (0, 6),   # Nov 1: 6 tots
    (1, 0),   # Nov 2: 0 tots
    (2, 1),   # Nov 3: 1 tot
    (3, 0),   # Nov 4: 0 tots
    (4, 0),   # Nov 5: 0 tots
    (5, 0),   # Nov 6: 0 tots
]

# Expenses data - Format: [(date_index, description, amount, category), ...]
EXPENSES_DATA = [
    (0, "Tissue", 20, "General Expenses"),
    (0, "Stocksheet", 50, "Office Supplies"),
    (0, "Police", 150, "Security"),
    (1, "Police", 250, "Security"),
    (1, "Stocksheet", 50, "Office Supplies"),
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
    return category

def get_or_create_size(name, description, sort_order):
    """Get or create a size"""
    size = Size.query.filter_by(name=name).first()
    if not size:
        admin = User.query.filter_by(role='admin').first()
        size = Size(
            name=name,
            description=description,
            sort_order=sort_order,
            created_by=admin.id if admin else None
        )
        db.session.add(size)
        db.session.flush()
    return size

def import_product_daily_data(product_name, category_name, buying_price, default_selling_price, daily_data):
    """Import a product and its daily stock movements with support for variable prices"""
    admin = User.query.filter_by(role='admin').first()
    category = Category.query.filter_by(name=category_name).first()

    # Get or create product
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        # Calculate final closing stock from last day's data
        last_day = daily_data[-1]
        closing = Decimal(str(last_day[0])) + Decimal(str(last_day[1])) - Decimal(str(last_day[2]))

        product = Product(
            name=product_name,
            category_id=category.id,
            base_unit='bottle',
            base_buying_price=buying_price,
            current_stock=float(closing),
            min_stock_level=5,
            created_by=admin.id if admin else None,
            last_stock_update=datetime.now()
        )
        db.session.add(product)
        db.session.flush()

    # Get or create "Full Bottle" size and variant
    full_bottle_size = get_or_create_size("Full Bottle", "Entire bottle/unit as purchased", 1)

    variant = ProductVariant.query.filter_by(
        product_id=product.id,
        size_id=full_bottle_size.id
    ).first()

    if not variant:
        variant = ProductVariant(
            product_id=product.id,
            size_id=full_bottle_size.id,
            selling_price=default_selling_price,
            conversion_factor=1.0,
            created_by=admin.id if admin else None
        )
        db.session.add(variant)
        db.session.flush()
    else:
        variant.selling_price = default_selling_price

    # Process each day's data
    for day_idx, day_tuple in enumerate(daily_data):
        opening, additions, sales, actual_price = day_tuple
        current_date = IMPORT_DATES[day_idx]

        # Use actual price if provided, otherwise use default
        selling_price = actual_price if actual_price is not None else default_selling_price

        # Convert to Decimal for precision
        opening_dec = Decimal(str(opening))
        additions_dec = Decimal(str(additions))
        sales_dec = Decimal(str(sales))

        # Create or update daily stock
        daily_stock = DailyStock.query.filter_by(
            product_id=product.id,
            date=current_date
        ).first()

        if not daily_stock:
            daily_stock = DailyStock(
                product_id=product.id,
                date=current_date,
                opening_stock=float(opening_dec),
                additions=0,
                sales_quantity=0,
                closing_stock=float(opening_dec),
                updated_by=admin.id if admin else None,
                updated_at=datetime.now()
            )
            db.session.add(daily_stock)
            db.session.flush()

        # Create stock purchase if additions > 0
        if additions_dec > 0:
            purchase = StockPurchase(
                product_id=product.id,
                quantity=float(additions_dec),
                unit_cost=buying_price,
                total_cost=float(additions_dec) * buying_price,
                purchase_date=current_date,
                notes=f"Stock purchase - {product_name}",
                recorded_by=admin.id if admin else None,
                timestamp=datetime.now()
            )
            db.session.add(purchase)
            db.session.flush()
            daily_stock.additions = float(additions_dec)

        # Create sale if sales > 0
        if sales_dec > 0:
            cost_per_unit = buying_price * variant.conversion_factor
            total_cost = cost_per_unit * float(sales_dec)
            total_amount = float(sales_dec) * selling_price

            sale = Sale(
                variant_id=variant.id,
                attendant_id=admin.id if admin else None,
                quantity=float(sales_dec),
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
                sale_date=current_date,
                timestamp=datetime.now(),
                notes=f"Sale - {product_name}" + (f" @ {selling_price}" if actual_price else "")
            )
            db.session.add(sale)
            db.session.flush()
            daily_stock.sales_quantity = float(sales_dec)

        # Calculate closing stock
        daily_stock.calculate_closing_stock()

    # Update product's final stock
    last_daily = DailyStock.query.filter_by(
        product_id=product.id,
        date=IMPORT_DATES[-1]
    ).first()
    if last_daily:
        product.current_stock = last_daily.closing_stock

    return product

def create_tot_variant_and_sales():
    """Create 'Tot (25ml)' variant for County 750ML and record tot sales"""
    admin = User.query.filter_by(role='admin').first()

    # Find County 750ML product
    county_product = Product.query.filter_by(name="County 750ML").first()
    if not county_product:
        print("⚠️  County 750ML product not found!")
        return

    # Create or get "Tot (25ml)" size
    tot_size = get_or_create_size("Tot (25ml)", "25ml shot/tot", 2)

    # Check if tot variant exists
    tot_variant = ProductVariant.query.filter_by(
        product_id=county_product.id,
        size_id=tot_size.id
    ).first()

    if not tot_variant:
        # 750ml bottle has 30 tots (750/25 = 30)
        # Conversion factor: 1 tot = 0.0333 bottles (1/30)
        tot_variant = ProductVariant(
            product_id=county_product.id,
            size_id=tot_size.id,
            selling_price=50,  # 50 KES per tot
            conversion_factor=0.0333,  # 1 tot = 0.0333 bottles
            created_by=admin.id if admin else None
        )
        db.session.add(tot_variant)
        db.session.flush()
        print(f"  ✓ Created 'Tot (25ml)' variant for County 750ML (Price: KES 50)")

    # Record tot sales
    for day_idx, quantity in TOTS_SALES:
        if quantity > 0:
            current_date = IMPORT_DATES[day_idx]

            # Calculate cost and profit
            cost_per_tot = county_product.base_buying_price * tot_variant.conversion_factor
            total_cost = cost_per_tot * quantity
            total_amount = quantity * 50

            sale = Sale(
                variant_id=tot_variant.id,
                attendant_id=admin.id if admin else None,
                quantity=quantity,
                unit_price=50,
                original_amount=total_amount,
                discount_type='none',
                discount_value=0,
                discount_amount=0,
                total_amount=total_amount,
                cash_amount=total_amount,
                mpesa_amount=0,
                credit_amount=0,
                payment_method='cash',
                sale_date=current_date,
                timestamp=datetime.now(),
                notes=f"County tots sale"
            )
            db.session.add(sale)
            print(f"    → Tot sale on {current_date}: {quantity} tots @ KES 50 = KES {total_amount}")

def import_expenses():
    """Import all expenses"""
    admin = User.query.filter_by(role='admin').first()

    print("\n💰 Importing Expenses...")
    print("-" * 70)

    for day_idx, description, amount, category_name in EXPENSES_DATA:
        expense_cat = get_or_create_expense_category(category_name)
        current_date = IMPORT_DATES[day_idx]

        expense = Expense(
            description=description,
            amount=amount,
            expense_category_id=expense_cat.id,
            expense_date=current_date,
            notes=f"From Excel import - {current_date}",
            recorded_by=admin.id
        )
        db.session.add(expense)
        print(f"  {current_date}: {description} - KES {amount} ({category_name})")

def update_daily_summaries():
    """Update daily summaries for all import dates"""
    admin = User.query.filter_by(role='admin').first()

    print("\n📊 Updating Daily Summaries...")
    print("-" * 70)

    for import_date in IMPORT_DATES:
        # Calculate totals from actual records
        total_sales = db.session.query(
            db.func.coalesce(db.func.sum(Sale.total_amount), 0)
        ).filter(Sale.sale_date == import_date).scalar() or 0

        total_expenses = db.session.query(
            db.func.coalesce(db.func.sum(Expense.amount), 0)
        ).filter(Expense.expense_date == import_date).scalar() or 0

        # Calculate profit from sales
        sales_with_profit = db.session.query(
            db.func.coalesce(db.func.sum(
                Sale.total_amount - (Product.base_buying_price * ProductVariant.conversion_factor * Sale.quantity)
            ), 0)
        ).join(ProductVariant).join(Product).filter(
            Sale.sale_date == import_date
        ).scalar() or 0

        # Calculate payment breakdown
        payment_breakdown = db.session.query(
            db.func.coalesce(db.func.sum(Sale.cash_amount), 0).label('cash'),
            db.func.coalesce(db.func.sum(Sale.mpesa_amount), 0).label('mpesa'),
            db.func.coalesce(db.func.sum(Sale.credit_amount), 0).label('credit')
        ).filter(Sale.sale_date == import_date).first()

        transaction_count = Sale.query.filter_by(sale_date=import_date).count()
        expense_count = Expense.query.filter_by(expense_date=import_date).count()

        # Create or update daily summary
        summary = DailySummary.query.filter_by(date=import_date).first()
        if not summary:
            summary = DailySummary(date=import_date)
            db.session.add(summary)

        summary.total_sales = total_sales
        summary.total_profit = sales_with_profit
        summary.total_expenses = total_expenses
        summary.net_profit = sales_with_profit - total_expenses
        summary.cash_amount = payment_breakdown.cash or 0
        summary.paybill_amount = payment_breakdown.mpesa or 0
        summary.credit_amount = payment_breakdown.credit or 0
        summary.last_updated_by = admin.id
        summary.last_updated_at = datetime.now()

        print(f"  {import_date}: Sales=KES {total_sales:,.2f}, Profit=KES {sales_with_profit:,.2f}, " +
              f"Expenses=KES {total_expenses:,.2f}, Net=KES {summary.net_profit:,.2f}")

def import_data():
    """Main import function that orchestrates the entire data import"""
    with app.app_context():
        print("\n" + "="*70)
        print("LIQUORPRO SYSTEM - COMPLETE NOVEMBER DATA IMPORT")
        print("="*70)

        try:
            # Create categories
            print("\n📁 Setting up categories...")
            get_or_create_category("Beers", "Alcoholic beverages - beers and ciders")
            get_or_create_category("Spirits", "Alcoholic spirits and liquors")
            get_or_create_category("Wines", "Wine products")
            get_or_create_category("Soft Drinks", "Non-alcoholic beverages")

            # Import all products
            print("\n📦 Importing Products & Daily Stock Data...")
            print("-" * 70)
            for product_name, (category, buying_price, selling_price, daily_data) in PRODUCTS_DATA.items():
                print(f"  → {product_name}")
                import_product_daily_data(product_name, category, buying_price, selling_price, daily_data)

            # Create tot variant and sales
            print("\n🥃 Creating Tot Variant & Sales...")
            create_tot_variant_and_sales()

            # Import expenses
            import_expenses()

            # Update daily summaries
            update_daily_summaries()

            # Commit everything
            db.session.commit()

            print("\n" + "="*70)
            print("✅ IMPORT COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"\nImported data for dates: {IMPORT_DATES[0]} to {IMPORT_DATES[-1]}")
            print(f"Total products: {len(PRODUCTS_DATA)}")
            print(f"Total expenses: {len(EXPENSES_DATA)}")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR during import: {str(e)}")
            print("Database changes have been rolled back.")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will import complete November 1-6, 2025 data.")
    print("   - Each size (750ML, 250ML) will be a SEPARATE product")
    print("   - Daily stock continuity will be maintained")
    print("   - Fractional quantities are supported (e.g., 2.5, 15.75)")
    print("   - Variable selling prices are tracked per transaction")
    print("   - County 750ML tots variant will be created automatically")
    print("   - All sales, purchases, and expenses will be recorded")
    print("   - Missing products (Lime, Old Monk, Robertson Wine) are included\n")

    response = input("Do you want to continue? (yes/no): ")
    if response.lower() == 'yes':
        import_data()
    else:
        print("Import cancelled.")