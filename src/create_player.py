# from src.database import users
# from typing import Tuple
# from flask import flash
# import uuid
#
#
# def is_valid_username(username: str) -> bool:
#     """
#     Check if a given username is valid.
#
#     Args:
#         username (str): The username to check.
#
#     Returns:
#         bool: True if the username is valid, False otherwise.
#     """
#     return '/' not in username
#
#
# def is_available_username(username: str) -> bool:
#     """
#     Check if a given username is available.
#
#     Args:
#         username (str): The username to check.
#
#     Returns:
#         bool: True if the username is available, False otherwise.
#     """
#     return users.find_one({"username": username}) is None
#
#
# def _search_db_available(db_search_type: str, user_search_type: str, users) -> bool:
#     """
#         Check if a given user search type value is available in the database for the given search type.
#
#         Args:
#             db_search_type (str): The search type to use for the database query.
#             user_search_type (str): The value to search for in the database for the given search type.
#
#         Returns:
#             bool: True if the user search type value is not found in the database for the given search type,
#             False otherwise.
#         """
#
#     return users.find_one({db_search_type: user_search_type}) is None
#
#
# def create_player(username: str, email: str, password: str, bcrypt) -> dict:
#     """
#     Create a new user object.
#
#     Args:
#         username: The username of the user.
#         email: The email of the user.
#         password: The password of the user.
#
#     Returns:
#         A dictionary containing the user's information.
#     """
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(password.encode(), salt)
#
#     user = {
#         "_id": uuid.uuid4().hex,
#         "username": username,
#         "email": email,
#         "salt": salt,
#         "password": hashed_password,
#         "wins": 0,
#         "played": 0,
#         "games": {"datetime": [], "rps": [], "result": []}  # TODO: add more data to be collected
#     }
#
#     return user
#
#
# def _is_available(type_check_available: bool, type_of_check: str) -> bool:
#     """
#     Check if the given type is available. If it's not, a flash message is added, and the user is redirected to the
#     signup page.
#
#     Args:
#         type_check_available (bool): A boolean that indicates whether the given type is available or not.
#         type_of_check (str): A string indicating the type being checked.
#
#     Returns:
#         Union[None, redirect]: None if the type is available, else a redirect to the signup page.
#     """
#     if not type_check_available:
#         flash(f"{type_of_check} already in use")
#         return False
#
#     return True
#
#
# def check_email_and_username_availability(user, users) -> Tuple[bool, bool]:
#     """
#     Check if the email and username are available in the given database. Raises a ValueError if not.
#
#     Args:
#         user: A dictionary containing information about the user.
#         users:
#     Returns:
#         None
#     """
#     # Check if any users exist in the database
#     if users.count_documents({}) > 0:
#         # Check if Name and/or Email exists
#         available_email = _search_db_available("email", user['email'], users)
#         available_name = _search_db_available("username", user['username'], users)
#
#         return _is_available(available_email, "Email"), _is_available(available_name, "Name")
