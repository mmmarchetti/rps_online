from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash, Response
from src.player import is_valid_username, is_available_username, handle_player_choice
from src.forms import RegistrationForm, LoginForm, JoinRoom, EditUserForm
from flask_socketio import SocketIO, join_room, leave_room
from typing import Union, Tuple, Dict
from dotenv import load_dotenv
from src.database import users
from src.models import User
import random
import string
import html
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Access environment variables using os.environ
app.secret_key = os.environ.get("SECRET_KEY")

# Start SocketIo
socketio = SocketIO(app, cors_allowed_origins='*')

# Socket global variables
players = {}


def generate_room_code(string_length: int) -> str:
    """
    Generate a random string of uppercase letters with the given length.

    Args:
        string_length (int): The length of the random string to generate.

    Returns:
        str: A random string of uppercase letters.
    """
    return ''.join(random.choices(string.ascii_uppercase, k=string_length))


@app.route('/', methods=["POST", "GET"])
def login_page() -> Union[redirect, str]:
    """
    Display the login page.

    If the user is already logged in, redirect to the lobby page.
    Otherwise, display the login form and handle form submission.

    Returns:
        Either a redirect to the lobby page if the user is already logged in, or
        the rendered login template with the login form.
    """
    if "username" in session:
        return redirect(url_for("lobby_page"))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        return User().login()

    return render_template('login.html', form=login_form)


@app.route('/signup/', methods=["POST", "GET"])
def signup_page() -> Union[redirect, str]:
    """
    Render the registration page and handle form submissions.

    Returns:
        Union[flask.redirect, str]: If the form is successfully validated, redirect to the signup success page.
            Otherwise, render the registration page with the registration form.
    """
    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        return User().signup()

    return render_template('register.html', form=registration_form)


@app.route("/lobby/", methods=["GET"])
def lobby_page() -> Union[str, redirect]:
    """
    Renders the lobby page with a JoinRoom form and the user's username if they are logged in,
    or redirects to the login page.

    Returns:
        Union[str, redirect]: The rendered lobby page with the JoinRoom form and the user's username,
        or a redirect to the login page.
    """

    if "username" in session:
        join_room_form = JoinRoom()
        username = html.escape(session["username"])

        return render_template('lobby.html', form=join_room_form, username=username)

    else:
        return redirect(url_for("login_page"))


@app.route("/about/")
def about_page() -> str:
    """
    Renders the about page.

    Returns:
        str: Rendered HTML template of the about page.
    """
    return render_template('about.html')


@app.route("/profile/signout")
def signout_page() -> None:
    """
    Signs out the current user by clearing the session.

    Returns:
        None
    """
    return User().signout()


@app.route("/profile/")
def profile_check() -> Union[jsonify, redirect]:
    """
    Check if user is logged in and redirect to user's profile page.

    Returns:
        flask.jsonify or flask.redirect: A JSON response if the user is not logged in,
        a redirect to the user's profile page otherwise.
    """
    if session.get("username") is None:
        return jsonify({"failed": "Login first to view profiles."}), 401

    return redirect(f'/profile/{session.get("username")}')


@app.route('/profile/<string:username>', methods=['GET'])
def profile_page(username: str) -> Union[str, Tuple[Response, int]]:
    """
       Get the profile page for a given user.

       Args:
           username (str): The username of the user to get the profile page for.

       Returns:
           Union[str, Tuple[Response, int]]: If user is found, render profile.html with user information, rank and form.
           If user is not found, return a JSON error message and 401 status code.
       """

    user = users.find_one({"username": username})
    if not user:
        return jsonify({"failed": "User can not be found"}), 401

    user_board = list(users.find().sort("wins", -1))
    user_rank = user_board.index(user) + 1

    edit_username_form = EditUserForm()
    return render_template('profile.html', form=edit_username_form, user=user, username=session.get('username', ''),
                           rank=user_rank)


@app.route('/profile/<string:username>', methods=['POST'])
def edit_username(username: str) -> Union[Tuple[jsonify, int], redirect]:
    """
    Edit the username of the currently logged-in user.

    Args:
        username (str): The current username of the user.

    Returns:
        Union[Tuple[jsonify, int], redirect]: Returns a redirect to the new user profile page or a failed JSON
        response with a 401 status code.
    """
    # Check if the user is logged in with the given username
    if session.get("username") != username:
        return jsonify({"failed": "Please login to change this account's username."}), 401

    # Get the new username from the request form data
    new_username = request.form.get('newUsername')

    # Check if the new username is valid and available
    if not is_valid_username(new_username) or not is_available_username(new_username):
        flash("Invalid username")
        return redirect(f'/profile/{session.get("username")}')

    # Update the user's username in the database and in the session
    users.update_one({"username": username}, {"$set": {'username': new_username}})
    session["username"] = new_username

    # Redirect to the new user profile page
    return redirect(f'/profile/{new_username}')


@app.route('/leaderboard/')
def leaderboard_page():
    """
    Render the leaderboard page with user statistics sorted by wins in descending order.

    Returns:
        str: A HTML page with the leaderboard table and title.
    """
    user_board = users.find({}).sort("wins", -1)

    return render_template('leaderboard.html', boards=user_board, title="Leaderboard")


# WEBSOCKET ROUTES

@socketio.on('create_room')
def create_room(data: Dict[str, str]) -> None:
    """
    Create a new room and add the player to it.

    Args:
        data: A dictionary containing information about the player.
            Requires the key "username" to be present.

    Returns:
        None.
    """
    room_code = generate_room_code(4)

    user1 = data["username"]
    players[room_code] = user1

    if data["maria"]:
        socketio.emit('new_maria_game', {'user2': 'MarIA', 'user1': user1})

    else:
        join_room(room_code)
        socketio.emit('new_game', {'room_id': room_code}, room=room_code)


@socketio.on('join_game')
def join_game(data: Dict[str, str]) -> None:
    """
    Join a game and emit a 'user2_joined' event to the specified room.

    Args:
        data: A dictionary containing information about the player and the room to join.
              Requires the keys "username" and "room_id" to be present.

    Returns:
        None
    """
    room_id = data['room_id']
    join_room(room_id)

    user1 = players[room_id]
    user2 = data['username']

    socketio.emit('user2_joined', {'user2': user2, 'user1': user1}, room=data['room_id'])


@socketio.on('leave_room')
def leave_room(data):
    """
        Emit a "leave" event and remove the current client from the specified room.

        Args:
            data: A dictionary containing information about the player and room.
                  Requires the keys "username" and "room_id" to be present.

        Returns:
            None
        """

    socketio.emit('leave', {'username': data['username']}, room=data['room_id'])


@socketio.on('show_game_user_1')
def show_game_user_1() -> None:
    """
    Emit a "show_game_user_1" event to the client.

    Returns:
        None
    """
    socketio.emit('show_game_user_1')


@socketio.on('register_player_choice')
def register_player_choice(data: Dict[str, str]) -> None:
    """
    Handle player choice of rock, paper, or scissors.

    Args:
        data: A dictionary containing information about the game state.
              Requires the keys "player1", "player2", "choice", and "room_id" to be present.

    Returns:
        None
    """
    handle_player_choice(data, socketio)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)
