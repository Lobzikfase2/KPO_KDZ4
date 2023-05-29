import json as json_lib
from functools import wraps

from flask import Response
from flask_jwt_extended import verify_jwt_in_request
from jwt import ExpiredSignatureError
from loguru import logger

from db_api.db_funcs import find_dish_by_id, add_new_order, add_new_order_dish, update_dish_quantity, find_order_by_id


def make_json_response(data: dict, status: int = 200):
    if not data:
        raise TypeError('No data')
    if not isinstance(data, dict):
        raise TypeError('Data is not a dict')
    for key, value in data.items():
        try:
            if type(value) == str:
                raise TypeError
            _ = (_ for _ in value)
        except TypeError:
            # Объект не итерируемый
            try:
                value = value.serialize()
                data[key] = value
                continue
            except AttributeError:
                # Объект не содержит метода serialize()
                try:
                    json_lib.dumps(value)
                    continue
                except TypeError:
                    logger.debug(value)
                    raise TypeError('Data is not JSON serializable')
        else:
            lst = []
            for item in value:
                try:
                    lst.append(item.serialize())
                    continue
                except AttributeError:
                    try:
                        json_lib.dumps(item)
                        lst.append(item)
                        continue
                    except TypeError:
                        logger.debug(item)
                        raise TypeError('Data is not JSON serializable')
            data[key] = lst

    response = Response(
        response=json_lib.dumps(data, ensure_ascii=False).encode('utf8'),
        status=status,
        mimetype='application/json'
    )
    return response


def validate_ordered_dishes(ordered_dishes: list):
    lst = []
    for ordered_dish in ordered_dishes:
        if 'id' not in ordered_dish or not (dish_id := ordered_dish['id']):
            return "incorrect data"
        if 'quantity' not in ordered_dish or not (quantity := ordered_dish['quantity']):
            return "incorrect data"
        if 'total_price' not in ordered_dish or not (total_price := ordered_dish['total_price']):
            return "incorrect data"
        try:
            dish_id = int(dish_id)
            quantity = int(quantity)
            total_price = float(total_price)
        except ValueError:
            return "incorrect data"

        dish = find_dish_by_id(dish_id)
        if dish and dish.is_available and dish.quantity > 0:
            if quantity > dish.quantity:
                quantity = dish.quantity
            lst.append((dish_id, quantity, total_price))
            update_dish_quantity(dish_id, dish.quantity - quantity)

    if len(lst) == 0:
        return "заказ должен состоять, как минимум из одного блюда"
    return lst


def create_new_order(json: dict, user_id):
    if 'dishes' not in json or (not (dishes := (json['dishes'])) or not isinstance(dishes, list)):
        return "заказ должен состоять, как минимум из одного блюда"

    res = validate_ordered_dishes(dishes)
    if type(res) == str:
        return res

    special_requests = None
    if 'special_requests' in json:
        special_requests = json['special_requests']
    order = add_new_order(user_id, "created", special_requests)

    for dish_data in res:
        add_new_order_dish(order.id, *dish_data)

    return find_order_by_id(order.id)


class UserData:
    def __init__(self):
        self.id = None
        self.role = None
        self.token_expired = None

    def clear(self):
        self.id = None
        self.role = None
        self.token_expired = None


user_data = UserData()


def custom_jwt_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            user_data.clear()
            data = verify_jwt_in_request(optional=True)
            if data and len(data) == 2:
                user_data.id = data[1]['sub']
                user_data.role = data[1]['role']
            user_data.token_expired = False
        except ExpiredSignatureError:
            user_data.token_expired = True
        return fn(*args, **kwargs)

    return wrapper
