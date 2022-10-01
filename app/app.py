from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/secret")
def secret():
    return "You found a secret place!"


if __name__ == "__main__":
    app.run(debug=True)
