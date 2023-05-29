from datetime import datetime

from sqlalchemy import func, ForeignKey

from config import db

db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))


class Dish(db.Model):
    __tablename__ = 'Dishes'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False, decimal_return_scale=None), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, name, price, quantity, description=None, is_available=True):
        self.name = name
        self.price = float("{:.2f}".format(price))
        self.quantity = quantity
        self.description = description
        self.is_available = is_available

    def serialize(self):
        return {"id": self.id, "name": self.name, "description": self.description,
                "price": float(self.price), "quantity": self.quantity}


class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    special_requests = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    order_dishes = db.relationship("OrderDish")

    def __init__(self, user_id, status, special_requests=None):
        self.user_id = user_id
        self.status = status
        self.special_requests = special_requests

    def serialize(self):
        return {"id": self.id, "status": self.status,
                "special_requests": self.special_requests,
                "order_dishes": [order_dish.serialize() for order_dish in self.order_dishes],
                "created_at": datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")}


class OrderDish(db.Model):
    __tablename__ = 'Orders_dishes'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(db.Integer, ForeignKey("Orders.id"), nullable=False)
    dish_id = db.Column(db.Integer, ForeignKey("Dishes.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False, decimal_return_scale=None),
                            nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, order_id, dish_id, quantity, total_price):
        self.order_id = order_id
        self.dish_id = dish_id
        self.quantity = quantity
        self.total_price = float("{:.2f}".format(total_price))

    def serialize(self):
        from db_api.db_funcs import find_dish_by_id
        dish: Dish = find_dish_by_id(self.dish_id)
        return {"id": self.id, "dish_id": self.dish_id, "quantity": self.quantity,
                "total_price": float(self.total_price), "name": dish.name, "description": dish.description,
                "created_at": datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.strftime(self.updated_at, "%Y-%m-%d %H:%M:%S")}
