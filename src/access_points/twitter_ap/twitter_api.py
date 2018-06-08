import tweepy
from src.access_points.auth_keys import TWITTER_ACCESS_TOKEN,TWITTER_TOKEN_SECRET,TWITTER_API_KEY,TWITTER_API_SECRET


class TwitterAPI(object):
    def __init__(self):
        self.auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        self.auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
    # testing => get our account tweets
    def get_self_tweets(self):
        tweets = [tweet.text for tweet in self.api.home_timeline()]
        return tweets

    # Get the User object for twitter...
    def get_user(self,user_name):
        user = self.api.get_user(user_name)
        return user


if __name__ == "__main__":
    user = TwitterAPI().get_user("isan_rivkin")
    print(user.screen_name)
    print(user.followers_count)
    for friend in user.friends():
        print(friend.screen_name)
