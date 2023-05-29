import enum
from datetime import timedelta, datetime

from flask_jwt_extended import create_access_token
from sqlalchemy import ForeignKey

from config import db, jwt_token_lifetime, r_session
from misc.misc import hash_password, compare_passwords


class UserRole(enum.Enum):
    CLIENT = 0,
    MANAGER = 1


class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)

    def __init__(self, login, first_name, last_name, email, password, user_role):
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = hash_password(password).decode('utf-8')
        self.role = user_role

    def check_password(self, password):
        return compare_passwords(password, self.password.encode('utf-8'))

    # время в часах
    def get_token(self):
        return create_access_token(identity=self.id, expires_delta=timedelta(minutes=jwt_token_lifetime),
                                   additional_claims={"role": str(self.role).split('.')[1]})

    def serialize(self):
        session = db.session.query(Session).filter(Session.user_id == self.id).order_by(Session.id.desc()).first()
        r = r_session.get('http://order_ms:5000/api/orders', cookies={"access_token_cookie": session.session_token})
        orders = r.json()['orders']

        return {"id": self.id, "login": self.login, "first_name": self.first_name, "last_name": self.last_name,
                "email": self.email, "password": self.password, "role": str(self.role).split('.')[1],
                "jwt_token": str(session.session_token),
                "token_expiration_time": datetime.strftime(session.expires_at, "%Y-%m-%d %H:%M:%S"),
                'orders': orders}


class Session(db.Model):
    __tablename__ = 'Sessions'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("Users.id"), nullable=False)
    session_token = db.Column(db.String, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, user_id, session_token):
        self.user_id = user_id
        self.session_token = session_token
        self.expires_at = datetime.now() + timedelta(minutes=jwt_token_lifetime)
