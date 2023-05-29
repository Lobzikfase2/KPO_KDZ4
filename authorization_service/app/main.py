from config import app


@app.route("/")
def index():
    return "<h1 style='color: green;'>Вы находитесь на микросервисе авторизации</h1>"
