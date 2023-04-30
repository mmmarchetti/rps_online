from random import choice
from time import sleep


def generate_maria_choice():
    """
    Generate a random choice for Maria
    """
    sleep(3)
    choices = ["rock", "paper", "scissor"]
    return choice(choices)
