"""
TODO: make a function to update the banner and maybe the photo
TODO: publish to PyPI
TODO: add scheduling of tweets
TODO: check for new DMs and forward them to email
"""
import os

from dotenv import load_dotenv
import tweepy

load_dotenv()

USER_ID = os.getenv("TWITTER_USER_ID")
        
auth = tweepy.OAuthHandler(
    os.getenv('TWITTER_CONSUMER_KEY'),
    os.getenv('TWITTER_CONSUMER_SECRET'),
)
auth.set_access_token(
    os.getenv('TWITTER_ACCESS_TOKEN'),
    os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
)
api = tweepy.API(auth)


def send_tweet(tweet: str):
    return api.update_status(status=tweet)


def update_profile_description(description: str):
    # TODO: store the history somewhere, for rollbacks
    # TODO: make a function to roll back the profile
    return api.update_profile(description=description)


def delete_last_tweet() -> tweepy.models.Status:
    last_tweet_id = api.user_timeline(user_id=USER_ID)[0].id # type: ignore
    return api.destroy_status(last_tweet_id)
