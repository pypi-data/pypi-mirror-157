from twi.app import delete_last_tweet

def main():
    res = delete_last_tweet()
    id_ = res._json["id"]
    print(f'Okay, deleted your last tweet, ID "{id_}".')
