# from flask import request, session, redirect, url_for, flash
# from src.create_player import create_player, check_email_and_username_availability
# from typing import Dict, Union, Optional
# from flask_socketio import join_room, leave_room
# # from werkzeug import Response
# from src.database import users
# from random import choices
# from string import ascii_uppercase
# import bcrypt
#
#
# players = {}
#
# choice = {'choice1': '',
#           'choice2': ''}
#
#
# def _start_session(user: Dict[str, str]) -> redirect:
#     """
#     Start a new session for the given user.
#
#     Args:
#         user (dict): A dictionary containing user information, including the user's ID and username.
#
#     Returns:
#         flask.redirect: A redirect to the user's profile page.
#     """
#     session['logged_in'] = True
#     session['userid'] = user["_id"]
#     session["username"] = user["username"]
#
#     return redirect('/lobby/')
#
#
# def _generate_room_code(string_length: int) -> str:
#     """
#     Generate a random string of uppercase letters with the given length.
#
#     Args:
#         string_length (int): The length of the random string to generate.
#
#     Returns:
#         str: A random string of uppercase letters.
#     """
#     return ''.join(choices(ascii_uppercase, k=string_length))
#
#
# def _check_valid_username(username: str) -> Union[None, redirect]:
#     """
#     Check if a username is valid, and if not, flash an error message and redirect to the signup page.
#
#     Args:
#         username: A string containing the username to be checked.
#
#     Returns:
#         None if the username is valid, or a redirect to the signup page if the username is invalid.
#     """
#     if '/' in username:
#         flash("Usernames cannot contain '/'!")
#         return redirect(url_for('signup_page'))
#     return None
#
#
# def _check_password() -> redirect:
#     """
#     Check if password and confirm_password fields match.
#
#     Returns:
#         flask.redirect: A redirect to the signup page if passwords do not match.
#     """
#     if request.form.get('password') != request.form.get('confirm_password'):
#         flash("Passwords do not match")
#         return redirect(url_for('signup_page'))
#
#
# def signup() -> Union[redirect, None]:
#     """
#     Sign up a new user by adding their information to the database.
#
#     Returns:
#         Union[flash, redirect]: A flash message if the sign-up is unsuccessful,
#         or a redirect to the login page if the sign-up is successful.
#     """
#
#     username = request.form.get('username')
#     _check_valid_username(username)
#
#     user = create_player(username=request.form.get('username'),
#                          email=request.form.get('email'),
#                          password=request.form.get('password'),
#                          bcrypt=bcrypt)
#
#     available_email, available_name = check_email_and_username_availability(user=user, users=users)
#
#     if not available_name or not available_email:
#         return redirect(url_for('signup_page'))
#
#     _check_password()
#
#     users.insert_one(user)
#
#     return redirect(url_for('login_page'))
#
#
# def signout() -> redirect:
#     """
#     Clears the user's session and redirects to the homepage.
#
#     Returns:
#         flask.redirect: A redirect to the homepage.
#     """
#     session.clear()
#     flash("Successfully signed out!")
#     return redirect('/')
#
#
# def login() -> Optional[redirect]:
#     """
#     Log in the user with the email and password from the request form.
#
#     Returns:
#         Optional[flask.redirect]: A redirect to the user's profile page if login successful,
#         otherwise a redirect to the home page.
#     """
#
#     if len(list(users.find({}))) > 0:
#         user_found: dict = users.find_one({"email": request.form.get('email')})
#
#         if user_found and bcrypt.hashpw(request.form.get('password').encode(),
#                                         user_found['salt']) == user_found['password']:
#
#             return _start_session(user_found)
#
#     flash("Can't login due to wrong password or invalid email.")
#
#     return redirect('/')
#
#
# def enter_game_room(data):
#
#     if data["player1"]:
#         room_id = _generate_room_code(4)
#         players[room_id] = {"player1": data['player1'], "player2": None}
#
#     else:
#         room_id = data['room_code']
#         players[room_id]["player2"] = data['player2']
#
#     join_room(room_id)
#
#     return redirect(url_for('game', room_code=room_id))
#
#
# def _get_winner(choice1: str, choice2: str) -> str:
#     """
#     Determine the winner of the game based on the choices made by player 1 and player 2.
#
#     Args:
#         choice1: A string representing the choice made by player 1.
#         choice2: A string representing the choice made by player 2.
#
#     Returns:
#         A string indicating the result of the game. Can be "player1_win", "player2_win", or "TIE".
#     """
#     if choice1 == choice2:
#         return "TIE"
#
#     winning_combinations = {
#         'rock': 'scissor',
#         'scissor': 'paper',
#         'paper': 'rock'
#     }
#
#     if winning_combinations[choice1] == choice2:
#         return 'player1'
#
#     else:
#         return 'player2'
#
#
# def _update_winner(player_name: str) -> None:
#     """
#     Update the number of wins for the winner of the game in the database.
#
#     Args:
#         player_name: A string representing the username of win player.
#
#     Returns:
#         None
#     """
#
#     user_wins = users.find_one({"username": player_name})['wins']
#     users.find_one_and_update({"username": player_name}, {"$set": {'wins': user_wins + 1}})
#
#
# def handle_player_choice(data: Dict[str, str], socketio) -> None:
#     """
#     Handle a player's choice of rock, paper, or scissors, and update the game state and send results to the clients.
#
#     Args:
#         data: A dictionary containing information about the game state.
#               Requires the keys "player1", "player2", and "room_id" to be present.
#         socketio: SocketIo
#
#     Returns:
#         None
#
#     """
#     player_choice = data["player_number"]
#
#     if player_choice == "player1":
#         choice['choice1'] = data['choice']
#
#         # if data['player2'] == "MarIA":
#         #     choice["choice2"] = generate_maria_choice()
#
#     else:
#         choice['choice2'] = data['choice']
#
#     choice1 = choice['choice1']
#     choice2 = choice['choice2']
#
#     # If both players have made a choice, determine the winner and update the game state
#     if choice1 and choice2:
#         winner = _get_winner(choice1, choice2)
#
#         if winner != "TIE":
#             _update_winner(data[winner])
#
#         socketio.emit('result', {'result': winner}, room=data['room_id'])
#
#         choice['choice1'] = ''
#         choice['choice2'] = ''
#
#     else:
#         # If the other player hasn't made a choice yet, wait for them to do so
#         socketio.emit('wait', {'person_waiting': player_choice}, room=data['room_id'])
