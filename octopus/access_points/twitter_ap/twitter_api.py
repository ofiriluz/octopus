import tweepy
from src.access_points.auth_keys import TWITTER_ACCESS_TOKEN,TWITTER_TOKEN_SECRET,TWITTER_API_KEY,TWITTER_API_SECRET

class TwitterUser(object):
    def __init__(self,user):
        self.user = user

    def to_dictionary(self):

        self.user_dict = {}
        self.user_dict['name'] = self.user.name
        self.user_dict['screen_name'] = self.user.screen_name
        self.user_dict['url'] = self.user.url
        self.user_dict['followers_count'] = self.user.followers_count
        self.user_dict['friends'] = [{'name': f.name,'description':f.description}
                                     for f in self.get_user_friends(names_only=False)]
        self.user_dict['profile_image_url'] = self.user.profile_image_url
        self.user_dict['description'] = self.user.description
        self.user_dict['statuses_count'] = self.user.statuses_count
        self.user_dict['time_zone'] = self.user.time_zone
        self.user_dict['location'] = self.user.location
        self.user_dict['friends_count'] = self.user.friends_count
        self.user_dict['recent_status'] = self.user.status.text
        return self

    def get_user_friends(self, names_only = True):
        if names_only:
            return [friend.screen_name for friend in self.user.friends()]
        else:
            return self.user.friends()
    def build_time_line(self,time_line):
        self.user_dict['user_tweets'] = [{'text':tweet.text,
                                          'date':tweet.created_at,
                                          'source': tweet.source,
                                          'coordinates':tweet.coordinates,
                                          'retweets' : tweet.retweet_count}
                                         for tweet in time_line]
        return self

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
            return TwitterUser(user)
        except:
            print("[Error] no such twitter name {}".format(user_name))
            return None
    def get_user_time_line(self, user_name):
        try:
            time_line = self.api.user_timeline(user_name)
            return time_line
        except:
            return None

if __name__ == "__main__":
    twitter = TwitterAPI()
    # find user info
    user = twitter.get_user("isan_rivkin")
    # find user tweets
    time_line = twitter.get_user_time_line("isan_rivkin")
    # build user dictionary
    print(user.to_dictionary().build_time_line(time_line).user_dict)