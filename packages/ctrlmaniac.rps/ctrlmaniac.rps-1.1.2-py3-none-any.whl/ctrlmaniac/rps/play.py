"""Main module."""
from ctrlmaniac.rps.rps import (
    TheCaothicOne,
    TheMimic,
    TheNonStrategicOne,
    TheRock,
    computers_battle,
    human_vs_computer,
    print_pause,
    validate_input,
)


def play():
    players = [
        TheRock(),
        TheMimic(),
        TheNonStrategicOne(),
        TheCaothicOne(),
    ]

    print_pause("Welcome to Rock Paper Scissors!\n")
    print_pause("1. Do you want to play?")
    print_pause("2. Do you want to see other playing?")

    choice = validate_input("Type 1 o 2: ", ["1", "2"])

    if int(choice) == 1:
        human_vs_computer(players)
    else:
        computers_battle(players)


if __name__ == "__main__":
    play()
