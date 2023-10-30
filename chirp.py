from flask import Flask, render_template, flash, url_for, redirect
from forms import RegisterForm, LoginForm

app = Flask(__name__)

# standard practice in Flask for security
app.config['SECRET_KEY'] = 'c5d8384942a409d54c42eca4512864f7'


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
    form = LoginForm() # instance of
    if form.validate_on_submit():
        flash("Account Created!")
        return redirect(url_for("home"))
    else:
        flash("Login Unsuccessful. Check username and password")
    return render_template("login.html", title="Login", form=form)


@app.route("/register")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Account Created!")
        return redirect(url_for("login"))
    else:
        flash("Invalid email, username, or password. Try again")
    return render_template("register.html", title="Register", form=form)


if __name__ == "__main__":
    app.run(debug=True)

# TODO: Get the flashed message to show up
# TODO: Check validators