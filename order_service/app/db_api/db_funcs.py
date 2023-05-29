from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import true

from config import db, app, fill_dish_table
from db_api.db_models import Dish, Order, OrderDish


def find_dish_by_id(dish_id):
    return db.session.query(Dish).get(dish_id)


def add_new_order(user_id, status, special_requests=None):
    try:
        order = Order(user_id, status, special_requests)
        db.session.add(order)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return order


def find_order_by_id(order_id):
    return db.session.query(Order).get(order_id)


def get_all_user_orders(user_id):
    return db.session.query(Order).filter(Order.user_id == user_id).order_by(Order.id).all()


def add_new_dish(name, price, quantity, description=None, is_available=True):
    with app.app_context():
        try:
            dish = Dish(name, price, quantity, description, is_available)
            db.session.add(dish)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return dish


def add_new_order_dish(order_id, dish_id, quantity, price):
    try:
        order_dish = OrderDish(order_id, dish_id, quantity, price)
        db.session.add(order_dish)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return order_dish


def update_dish_quantity(dish_id, quantity):
    if quantity < 0:
        quantity = 0
    dish = find_dish_by_id(dish_id)
    if dish:
        dish.quantity = quantity
    db.session.add(dish)
    db.session.commit()


def get_all_dishes():
    return db.session.query(Dish).filter(Dish.quantity > 0).filter(Dish.is_available == true()).order_by(
        Dish.name).all()


def get_waiting_order():
    return db.session.query(Order).filter(or_(Order.status == "created", Order.status == "cooking")).order_by(
        Order.id).first()


def update_order_status(order_id, status):
    order = find_order_by_id(order_id)
    if order:
        order.status = status
        db.session.add(order)
        db.session.commit()


with app.app_context():
    db.create_all()

if fill_dish_table:
    add_new_dish("Котлетки", 120, 7, "С макарошками")
    add_new_dish("Зло-Кола", 2300, 4, "Напиток (0.01мл)")
    add_new_dish("Картофель", 111.1111111, 11, "В мундире (11 клубней)")
    add_new_dish("Бургер", 59.90, 8, "Просто бургер")
    add_new_dish("Борщ", 95.5, 1, "С капустой, но не красный")
    add_new_dish("Котлеты", 130, 7, "С пюрешкой")
    add_new_dish("Бокал", 250, 43, "Пустой")
    add_new_dish("Батон", 50, 11, "Хлебный")
    add_new_dish("Чизбургер", 59.90, 6, "Просто бургер, но с сыром")
    add_new_dish("Щи", 80.35, 5, "Кислые")
