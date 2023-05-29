from flask import request, redirect, url_for, make_response, render_template
from flask_cors import cross_origin
from flask_jwt_extended import get_jwt_identity, jwt_required

from config import app, jwt
from db_api.db_funcs import get_all_dishes, find_order_by_id, get_all_user_orders
from misc.misc import create_new_order, make_json_response


@app.route("/api/new-order", methods=['POST'])
@cross_origin(supports_credentials=True)
@jwt_required()
def new_order():
    if not request.is_json or not (json := request.get_json(silent=True)):
        return make_json_response({"status": "failed", "error": "пустой запрос"}, 400)

    res = create_new_order(json, get_jwt_identity())
    if type(res) == str:
        return make_json_response({"status": "failed", "error": res}, 400)

    return make_json_response({"status": "OK", "order": res})


@app.route("/api/dishes", methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def dishes():
    return make_json_response({"status": "OK", "dishes": get_all_dishes()})


@app.route("/api/order", methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def get_order():
    order_id = request.args.get('id')
    if not order_id:
        return make_json_response({"status": "failed", "error": "отсутствует id заказа"}, 400)

    order = find_order_by_id(order_id)
    if not order:
        return make_json_response({"status": "failed", "error": f"заказ с id '{order_id}' не был найден"}, 400)

    if order.user_id != get_jwt_identity():
        return make_json_response(
            {"status": "failed", "error": f"заказ с id '{order_id}' принадлежит другому пользователю"}, 401)

    return make_json_response({"status": "OK", "order": order})


@app.route("/api/orders", methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def user_orders():
    orders = get_all_user_orders(get_jwt_identity())
    return make_json_response({"status": "OK", "orders": orders})


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    if request.path == "/login":
        return redirect(url_for('login'))
    if request.path == "/register":
        return redirect(url_for('register'))

    if request.path == "/create-order" or request.path.split("/")[1] == "dish":
        return make_response(
            render_template('not_logged.html', text="jwt токен устарел"), 401)

    return make_json_response({"status": "failed", "error": "jwt токен устарел"}, 401)


@jwt.unauthorized_loader
def unauthorized_token_callback(callback):
    if request.path == "/create-order" or request.path.split("/")[1] == "dish":
        return make_response(
            render_template('not_logged.html', text="Отсутствует jwt токен в печеньках или в заголовке запроса"), 401)
    return make_json_response(
        {"status": "failed", "error": "Отсутствует jwt токен в печеньках или в заголовке запроса"}, 401)
