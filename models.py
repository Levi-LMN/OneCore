from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta, timezone
import json
from decimal import Decimal

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='attendant', index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creator = db.relationship('User', backref=db.backref('created_categories', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None
        }

    def __repr__(self):
        return f'<Category {self.name}>'


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.String(100), nullable=True)
    sort_order = db.Column(db.Integer, default=0, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creator = db.relationship('User', backref=db.backref('created_sizes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None
        }

    def __repr__(self):
        return f'<Size {self.name}>'


class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creator = db.relationship('User', backref=db.backref('created_expense_categories', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None
        }

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


class Product(db.Model):
    """Base product model - represents the actual item you stock (e.g., Jameson Whiskey bottles)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    base_unit = db.Column(db.String(20), nullable=False, default='bottle')  # What you actually stock
    base_buying_price = db.Column(db.Float, nullable=False)  # Cost per base unit
    current_stock = db.Column(db.Float, nullable=False, default=0, index=True)  # Stock in base units
    min_stock_level = db.Column(db.Float, nullable=False, default=5)  # Minimum base units
    last_stock_update = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_products', lazy=True))

    def get_available_stock(self):
        """Get actual available stock in base units"""
        return max(0, self.current_stock or 0)

    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.get_available_stock() <= self.min_stock_level

    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.get_available_stock() <= 0

    def get_stock_status(self):
        """Get stock status as string"""
        stock = self.get_available_stock()
        if stock <= 0:
            return "out_of_stock"
        elif stock <= self.min_stock_level:
            return "low_stock"
        else:
            return "good_stock"

    def reduce_stock(self, base_units):
        """Reduce stock by base units and return success"""
        if self.get_available_stock() >= base_units:
            self.current_stock = max(0, (self.current_stock or 0) - base_units)
            self.last_stock_update = datetime.now(timezone.utc)
            return True
        return False

    def add_stock(self, base_units):
        """Add stock in base units"""
        self.current_stock = (self.current_stock or 0) + base_units
        self.last_stock_update = datetime.now(timezone.utc)

    def get_active_variants(self):
        """Get all active product variants for this product"""
        return ProductVariant.query.filter_by(
            product_id=self.id,
            is_active=True
        ).join(Size).filter(Size.is_active == True).order_by(Size.sort_order).all()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'base_unit': self.base_unit,
            'base_buying_price': self.base_buying_price,
            'current_stock': self.current_stock,
            'available_stock': self.get_available_stock(),
            'min_stock_level': self.min_stock_level,
            'stock_status': self.get_stock_status(),
            'last_stock_update': self.last_stock_update.isoformat() if self.last_stock_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None
        }

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductVariant(db.Model):
    """Product variants - for selling tots"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=False, index=True)
    selling_price = db.Column(db.Float, nullable=False)  # Price for this variant
    conversion_factor = db.Column(db.Float, nullable=False, default=1.0)  # How many base units this represents
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    product = db.relationship('Product', backref=db.backref('variants', lazy=True))
    size = db.relationship('Size', backref=db.backref('product_variants', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_variants', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('product_id', 'size_id', name='unique_product_size'),
        db.Index('idx_variant_product_size', 'product_id', 'size_id'),
    )

    def get_display_name(self):
        """Get display name for the variant"""
        return f"{self.product.name} - {self.size.name}"

    def get_available_stock_in_variant_units(self):
        """Calculate how many of this variant are available based on base stock"""
        if self.conversion_factor <= 0:
            return 0
        return int(self.product.get_available_stock() / self.conversion_factor)

    def can_sell_quantity(self, quantity):
        """Check if we can sell the requested quantity of this variant"""
        required_base_units = quantity * self.conversion_factor
        return self.product.get_available_stock() >= required_base_units

    def get_profit_per_unit(self):
        """Calculate profit per variant unit"""
        cost_per_variant = self.product.base_buying_price * self.conversion_factor
        return self.selling_price - cost_per_variant

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'size_id': self.size_id,
            'size_name': self.size.name if self.size else None,
            'display_name': self.get_display_name(),
            'selling_price': self.selling_price,
            'conversion_factor': self.conversion_factor,
            'available_quantity': self.get_available_stock_in_variant_units(),
            'base_stock': self.product.get_available_stock() if self.product else 0,
            'profit_per_unit': self.get_profit_per_unit(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None
        }

    def __repr__(self):
        return f'<ProductVariant {self.get_display_name()}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'), nullable=False, index=True)
    expense_date = db.Column(db.Date, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    expense_category = db.relationship('ExpenseCategory', backref=db.backref('expenses', lazy=True))
    recorder = db.relationship('User', backref=db.backref('recorded_expenses', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'expense_category_id': self.expense_category_id,
            'category_name': self.expense_category.name if self.expense_category else None,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'recorder_name': self.recorder.full_name if self.recorder else None
        }

    def __repr__(self):
        return f'<Expense {self.description}>'


class DailyStock(db.Model):
    """Track daily stock movements for base products"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    opening_stock = db.Column(db.Float, default=0)  # In base units
    additions = db.Column(db.Float, default=0)  # In base units
    sales_quantity = db.Column(db.Float, default=0)  # In base units (calculated from variant sales)
    closing_stock = db.Column(db.Float, default=0)  # In base units
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('daily_stocks', lazy=True))
    updater = db.relationship('User', backref=db.backref('stock_updates', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('product_id', 'date', name='unique_product_date'),
        db.Index('idx_product_date', 'product_id', 'date'),
    )

    def calculate_closing_stock(self):
        """Calculate closing stock and update product's current stock"""
        opening = self.opening_stock if self.opening_stock is not None else 0
        additions = self.additions if self.additions is not None else 0
        sales = self.sales_quantity if self.sales_quantity is not None else 0

        self.closing_stock = max(0, opening + additions - sales)

        # Update product's current stock immediately
        if self.product:
            self.product.current_stock = self.closing_stock
            self.product.last_stock_update = datetime.now(timezone.utc)

        return self.closing_stock

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'date': self.date.isoformat() if self.date else None,
            'opening_stock': self.opening_stock,
            'additions': self.additions,
            'sales_quantity': self.sales_quantity,
            'closing_stock': self.closing_stock,
            'updated_by': self.updated_by,
            'updater_name': self.updater.full_name if self.updater else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<DailyStock {self.product.name if self.product else "Unknown"} {self.date}>'


class Sale(db.Model):
    """Sales now reference product variants instead of direct products"""
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False, index=True)
    attendant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    quantity = db.Column(db.Float, nullable=False)  # Quantity of the variant sold
    unit_price = db.Column(db.Float, nullable=False)  # Price per variant unit
    original_amount = db.Column(db.Float, nullable=False)
    discount_type = db.Column(db.String(20), default='none')
    discount_value = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    cash_amount = db.Column(db.Float, default=0)
    mpesa_amount = db.Column(db.Float, default=0)
    credit_amount = db.Column(db.Float, default=0)
    customer_name = db.Column(db.String(100), nullable=True)
    discount_reason = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sale_date = db.Column(db.Date, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), default='cash')

    variant = db.relationship('ProductVariant', backref=db.backref('sales', lazy=True))
    attendant = db.relationship('User', backref=db.backref('sales', lazy=True))

    __table_args__ = (
        db.Index('idx_sale_date_attendant', 'sale_date', 'attendant_id'),
        db.Index('idx_sale_date_variant', 'sale_date', 'variant_id'),
    )

    def calculate_discount(self):
        """Calculate discount amount based on type and value"""
        if self.discount_type == 'percentage':
            self.discount_amount = (self.original_amount * self.discount_value) / 100
        elif self.discount_type == 'fixed':
            self.discount_amount = min(self.discount_value, self.original_amount)
        else:
            self.discount_amount = 0

        self.total_amount = self.original_amount - self.discount_amount
        return self.discount_amount

    def get_base_units_sold(self):
        """Calculate how many base units this sale represents"""
        return self.quantity * self.variant.conversion_factor

    def get_profit(self):
        """Calculate profit for this sale"""
        cost_per_variant = self.variant.product.base_buying_price * self.variant.conversion_factor
        total_cost = cost_per_variant * self.quantity
        return self.total_amount - total_cost

    def to_dict(self):
        return {
            'id': self.id,
            'variant_id': self.variant_id,
            'variant_name': self.variant.get_display_name() if self.variant else None,
            'product_id': self.variant.product_id if self.variant else None,
            'product_name': self.variant.product.name if self.variant and self.variant.product else None,
            'size_name': self.variant.size.name if self.variant and self.variant.size else None,
            'attendant_id': self.attendant_id,
            'attendant_name': self.attendant.full_name if self.attendant else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'original_amount': self.original_amount,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'cash_amount': self.cash_amount,
            'mpesa_amount': self.mpesa_amount,
            'credit_amount': self.credit_amount,
            'customer_name': self.customer_name,
            'discount_reason': self.discount_reason,
            'notes': self.notes,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'payment_method': self.payment_method,
            'base_units_sold': self.get_base_units_sold(),
            'profit': self.get_profit()
        }

    def __repr__(self):
        return f'<Sale {self.variant.get_display_name() if self.variant else "Unknown"} x{self.quantity}>'


class DailySummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    total_sales = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    total_profit = db.Column(db.Float, default=0)
    total_expenses = db.Column(db.Float, default=0)
    net_profit = db.Column(db.Float, default=0)
    paybill_amount = db.Column(db.Float, default=0)
    cash_amount = db.Column(db.Float, default=0)
    credit_amount = db.Column(db.Float, default=0)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=True)

    updater = db.relationship('User', backref=db.backref('updated_summaries', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_sales': self.total_sales,
            'total_cost': self.total_cost,
            'total_profit': self.total_profit,
            'total_expenses': self.total_expenses,
            'net_profit': self.net_profit,
            'paybill_amount': self.paybill_amount,
            'cash_amount': self.cash_amount,
            'credit_amount': self.credit_amount,
            'last_updated_by': self.last_updated_by,
            'updater_name': self.updater.full_name if self.updater else None,
            'last_updated_at': self.last_updated_at.isoformat() if self.last_updated_at else None
        }

    def __repr__(self):
        return f'<DailySummary {self.date}>'


# Add this new model to your models.py file

class StockPurchase(db.Model):
    """Track stock purchases/additions with costs"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    quantity = db.Column(db.Float, nullable=False)  # Quantity in base units
    unit_cost = db.Column(db.Float, nullable=False)  # Cost per base unit
    total_cost = db.Column(db.Float, nullable=False)  # Total amount spent
    supplier_name = db.Column(db.String(100), nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    purchase_date = db.Column(db.Date, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    product = db.relationship('Product', backref=db.backref('purchases', lazy=True))
    recorder = db.relationship('User', backref=db.backref('recorded_purchases', lazy=True))

    __table_args__ = (
        db.Index('idx_purchase_date_product', 'purchase_date', 'product_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'supplier_name': self.supplier_name,
            'invoice_number': self.invoice_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'recorder_name': self.recorder.full_name if self.recorder else None
        }

    def __repr__(self):
        return f'<StockPurchase {self.product.name if self.product else "Unknown"} x{self.quantity}>'


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    table_name = db.Column(db.String(50), nullable=False, index=True)
    record_id = db.Column(db.Integer, nullable=True)
    old_values = db.Column(db.Text, nullable=True)
    new_values = db.Column(db.Text, nullable=True)
    changes_summary = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    __table_args__ = (
        db.Index('idx_audit_timestamp_user', 'timestamp', 'user_id'),
        db.Index('idx_audit_action_table', 'action', 'table_name'),
    )

    def __repr__(self):
        return f'<AuditLog {self.user.username} {self.action} {self.table_name}>'