from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>Hello, World!</h1>"


@app.route("/secret")
def secret():
    return "You found a secret place!"


if __name__ == "__main__":
    app.run(debug=True)
