from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return "<h1>Login Info Here</h1>"


@app.route("/register")
def register():
    return "<h1>Sign Up Here<h1>"


@app.route("/account")
def account():
    return "<h1>Include Account Setting<h1>"


if __name__ == "__main__":
    app.run(debug=True)
