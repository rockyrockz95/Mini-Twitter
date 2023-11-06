from flask import Flask, render_template, flash, url_for, redirect
from flask_login import LoginManager, current_user, login_user, logout_user
from forms import RegistrationForm, LoginForm
from data import User

app = Flask(__name__)

# standard practice in Flask for security
app.config["SECRET_KEY"] = "c5d8384942a409d54c42eca4512864f7"

# for mnanging authentication
User.load_users()
login_manager = LoginManager(app)
login_manager.login_view = "login"


# flask_login requires a user loader
@login_manager.user_loader
# returns the integer described by the user_id, where user_id = email
def user_loader(user_id):
    # integer indexed slicing of user dataFrame with email == user_id
    user_data = User.users[User.users["email"] == user_id].iloc[0]

    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password=user_data["password"],
        image_file=user_data["image_file"],
        likes=user_data["likes"],
        posts=user_data["posts"],
    )

    return user


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # logged in user does not need to login in again
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        User.createUser(form.email.data, form.username.data, form.password.data)
        flash("Account Created!", "info")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


# passing in GET and POST methods allows us to submit data via the page
# TODO: Visual feedback for incorrectly logging in
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()  # instance of
    print("Form data - Username:", form.username.data)
    print("Form data - Password:", form.password.data)  # authetification issue test
    if form.validate_on_submit():
        # return row of matching username
        user = User.users[User.users["username"] == form.username.data].iloc[0]
        if form.password.data == user["password"]:
            user_instance = User(
                email=user["email"],
                username=user["username"],
                password=user["password"],
                image_file=user["image_file"],
                likes=user["likes"],
                posts=user["posts"],
            )
            login_user(user_instance)
            flash("Login Successful!", "info")
            return redirect(url_for("home"))

    return render_template("login.html", title="Login", form=form)


# should replace login route on bottom navbar when user logged in
@app.route("/logout")
def logout():
    logout_user()
    flash("Logged Out", "info")
    return redirect(url_for("home"))


@app.route("/reset_password")
def reset_request():
    return render_template("reset_request.html")


@app.route("/account")
def account():
    return render_template("account.html")


if __name__ == "__main__":
    app.run(debug=True)

# TODO: Check validators
