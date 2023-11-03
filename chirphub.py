from flask import Flask, render_template, flash, url_for, redirect
from forms import RegistrationForm, LoginForm
from data import User

app = Flask(__name__)

# standard practice in Flask for security
app.config["SECRET_KEY"] = "c5d8384942a409d54c42eca4512864f7"

# Load data @ startup
User.load_users()


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/account")
def account():
    return render_template("account.html")


# passing in GET and POST methods allows us to submit data via the page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()  # instance of
    if form.validate_on_submit():
        print("Reached login")
        # login logic
        flash("Login Successful!", "info")
        return redirect(url_for("login"))

    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        User.createUser(form.email.data, form.username.data, form.password.data)
        flash("Account Created!", "info")
        return redirect(url_for("register"))

    return render_template("register.html", title="Register", form=form)

@app.route("/reset_password")
def reset_request():
    return render_template("reset_request.html")

if __name__ == "__main__":
    app.run(debug=True)

# TODO: Check validators
