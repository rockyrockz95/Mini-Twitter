from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    ValidationError,
)
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo
from data import User
from flask_login import current_user


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
    submit = SubmitField("Sign Up")

    # Check for username/email already taken
    def validate_email(self, email):
        # return all rows that fit the search
        user = User.users[User.users["email"] == email.data]
        if not user.empty:
            # custom validation error
            raise ValidationError(
                "Email already used. Please choose another or login to existing account"
            )

    def validate_username(self, username):
        user = User.users[User.users["username"] == username.data]
        if not user.empty:
            raise ValidationError("Username taken. Please choose another")


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

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.users[User.users["email"] == email.data]
            if not user.empty:
                raise ValidationError(
                    "Email already used. Please choose another or login to existing account"
                )

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.users[User.users["username"] == username.data]
            if not user.empty:
                raise ValidationError("Username taken. Please choose another")


""" both forms not not fully implemented yet in reset_request.html
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
"""
# Sources:
#   validators: https://wtforms.readthedocs.io/en/2.3.x/validators/#:~:text=Validates%20that%20input%20was%20provided%20for%20this%20field.,required%20flag%20on%20fields%20it%20is%20used%20on.