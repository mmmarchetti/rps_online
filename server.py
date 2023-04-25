from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash
from werkzeug import Response

from src.forms import RegistrationForm, LoginForm, JoinRoom, EditUserForm
from src.database import users
from flask_socketio import SocketIO, join_room, leave_room
from typing import Union, Tuple, Dict, Optional
from dotenv import load_dotenv
import uuid
import html
import os
from random import choices
from string import ascii_uppercase
import bcrypt


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Access environment variables using os.environ
app.secret_key = os.environ.get("SECRET_KEY")

# Start SocketIo
socketio = SocketIO(app, cors_allowed_origins='*')

# Socket global variables
players = {}

choice = {'player1': None,
          'player2': None}


# Player functions


def is_valid_username(username: str) -> bool:
    """
    Check if a given username is valid.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    return '/' not in username


def is_available_username(username: str) -> bool:
    """
    Check if a given username is available.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username is available, False otherwise.
    """
    return users.find_one({"username": username}) is None


def _search_db_available(db_search_type: str, user_search_type: str) -> bool:
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


def create_player(username: str, email: str, password: str) -> dict:
    """
    Create a new user object.

    Args:
        username: The username of the user.
        email: The email of the user.
        password: The password of the user.

    Returns:
        A dictionary containing the user's information.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    user = {
        "_id": uuid.uuid4().hex,
        "username": username,
        "email": email,
        "salt": salt,
        "password": hashed_password,
        "wins": 0,
        "played": 0,
        "games": {"datetime": [], "rps": [], "result": []}  # TODO: add more data to be collected
    }

    return user


def _is_available(type_check_available: bool, type_of_check: str) -> bool:
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
        return False

    return True


def check_email_and_username_availability(user) -> Tuple[bool, bool]:
    """
    Check if the email and username are available in the given database. Raises a ValueError if not.

    Args:
        user: A dictionary containing information about the user.

    Returns:
        None
    """
    available_email = _search_db_available("email", user['email'])
    available_name = _search_db_available("username", user['username'])

    return _is_available(available_email, "Email"), _is_available(available_name, "Name")


# Game Session Functions


def _start_session(user: Dict[str, str]) -> redirect:
    """
    Start a new session for the given user.

    Args:
        user (dict): A dictionary containing user information, including the user's ID and username.

    Returns:
        flask.redirect: A redirect to the user's profile page.
    """
    session['logged_in'] = True
    session['userid'] = user["_id"]
    session["username"] = user["username"]
    session['player_room_id'] = None

    return redirect('/lobby/')


def _generate_room_code(string_length: int) -> str:
    """
    Generate a random string of uppercase letters with the given length.

    Args:
        string_length (int): The length of the random string to generate.

    Returns:
        str: A random string of uppercase letters.
    """
    return ''.join(choices(ascii_uppercase, k=string_length))


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


def _check_password() -> redirect:
    """
    Check if password and confirm_password fields match.

    Returns:
        flask.redirect: A redirect to the signup page if passwords do not match.
    """
    if request.form.get('password') != request.form.get('confirm_password'):
        flash("Passwords do not match")
        return redirect(url_for('signup_page'))


def signup() -> Union[redirect, None]:
    """
    Sign up a new user by adding their information to the database.

    Returns:
        Union[flash, redirect]: A flash message if the sign-up is unsuccessful,
        or a redirect to the login page if the sign-up is successful.
    """

    username = request.form.get('username')
    _check_valid_username(username)

    user = create_player(username=request.form.get('username'),
                         email=request.form.get('email'),
                         password=request.form.get('password'))

    available_email, available_name = check_email_and_username_availability(user=user)

    if not available_name or not available_email:
        return redirect(url_for('signup_page'))

    _check_password()

    users.insert_one(user)

    return redirect(url_for('login_page'))


def signout() -> redirect:
    """
    Clears the user's session and redirects to the homepage.

    Returns:
        flask.redirect: A redirect to the homepage.
    """
    session.clear()
    flash("Successfully signed out!")
    return redirect('/')


def login() -> Optional[redirect]:
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

            return _start_session(user_found)

    flash("Can't login due to wrong password or invalid email.")

    return redirect('/')


def _get_winner(choice1: Union[str, None], choice2: Union[str, None]) -> str:
    """
    Determine the winner of the game based on the choices made by player 1 and player 2.

    Args:
        choice1: A string representing the choice made by player 1.
        choice2: A string representing the choice made by player 2.

    Returns:
        A string indicating the result of the game. Can be "player1_win", "player2_win", or "TIE".
    """
    if choice1 == choice2:
        return "TIE"

    winning_combinations = {
        'rock': 'scissor',
        'scissor': 'paper',
        'paper': 'rock'
    }

    if winning_combinations[choice1] == choice2:
        return 'player1'

    else:
        return 'player2'


def _update_winner(player_name: str) -> None:
    """
    Update the number of wins for the winner of the game in the database.

    Args:
        player_name: A string representing the username of win player.

    Returns:
        None
    """

    user_wins = users.find_one({"username": player_name})['wins']
    users.find_one_and_update({"username": player_name}, {"$set": {'wins': user_wins + 1}})


