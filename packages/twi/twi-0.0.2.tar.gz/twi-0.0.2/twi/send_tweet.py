import sys

from twi.app import send_tweet, USER_ID


def main() -> None:
    if len(sys.argv) != 2:
        print("please provide a tweet")
        sys.exit()
    res = send_tweet(sys.argv[1])
    id_ = res._json["id"]
    print(f"Okay, published the tweet at https://twitter.com/{USER_ID}/status/{id_}")


