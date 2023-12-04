import os
from flask import Flask, render_template, flash, url_for, redirect, request, abort
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_bcrypt import Bcrypt
from forms import (
    RegistrationForm,
    LoginForm,
    EditAccountForm,
    UserPostForm,
    RequestResetForm,
    ResetPasswordForm,
    AdminCreateUserForm,
    AdminRemoveUserForm,
    AdminRemovePostForm
)
from data import User
from datetime import datetime
from flask_mail import Mail, Message
from smtplib import SMTP

app = Flask(__name__)

# standard practice in Flask for security
app.config["SECRET_KEY"] = "c5d8384942a409d54c42eca4512864f7"

# for mnanging authentication
User.load_users()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")
mail = Mail(app)

User.Post.load_posts()


# flask_login requires a user loader
@login_manager.user_loader
# returns the integer described by the user_id, where user_id = email
def user_loader(user_id):
    # integer indexed slicing of user dataFrame with email == user_id
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
        user_role=user_data["user_role"],
        image_file=user_data["image_file"],
        likes=user_data["likes"],
        posts=user_data["posts"],
    )

    return user


@app.route("/")
@app.route("/home")
def home():
    # need access to both to show the user and post attributes
    users = User.users
    posts = User.Post.posts
    return render_template("home.html", posts=posts, users=users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        User.createUser(form.email.data, form.username.data, form.password.data, form.user_role.data)
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
        # returns an error if incorrect username entered. oops
        user = User.users[User.users["username"] == form.username.data]
        if not user.empty:
            user = user.iloc[0]
            if form.password.data == user["password"]:
                user_instance = User(
                    email=user["email"],
                    username=user["username"],
                    password=user["password"],
                    user_role=user["user_role"],
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


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged Out", "info")
    return redirect(url_for("home"))


def send_reset_email(user):
    if request.method == "POST":
        msg = Message(
            "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
        )
        msg.body = f"""To reset your password, visit the following link:
If you did not make this request then simply ignore this email and no changes will be made.
"""
        mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.users[User.users["email"] == form.email.data].iloc[0]
        print("User data for password reset request:", user)
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Set the new password for the user using the form data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        # Update the user's password in the DataFrame
        User.update_user_password(user.email, form.password.data)

        flash("Password has been updated!", "info")
        return redirect(url_for("login"))

    return render_template("reset_token.html", title="Reset Password", form=form)


# add pitcure file to sys
# needed for editing the user profile picture
def picture_path(image_file):
    img_path = os.path.join("static/profile_pics", image_file.filename)
    image_file.save(img_path)

    return img_path


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
        form.picture.data = current_user.image_file
    else:
        # remember CSRF token for each form
        print(form.errors)

    # string value for form input
    image_file = str(current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = UserPostForm()
    if form.validate_on_submit():
        User.Post.createPost(
            title=form.title.data,
            content=form.content.data,
            username=current_user.username,
        )
        flash("Post created!", "success")
        return redirect(url_for("home"))
    return render_template(
        "new_post.html", title="New Post", legend="New Post", form=form
    )


# single post chosen/displaying individual posts in home
@app.route("/post/<post_id>")
def single_post(post_id):
    # pandas indexing error without int casting
    # urandom format requires float --> int
    post_id = int(float(post_id))
    posts = User.Post.posts
    post, user = User.Post.postUserPair(post_id)

    return render_template("single_post.html", posts=posts, user=user, post=post)


@app.route("/update_post/<post_id>", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post_id = int(float(post_id))
    post = User.Post.postUserPair(post_id)[0]

    # Only user who made the post can update it
    if post.username != current_user.username:
        abort(403)

    form = UserPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        updted_post = User.Post(
            title=form.title.data,
            content=form.content.data,
            username=current_user.username,
            keywords=form.keywords.data,
            post_id=post.post_id,
        )
        User.Post.updatePost(updted_post)
        flash("Post updated", "success")
        return redirect(url_for("single_post", post_id=post.post_id))
    #  only populate if existing data is in form
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.keywords.data = post.keywords
    return render_template(
        "new_post.html", title="Update Post", form=form, legend="Update Post"
    )


@app.route("/delete_post/<post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    post_id = int(float(post_id))
    post = User.Post.postUserPair(post_id)[0]
    # Only user who made the post can delete it
    if post.username != current_user.username:
        abort(403)

    User.Post.deletePost(post)
    flash("Post Deleted!", "success")
    print("Reached delete post route")
    return redirect(url_for("home"))


@app.route("/search", methods=["GET", "POST"])
def search():
    users = User.users
    results = None

    # Did not want to pass a form to layout (base temp) --> reauest.method
    #   to access input directly
    if request.method == "POST":
        results = User.Post.sresults(
            request.form.get("select"), request.form.get("search")
        )
        if results is not None:
            flash("Search Results", "info")
            return render_template("results.html", results=results, users=users)
        else:
            flash("No Results Found", "warning")
            return redirect(url_for("home"))

    # laoding page w/o using searchbar
    return redirect(url_for("home"))


# TODO: TypeError: missing posititional argument
@app.route("/like/<post_id>", methods=["GET"])
def like_post(post_id):
    post_id = int(float(post_id))
    User.Post.addLike(post_id)
    flash("Liked post", "success")
    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.user_role != "SU":
        abort(403)  # Restrict access to Super Users

    create_user_form = AdminCreateUserForm()
    remove_user_form = AdminRemoveUserForm()
    remove_post_form = AdminRemovePostForm()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_user' and create_user_form.validate():
            # Logic to create a new user
            User.createUser(
                email=create_user_form.email.data,
                username=create_user_form.username.data,
                password=create_user_form.password.data,
                user_role=create_user_form.role.data
            )
            flash("New user created!", "success")
            return redirect(url_for('admin'))

        elif action == 'remove_user' and remove_user_form.validate():
            # Logic to remove a user
            User.removeUser(remove_user_form.username.data)
            flash("User removed!", "success")
            return redirect(url_for('admin'))

        elif action == 'remove_post' and remove_post_form.validate():
            # Logic to remove a post
            post_id = remove_post_form.post_id.data
            User.Post.deletePost(post_id)
            flash("Post removed!", "success")
            return redirect(url_for('admin'))

    return render_template(
        "admin.html", 
        create_user_form=create_user_form, 
        remove_user_form=remove_user_form, 
        remove_post_form=remove_post_form
    )



if __name__ == "__main__":
    app.run(debug=True)

# TODO: Add sources for image file and os functions
""" Sources:
      - Flask introduction - Corey Schafer: https://youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&si=1SMoPOktWJfeVH8p
      - Request Object/Search route: https://www.geeksforgeeks.org/python-flask-request-object/ """
