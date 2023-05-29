import json as json_lib
from functools import wraps

import bcrypt
from flask import Response
from flask_jwt_extended import verify_jwt_in_request
from jwt import ExpiredSignatureError


def validate_email(email: str) -> bool:
    email = email.strip()
    ending = email[email.find('@') + 1:]
    if '@' not in email or len(email[:email.find('@')]) <= 3 \
            or len(ending) <= 3 or '.' not in ending \
            or len(ending[:ending.find('.')]) <= 1 \
            or len(ending[ending.find('.'):]) <= 1:
        return False
    return True


def validate_pass_without_len(psw: str) -> bool:
    psw = psw.strip()
    has_digit = False
    has_uppercase = False
    has_lowercase = False
    for char in psw:
        if char.isupper():
            has_uppercase = True
        if char.islower():
            has_lowercase = True
        if char.isdigit():
            has_digit = True
    if has_digit and has_uppercase and has_lowercase:
        return True
    return False


def validate_register_data(json: dict):
    from db_api.db_funcs import check_login_for_uniqueness, check_email_for_uniqueness
    from db_api.db_models import UserRole
    if 'login' not in json or ((login := str(json['login']).strip()) == ''):
        return "отсутствует имя пользователя"
    if 'first_name' not in json or ((first_name := str(json['first_name']).strip()) == ''):
        return "отсутствует имя"
    if 'last_name' not in json or ((last_name := str(json['last_name']).strip()) == ''):
        return "отсутствует фамилия"
    if 'email' not in json or ((email := str(json['email']).lower().strip()) == ''):
        return "отсутствует email"
    if 'password' not in json or ((password := str(json['password']).strip()) == ''):
        return "отсутствует пароль"
    if 'password_repeat' not in json or ((password_repeat := str(json['password_repeat']).strip()) == ''):
        return "отсутствует повторно введенный пароль"
    if 'role' not in json or ((role := str(json['role']).upper().strip()) == ''):
        return "отсутствует роль пользователя"

    if not check_login_for_uniqueness(login):
        return "пользователь с таким именем пользователя уже существует"
    if len(login) < 3:
        return "ваше имя пользователя должно содержать не менее 3 символов"
    if len(login) > 24:
        return "ваше имя пользователя должно содержать не более 24 символов"

    if not validate_email(email):
        return "указанный вами адрес электронной почты неверен"
    if not check_email_for_uniqueness(email):
        return "указанный вами адрес электронной почты уже привязан к чужой учетной записи"

    if len(password) < 8:
        return "ваш пароль должен содержать не менее 8 символов"
    if len(password) >= 30:
        return "ваш пароль должен содержать не более 30 символов"
    if not validate_pass_without_len(password):
        return "ваш пароль должен содержать по крайней мере одну строчную букву, одну заглавную букву и одну цифру"
    if password != password_repeat:
        return "введенные вами пароли не совпадают"

    try:
        role = UserRole[role]
    except KeyError:
        return "недопустимая роль пользователя"

    return login, first_name, last_name, email, password, role


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=15))


def compare_passwords(checking_password, hashed_password):
    return bcrypt.checkpw(checking_password.encode('utf-8'), hashed_password)


def validate_login_data(json: dict):
    from db_api.db_funcs import find_user_by_login, find_user_by_email
    if 'login_or_email' not in json or ((login_or_email := str(json['login_or_email']).strip()) == ''):
        return "отсутствует имя пользователя/email"
    if 'password' not in json or ((password := str(json['password']).strip()) == ''):
        return "отсутствует пароль"

    if not (user := find_user_by_login(login_or_email)) and not (user := find_user_by_email(login_or_email)):
        return "пользователя с таким именем пользователя/email не существует"

    if not user.check_password(password):
        return "неверный пароль"

    return user


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
                        raise TypeError('Data is not JSON serializable')
            data[key] = lst

    response = Response(
        response=json_lib.dumps(data, ensure_ascii=False).encode('utf8'),
        status=status,
        mimetype='application/json'
    )
    return response


def issue_user_token(user):
    from db_api.db_funcs import add_new_session
    token = user.get_token()
    add_new_session(user.id, token)
    return token


class UserData:
    def __init__(self):
        self.id = None
        self.role = None
        self.token_expired = None

    def clear(self):
        self.id = None
        self.role = None
        self.token_expired = None

    def __str__(self):
        return f"id: {self.id}, role: {self.role}, token_expired: {self.token_expired}"


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
