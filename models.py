import bcrypt
from flask import request, session, redirect, url_for, flash
from database import users
import uuid


class User:

    def start_session(self, user):
        session['logged_in'] = True
        session['userid'] = user["_id"]
        session["username"] = user["username"]
        return redirect('/profile/'+user["username"])

    def signup(self):
        salt = bcrypt.gensalt()

        # Usernames that contain '/' causes a bug, need to add a check for that
        is_valid_username = '/' not in request.form.get('username')
        if not is_valid_username:
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
            is_available_email = users.find_one({"email": user['email']}) is None
            is_available_name = users.find_one({"username": user['username']}) is None

            # Check for existing email address
            if not is_available_email:
                flash("Email address already in use")
                return redirect(url_for('signup_page'))

            if not is_available_name:
                flash("Username already in use")
                return redirect(url_for('signup_page'))

        if request.form.get('password') != request.form.get('confirm_password'):
            flash("password are not matched")
            return redirect(url_for('signup_page'))

        users.insert_one(user)
        print(list(users.find()))
        return redirect(url_for('login_page'))

    def signout(self):
        session.clear()
        flash("Sucessfully signed out!")
        return redirect('/')

    def login(self):

        if len(list(users.find({}))) > 0:
            user_found: dict = users.find_one({"email": request.form.get('email')})

            if user_found and bcrypt.hashpw(request.form.get('password').encode(),
                                            user_found['salt']) == user_found['password']:
                return self.start_session(user_found)

        flash("Can't login due to wrong password or invalid email.")
        return redirect('/')
