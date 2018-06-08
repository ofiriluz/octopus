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
        try:
            user = self.api.get_user(user_name)
            return user
        except:
            print("[Error] no such twitter name {}".format(user_name))
            return None


if __name__ == "__main__":
    user = TwitterAPI().get_user("isan_rivkin")
    if user is not None:
        print(user.screen_name)
        print(user.followers_count)
        for friend in user.friends():
            print(friend.screen_name)
