import os

from flask import Flask
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

app = Flask(__name__)
app.secret_key = "a97cb990c5f0f38f3fd86592425dbc156394e78aaf044ca79575722dbfd1b720"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://order_ms:HdHy?UPpEuP3@order_ms_db/order_ms_db"
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, support_credentials=True)
admin = Admin(app, base_template='admin/menuless-layout.html', template_mode="bootstrap4")

# Порт микросервиса авторизации
auth_port = os.environ['AUTHORIZATION_MS_PORT']
# Порт микросервиса заказов
order_port = os.environ['ORDER_MS_PORT']
# Заполнять ли таблицу блюд тестовыми данными
fill_dish_table = os.environ['FILL_DISHES_TABLE_WITH_EXAMPLE_DATA'] == 'true'
# Минимальное время приготовления заказа в секундах
cooking_time_min = int(os.environ.get('MIN_ORDER_COOKING_TIME'))
# Максимальное время приготовления заказа в секундах
cooking_time_max = int(os.environ.get('MAX_ORDER_COOKING_TIME'))
