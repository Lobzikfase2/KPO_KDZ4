from config import app


@app.template_filter(name="smart_round")
def smart_round(num) -> str:
    return "{:.2f}".format(num)