def handle_player_choice(data: Dict[str, str]) -> None:
    """
    Handle a player's choice of rock, paper, or scissors, and update the game state and send results to the clients.

    Args:
        data: A dictionary containing information about the game state.
              Requires the keys "player1", "player2", and "room_id" to be present.

    Returns:
        None

    """
    player_number = data["player_number"]

    choice[player_number] = data['choice']

    room_id = data['player_room_id']

    # If both players have made a choice, determine the winner and update the game state
    if choice['player1'] and choice['player2']:

        winner = _get_winner(choice['player1'], choice['player2'])

        if winner != "TIE":
            _update_winner(data[winner])

        socketio.emit('result', {'result': winner, 'coices': choice}, room=room_id)

        notify_opponent_choice(players_choices=choice, room=room_id)

        choice['player1'] = None
        choice['player2'] = None

    else:
        # If the other player hasn't made a choice yet, wait for them to do so
        socketio.emit('wait', {'person_waiting': player_number}, room=room_id)


def _get_game_message(player1, player2, session_user):
    """ Get the message to be displayed in the game page.

    Args:
        player1 (str): The username of the first player.
        player2 (str): The username of the second player.
        session_user (str): The username of the user in the current session.

    Returns:
        str: The message to be displayed in the game page.
    """
    # verify if the user is in the game
    if session_user in [player1, player2]:
        # verify if the game has started
        if not player2:
            message = f"Waiting for Player2 join... Send to your friend the Room ID code."
        else:
            message = f"Game Started! {player1} VS {player2}"

    # if the user is not in the game
    else:
        if player2:
            message = f"Sorry, this room is full. Please try another room."
        else:
            message = f"Please click 'Join Game' to join this room"

    return message


def notify_opponent_choice(players_choices, room):
    """
    Notify the opponent of the player's choice.
    """
    socketio.emit('update_opponent_choice',
                  {'choices': players_choices},
                  room=room)


# ROUTES


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
        return login()

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
        return signup()

    return render_template('register.html', form=registration_form)


@app.route("/lobby/", methods=["GET", "POST"])
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
    return signout()


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


@app.route('/edit-username/<string:username>', methods=['POST'])
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


@app.route('/create-game/', methods=['POST', 'GET'])
def create_game_page() -> Union[str, redirect]:
    """
    Render the game page with the given room id.

    Args:
        room_code (str): The room id of the game to be rendered.

    Returns:
        Union[str, redirect]: The rendered game page with the room id, or a redirect to the lobby page.
    """
    player_room_id = _generate_room_code(4)
    session['player_room_id'] = player_room_id  # todo limpar room id depois de sair do jogo

    players[player_room_id] = {"player1": session.get('username', ''), "player2": None}

    return redirect(url_for('enter_game_page', room=player_room_id))


@app.route('/join-game/', methods=['POST', 'GET'])
def join_game_page() -> Union[str, redirect]:
    """
    Render the game page with the given room id.

    Args:
        player_room_id (str): The room id of the game to be rendered.

    Returns:
        Union[str, redirect]: The rendered game page with the room id, or a redirect to the lobby page.
    """
    player_room_id = request.form.get('player_room_id')

    if player_room_id in players:

        if players[player_room_id]["player2"] is None:

            players[player_room_id]["player2"] = session.get('username', '')
            session['player_room_id'] = player_room_id

            return redirect(url_for('enter_game_page', room=player_room_id))

        else:
            flash("Sorry, this room is full. Please try another room.")
            return redirect(url_for('lobby_page'))
    else:
        flash("Sorry, this room does not exist. Please try another room.")
        return redirect(url_for('lobby_page'))


@app.route('/game', methods=['POST', 'GET'])
def enter_game_page() -> Union[str, redirect]:
    """
    Render the game page with the given room id.

    Args:
        room (str): The room id of the game to be rendered.

    Returns:
        Union[str, redirect]: The rendered game page with the room id, or a redirect to the lobby page.
    """
    player_room_id = request.args.get('room')

    if player_room_id in players:

        session_user = session.get('username', '')
        player1 = players[player_room_id]["player1"]
        player2 = players[player_room_id]["player2"]

        message = _get_game_message(player1, player2, session_user)

        return render_template('gameplay.html',
                               message=message,
                               player1=player1,
                               player2=player2,
                               username=session_user,
                               game_room_id=player_room_id)

    return redirect(url_for("lobby_page"))


# WEBSOCKET ROUTES


@socketio.on('start_game')
def start_game() -> None:
    """
    Emit a "load_event" event to the client.

    Returns:
        None
    """
    player_room_id = session.get('player_room_id', '')

    if player_room_id in players:
        player1 = players[player_room_id]["player1"]
        player2 = players[player_room_id]["player2"]
        join_room(player_room_id)

        socketio.emit("send_info_player_event", {"player_room_id": player_room_id,
                                                 "player1": player1,
                                                 "player2": player2},
                      room=player_room_id)

        if player1 and player2:
            socketio.emit('show_game_event', {}, room=player_room_id)


@socketio.on('leave_game_page')
def leave_game_page(data: Dict[str, str]) -> None:
    """
    Remove the player from the room and emit a "player_left" event to the other player(s).

    Returns:
        None
    """
    player_room_id = data['player_room_id']
    player = data['player']

    if session.get('player_room_id', '') == player_room_id:

        session['player_room_id'] = None

        socketio.emit('clear_game_event', {'player': player, 'player_room_id': player_room_id}, room=player_room_id)

        leave_room(player_room_id)

        players.pop(player_room_id)


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
    handle_player_choice(data)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)
