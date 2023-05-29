from flask import render_template, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import get_jwt, jwt_required

from config import app, admin, db, auth_port, order_port
from db_api.db_funcs import get_all_dishes
from db_api.db_models import Dish
from misc.misc import custom_jwt_optional, user_data

ports = dict(auth_port=auth_port, order_port=order_port)


@app.context_processor
def inject_paths():
    return dict(ports=ports)


@app.route("/")
def index():
    return "<h1 style='color: red;'>Вы находитесь на микросервисе заказов</h1>"


@app.route("/login", methods=['GET'])
@custom_jwt_optional
def login():
    if user_data.role == 'CLIENT':
        return redirect('/create-order')
    elif user_data.role == 'MANAGER':
        return redirect("/dish")

    return render_template("login-register.html", page="login")


@app.route("/register", methods=['GET'])
@custom_jwt_optional
def register():
    if user_data.role == 'CLIENT':
        return redirect('/create-order')
    elif user_data.role == 'MANAGER':
        return redirect("/dish")

    return render_template("login-register.html", page="register")


@app.route("/create-order", methods=['GET'])
@jwt_required()
def create_order():
    role = get_jwt()['role']
    if role == 'MANAGER':
        return redirect('/dish')

    return render_template("order_creation.html", dishes=get_all_dishes())


class MyModelView(ModelView):
    @expose('/')
    @jwt_required()
    def index_view(self):
        role = get_jwt()['role']
        if role == 'CLIENT':
            return redirect('/create-order')
        return super(ModelView, self).index_view()


admin.add_view(MyModelView(Dish, db.session, url="/dish"))
