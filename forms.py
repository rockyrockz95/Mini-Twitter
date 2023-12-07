import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    Optional,
    ValidationError,
)
from collections import Counter
from data import User

# creating each form as a class, possible using wtforms package


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=15)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    user_role = SelectField(
        "Account Type",
        choices=[("OU", "Ordinary User"), ("CU", "Corporate User")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user_data = User.users[User.users["username"] == username.data]
        if not user_data.empty:
            raise ValidationError(
                "Username already exists. Please choose another or log in"
            )

    def validate_email(self, email):
        user_data = User.users[User.users["email"] == email.data]
        if not user_data.empty:
            raise ValidationError(
                "There is an account with that email. Please choose another or log in."
            )


class EditAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=15)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    # fileAllowed is a validator where we can enter file types as strings to restrict picture format
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Edit Account")

    def validate_username(self, username):
        user_data = User.users[User.users["username"] == username.data]
        if username.data != current_user.username:
            if not user_data.empty:
                raise ValidationError(
                    "Username already exists. Please choose another or log in"
                )

    def validate_email(self, email):
        user_data = User.users[User.users["email"] == email.data]
        if email.data != current_user.email:
            if not user_data.empty:
                raise ValidationError(
                    "There is an account with that email. Please choose another or log in."
                )


class UserPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    type = SelectField(
        "Post Type",
        choices=[
            ("", "Select post type"),
            ("ad", "Advertisement"),
            ("job", "Job Posting"),
            ("standard", "Standard Post"),
        ],
        validators=[DataRequired()],
    )
    # multi-line input
    content = TextAreaField("Content", validators=[
                            DataRequired(), Length(max=280)])
    media = FileField(
        "Add Picture", validators=[FileAllowed(["jpg", "png", "gif", "mp4"])]
    )
    keywords = StringField("Key Words", validators=[Optional()])
    submit = SubmitField("Post")

    def validate_keywords(self, keywords):
        # count of words including contractions
        count = Counter(re.findall(r"[\w']+", keywords.data.lower())).total()
        print("Word Count: ", count)
        if count > 3:
            raise ValidationError("Only up to 3 keywords allowed")

    def validate_type(self, type):
        if current_user.user_role != "CU" and type.data != "standard":
            raise ValidationError(
                "Invalid type for role. Please choose standard or apply to be a Corporate User"
            )


class PostComplaintForm(FlaskForm):
    content = TextAreaField("Complaint Content", validators=[DataRequired()])
    submit = SubmitField("Submit Complaint")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user_data = User.users[User.users["email"] == email.data]
        if user_data.empty:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class AdminCreateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[
            ('', 'Select a role'),
            ('SU', 'Super User'),
            ('TU', 'Trendy User'),
            ('OU', 'Ordinary User'),
            ('CU', 'Corporate User')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Create User')


class AdminRemoveUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Remove User')


class AdminRemovePostForm(FlaskForm):
    post_id = StringField('Post ID', validators=[DataRequired()])
    submit = SubmitField('Remove Post')


class AdminTabooWordForm(FlaskForm):
    word = StringField('Word', validators=[DataRequired(), Length(min=1, max=50)])
    submit_add = SubmitField('Add Word')
    submit_remove = SubmitField('Remove Word')


# Sources:
#   validators: https://wtforms.readthedocs.io/en/2.3.x/validators/#:~:text=Validates%20that%20input%20was%20provided%20for%20this%20field.,required%20flag%20on%20fields%20it%20is%20used%20on.
