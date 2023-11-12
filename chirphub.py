import os
from flask import Flask, render_template, flash, url_for, redirect, request
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from forms import RegistrationForm, LoginForm, EditAccountForm
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
    user_data_email = User.users[User.users["email"] == user_id]
    # assume that both will not be changed/empty at the same time
    # TODO: changing username logs out the user, MUST FIX
    # TODO: find way to make this more concise
    # TODO: username and email can't be changed at the same time, leave as is or fix?

    # if the email is being changed, identify user by their username
    if not user_data_email.empty:
        # index slicing, return first row of dataFrame with matching email to user_id
        user_data = user_data_email.iloc[0]
    else:
        user_data_username = User.users[User.users["username"] == user_id]
        # can't find username || email --> user not in database
        if user_data_username.empty:
            print(user_id, "is not associated with any user")
            return None

        user_data = user_data_username.iloc[0]

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
    if form.validate_on_submit():
        # return row of matching username
        # returns an error if incorrect username entered. oops
        user = User.users[User.users["username"] == form.username.data]
        if not user.empty:
            user = user.iloc[0]
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
            else:
                flash("Invalid username or password", "warning")
                return redirect(url_for("login"))
        else:
            flash("Invalid username or password", "warning")
            return redirect(url_for("login"))

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


# add pitcure file to sys
# needed for editing the user profile picture
def picture_path(image_file):
    img_path = os.path.join("static/profile_pics", image_file.filename)
    image_file.save(img_path)

    return img_path


# TODO: default photo does not show unless explicitly chosen
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = EditAccountForm()
    if form.validate_on_submit():
        # add new photo if uploaded via form
        if form.picture.data:
            image_file = picture_path(form.picture.data)
            current_user.image_file = image_file

        # update database based on form data
        current_user.username = form.username.data
        current_user.email = form.email.data
        User.updateUser(current_user)

        flash("Your account has been updated", "info")
        return redirect(url_for("account"))

    # shows the current_user values on page
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        # remember CSRF token for each form
        print(form.errors)

    # string value for form input
    image_file = str(current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


if __name__ == "__main__":
    app.run(debug=True)

# TODO: Add sources for image file and os functions
