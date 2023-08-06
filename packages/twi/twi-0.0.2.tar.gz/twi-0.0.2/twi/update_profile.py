import sys

from twi.app import update_profile_description


def main() -> None:
    if len(sys.argv) != 2:
        print("please provide a profile description")
        sys.exit()
    update_profile_description(sys.argv[1])
    print("okay, updated profile")
