from flask import request, session, redirect, url_for, flash
from src.create_user import create_user, check_email_and_username_availability
from typing import Dict, Union, Optional
from werkzeug import Response
from src.database import users
import bcrypt


class User:

    def __init__(self):
        self.session = session

    def _start_session(self, user: Dict[str, str]) -> redirect:
        """
        Start a new session for the given user.

        Args:
            user (dict): A dictionary containing user information, including the user's ID and username.

        Returns:
            flask.redirect: A redirect to the user's profile page.
        """
        self.session['logged_in'] = True
        self.session['userid'] = user["_id"]
        self.session["username"] = user["username"]

        return redirect('/lobby/')

    @staticmethod
    def _check_valid_username(username: str) -> Union[None, redirect]:
        """
        Check if a username is valid, and if not, flash an error message and redirect to the signup page.

        Args:
            username: A string containing the username to be checked.

        Returns:
            None if the username is valid, or a redirect to the signup page if the username is invalid.
        """
        if '/' in username:
            flash("Usernames cannot contain '/'!")
            return redirect(url_for('signup_page'))
        return None

    @staticmethod
    def check_password() -> redirect:
        """
        Check if password and confirm_password fields match.

        Returns:
            flask.redirect: A redirect to the signup page if passwords do not match.
        """
        if request.form.get('password') != request.form.get('confirm_password'):
            flash("Passwords do not match")
            return redirect(url_for('signup_page'))

    def signup(self) -> Response:
        """
        Sign up a new user by adding their information to the database.

        Returns:
            Union[flash, redirect]: A flash message if the sign-up is unsuccessful,
            or a redirect to the login page if the sign-up is successful.
        """

        username = request.form.get('username')
        self._check_valid_username(username)

        user = create_user(username=request.form.get('username'),
                           email=request.form.get('email'),
                           password=request.form.get('password'),
                           bcrypt=bcrypt)

        available_email, available_name = check_email_and_username_availability(user=user, users=users)

        if not available_name or not available_email:
            return redirect(url_for('signup_page'))

        self.check_password()

        users.insert_one(user)

        return redirect(url_for('login_page'))

    def signout(self) -> redirect:
        """
        Clears the user's session and redirects to the homepage.

        Returns:
            flask.redirect: A redirect to the homepage.
        """
        self.session.clear()
        flash("Successfully signed out!")
        return redirect('/')

    def login(self) -> Optional[redirect]:
        """
        Log in the user with the email and password from the request form.

        Returns:
            Optional[flask.redirect]: A redirect to the user's profile page if login successful,
            otherwise a redirect to the home page.
        """

        if len(list(users.find({}))) > 0:
            user_found: dict = users.find_one({"email": request.form.get('email')})

            if user_found and bcrypt.hashpw(request.form.get('password').encode(),
                                            user_found['salt']) == user_found['password']:

                return self._start_session(user_found)

        flash("Can't login due to wrong password or invalid email.")

        return redirect('/')
