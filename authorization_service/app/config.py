import os

import requests
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
app = Flask(__name__)
app.secret_key = "a97cb990c5f0f38f3fd86592425dbc156394e78aaf044ca79575722dbfd1b720"
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgresql://authorization_ms:X7nGR|toVM?G@authorization_ms_db/authorization_ms_db"
app.config['CORS_HEADERS'] = 'application/json'
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, support_credentials=True)

r_session = requests.Session()

# Время жизни токена в минутах
jwt_token_lifetime = int(os.environ['JWT_TOKEN_LIFETIME'])
