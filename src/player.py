from src.database import users
from typing import Dict


choice = {'choice1': '',
          'choice2': ''}


def _get_winner(choice1: str, choice2: str) -> str:
    """
    Determine the winner of the game based on the choices made by player 1 and player 2.

    Args:
        choice1: A string representing the choice made by player 1.
        choice2: A string representing the choice made by player 2.

    Returns:
        A string indicating the result of the game. Can be "player1_win", "player2_win", or "TIE".
    """
    if choice1 == choice2:
        return 'TIE'

    winning_combinations = {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    }

    if winning_combinations[choice1] == choice2:
        return 'player1_win'

    else:
        return 'player2_win'


def _update_winner(result: str, player1: str, player2: str) -> None:
    """
    Update the number of wins for the winner of the game in the database.

    Args:
        result: A string indicating the result of the game. Can be "player1_win", "player2_win", or "TIE".
        player1: A string representing the username of player 1.
        player2: A string representing the username of player 2.

    Returns:
        None
    """
    if result == 'player1_win':
        user_wins = users.find_one({"username": player1})['wins']
        users.find_one_and_update({"username": player1}, {"$set": {'wins': user_wins + 1}})

    elif result == 'player2_win':
        user_wins = users.find_one({"username": player2})['wins']
        users.find_one_and_update({"username": player2}, {"$set": {'wins': user_wins + 1}})


def handle_player_choice(data: Dict[str, str], player_choice: str, socketio) -> None:
    """
    Handle a player's choice of rock, paper, or scissors, and update the game state and send results to the clients.

    Args:
        data: A dictionary containing information about the game state.
              Requires the keys "player1", "player2", and "room_id" to be present.
        player_choice: A string representing the player's choice of rock, paper, or scissors.
        socketio: SocketIo

    Returns:
        None

    """

    if player_choice == "player1":
        choice['choice1'] = data['choice']
        # other_player = data['player2']
    else:
        choice['choice2'] = data['choice']
        # other_player = data['player1']

    choice1 = choice['choice1']
    choice2 = choice['choice2']

    # If both players have made a choice, determine the winner and update the game state
    if choice1 and choice2:
        result = _get_winner(choice1, choice2)
        _update_winner(result, data['player1'], data['player2'])
        socketio.emit('result', {'result': result}, room=data['room_id'])

        choice['choice1'] = ''
        choice['choice2'] = ''

    else:
        # If the other player hasn't made a choice yet, wait for them to do so
        socketio.emit('wait', {'person_waiting': data[player_choice]}, room=data['room_id'])


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
