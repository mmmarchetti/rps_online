from flask import request, session, redirect, url_for, flash
from typing import Dict, Union, Optional
from werkzeug import Response
from database import users
import bcrypt
import uuid


class User:

    def __init__(self):
        self.session = session

    def start_session(self, user: Dict[str, str]) -> redirect:
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

        return redirect(f'/profile/{user["username"]}')

    @staticmethod
    def search_db_available(db_search_type: str, user_search_type: str) -> bool:
        """
            Check if a given user search type value is available in the database for the given search type.

            Args:
                db_search_type (str): The search type to use for the database query.
                user_search_type (str): The value to search for in the database for the given search type.

            Returns:
                bool: True if the user search type value is not found in the database for the given search type,
                False otherwise.
            """

        return users.find_one({db_search_type: user_search_type}) is None

    @staticmethod
    def is_available(type_check_available: bool, type_of_check: str) -> Union[None, redirect]:
        """
        Check if the given type is available. If it's not, a flash message is added, and the user is redirected to the
        signup page.

        Args:
            type_check_available (bool): A boolean that indicates whether the given type is available or not.
            type_of_check (str): A string indicating the type being checked.

        Returns:
            Union[None, redirect]: None if the type is available, else a redirect to the signup page.
        """
        if not type_check_available:
            flash(f"{type_of_check} already in use")
            return redirect(url_for('signup_page'))

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

        salt = bcrypt.gensalt()

        # Usernames that contain '/' causes a bug, need to add a check for that
        # Check if the username is valid
        username = request.form.get('username')
        if '/' in username:
            flash("Usernames cannot contain '/' !")
            return redirect(url_for('signup_page'))

        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "username": request.form.get('username'),
            "email": request.form.get('email'),
            "salt": salt,
            "password": bcrypt.hashpw(request.form.get('password').encode(), salt),
            "wins": 0,
            "played": 0
        }

        if len(list(users.find({}))) > 0:
            # Check if Name and/or Email exists
            is_available_email = self.search_db_available("email", user['email'])
            self.is_available(is_available_email, "Email")

            is_available_name = self.search_db_available("username", user['username'])
            self.is_available(is_available_name, "Name")

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

                return self.start_session(user_found)

        flash("Can't login due to wrong password or invalid email.")

        return redirect('/')
