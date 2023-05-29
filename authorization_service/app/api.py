from flask import request, redirect, url_for
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, unset_access_cookies

from config import app, jwt
from db_api.db_funcs import add_new_user, find_user_by_id
from misc.misc import validate_login_data, validate_register_data, make_json_response, issue_user_token, \
    custom_jwt_optional, user_data


@app.route("/api/register", methods=['POST'])
@cross_origin(supports_credentials=True)
@custom_jwt_optional
def register():
    if user_data.id:
        return make_json_response({"status": "failed", "error": "вы уже вошли в аккаунт"}, 400)

    if not request.is_json or not (json := request.get_json(silent=True)):
        return make_json_response({"status": "failed", "error": "пустой запрос"}, 400)

    res = validate_register_data(json)
    if type(res) == str:
        return make_json_response({"status": "failed", "error": res}, 400)

    if not (user := add_new_user(*res)):
        return make_json_response({"status": "failed", "error": "ошибка добавления в базу данных"}, 400)

    token = issue_user_token(user)

    response = make_json_response({"status": "OK", "user": user})
    set_access_cookies(response, token)
    return response


@app.route("/api/login", methods=['POST'])
@cross_origin(supports_credentials=True)
@custom_jwt_optional
def login():
    if user_data.id:
        return make_json_response({"status": "failed", "error": "вы уже вошли в аккаунт"}, 400)

    if not request.is_json or not (json := request.get_json(silent=True)):
        return make_json_response({"status": "failed", "error": "пустой запрос"}, 400)

    res = validate_login_data(json)
    if type(res) == str:
        return make_json_response({"status": "failed", "error": res}, 400)

    token = issue_user_token(res)

    response = make_json_response({"status": "OK", "user": res})
    set_access_cookies(response, token)
    return response


@app.route("/api/logout", methods=['GET'])
@cross_origin(supports_credentials=True)
@custom_jwt_optional
def logout():
    if not user_data.token_expired and not user_data.id:
        return make_json_response(
            {"status": "failed", "error": "Отсутствует jwt токен в печеньках или в заголовке запроса"}, 401)

    response = make_json_response({"status": "OK"})
    unset_access_cookies(response)
    return response


@app.route("/api/user", methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required(locations=["cookies", "headers"])
def current_user():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    if not user:
        return make_json_response({"status": "failed", "error": f"пользователь с id '{user_id}' не был найден"}, 400)

    return make_json_response({"status": "OK", "user": user})


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    if request.path == "/api/login":
        return redirect(url_for('login'))
    if request.path == "/api/logout":
        return redirect(url_for('logout'))
    if request.path == "/api/register":
        return redirect(url_for('register'))

    return make_json_response({"status": "failed", "error": "jwt токен устарел"}, 401)


@jwt.unauthorized_loader
def unauthorized_token_callback(callback):
    return make_json_response(
        {"status": "failed", "error": "Отсутствует jwt токен в печеньках или в заголовке запроса"}, 401)
