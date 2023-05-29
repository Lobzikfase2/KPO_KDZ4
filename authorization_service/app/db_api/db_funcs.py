from sqlalchemy.exc import IntegrityError

from config import db, app
from db_api.db_models import User, Session


def get_all_users():
    with app.app_context():
        return db.session.query(User).all()


def find_user_by_id(user_id):
    return db.session.query(User).get(user_id)


def find_user_by_login(login):
    return db.session.query(User).filter(User.login.like(login)).first()


def find_user_by_email(email):
    return db.session.query(User).filter(User.email.like(email.lower().strip())).first()


def check_login_for_uniqueness(login):
    if not find_user_by_login(login):
        return True
    return False


def check_email_for_uniqueness(email):
    if not find_user_by_email(email):
        return True
    return False


def add_new_user(*args):
    try:
        user = User(*args)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return user


def add_new_session(user_id, session_token):
    try:
        session = Session(user_id, session_token)
        db.session.add(session)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return session


with app.app_context():
    db.create_all()
