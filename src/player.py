from src.maria_brain import generate_maria_choice
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


def handle_player_choice(data: Dict[str, str], socketio) -> None:
    """
    Handle a player's choice of rock, paper, or scissors, and update the game state and send results to the clients.

    Args:
        data: A dictionary containing information about the game state.
              Requires the keys "player1", "player2", and "room_id" to be present.
        socketio: SocketIo

    Returns:
        None

    """
    player_choice = data["player_number"]

    if player_choice == "player1":
        choice['choice1'] = data['choice']

        if data['player2'] == "MarIA":
            choice["choice2"] = generate_maria_choice()

    else:
        choice['choice2'] = data['choice']

    choice1 = choice['choice1']
    choice2 = choice['choice2']

    # If both players have made a choice, determine the winner and update the game state
    if choice1 and choice2:
        winner = _get_winner(choice1, choice2)

        if winner != "TIE":
            _update_winner(data[winner])

        socketio.emit('result', {'result': winner}, room=data['room_id'])

        choice['choice1'] = ''
        choice['choice2'] = ''

    else:
        # If the other player hasn't made a choice yet, wait for them to do so
        socketio.emit('wait', {'person_waiting': player_choice}, room=data['room_id'])


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
