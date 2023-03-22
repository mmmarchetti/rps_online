from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    """
    Form for user registration.
    """
    username: StringField = StringField('Username', validators=[DataRequired(message="A username is required"),
                                                                Length(min=2, max=20)])
    email: StringField = StringField('Email', validators=[DataRequired(message="A proper email is required"),
                                                          Email()])
    password: PasswordField = PasswordField('Password', validators=[DataRequired(message="A password is required")])
    confirm_password: PasswordField = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit: SubmitField = SubmitField('Sign up')


class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    email: StringField = StringField('Email', validators=[DataRequired(message="A proper email is required"),
                                                          Email()])
    password: PasswordField = PasswordField('Password', validators=[DataRequired(message="A password is required")])
    remember: BooleanField = BooleanField('Remember me')
    submit: SubmitField = SubmitField('Login')


class JoinRoom(FlaskForm):
    """
    Form for user to join a room.
    """
    roomID: StringField = StringField('RoomID', validators=[DataRequired(message="A room id is required")])
    submit: SubmitField = SubmitField('Join Room')


class EditUserForm(FlaskForm):
    """
    Form for user to edit their username.
    """
    newUsername: StringField = StringField('New Username', validators=[DataRequired(message="A username is required"),
                                                                       Length(min=2, max=20)])
    submit: SubmitField = SubmitField('Edit Username')

