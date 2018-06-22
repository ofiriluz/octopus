import re
import tweepy
from octopus.access_points.auth_keys import TWITTER_ACCESS_TOKEN,TWITTER_TOKEN_SECRET,TWITTER_API_KEY,TWITTER_API_SECRET

class TwitterUser(object):
    def __init__(self,user):
        self.user = user

    def to_dictionary(self):
        try:
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
        except:
            return None

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
    def search_users(self,query):
        try:
            raw_users =  self.api.search_users(query)
            parsed_users = [TwitterUser(user) for user in raw_users]
            return parsed_users
        except:
            return None
    def educated_guess_target(self,target_name, target_keywords, users, with_timeline = False):
        users_dicts = [users.user_dict for user in users]
        all_bags = {}
        for dic in users_dicts:
            bag = self.to_bag_of_words(dic)
            all_bags.append(bag)

            pass
    def to_bag_of_words(self,user_dic, with_time_line = False):
        bag = []
        bag.append(user_dic['name'].lower())
        bag.append(user_dic['screen_name'].lower())
        bag.append(user_dic['url'].lower())
        bag += [re.sub('[^A-Za-z0-9]+', '', d.lower()) for d in user_dic['description'].split(' ')]
        bag.append(user_dic['time_zone'].lower() if user_dic['time_zone'] is not None else '')
        bag.append(user_dic['location'].lower() if user_dic['location'] is not None else '')

        if len(user_dic['recent_status']) > 0:
            bag += [re.sub('[^A-Za-z0-9]+', '', d.lower()) for d in user_dic['recent_status'].split(' ')]

        for friend in user_dic['friends']:
            bag.append(friend['name'].lower())
            bag += [re.sub('[^A-Za-z0-9]+', '', d.lower()) for d in friend['description'].split(' ')]

        if with_time_line:
            pass

        return bag

if __name__ == "__main__":


     twitter = TwitterAPI()

        # TODO:: complete educated_guess_target() with the help of to_bag_of_words()
     ### example 3 : make an estimation and guess the user from list of results + suspect keywords ###
     user_dic = twitter.get_user("isan_rivkin").to_dictionary().user_dict
     suspect_keywords = ['ethereum','programmer']
     bag = twitter.to_bag_of_words(user_dic)
     print(bag)

    ### example 2 : search user name and parse all user results into TwitterUser() object ###

    # search_result = twitter.search_users("isan rivkin")
    # for user in search_result:
    #     print (user.to_dictionary().user_dict)


    ### example 1 : get user info and twitts from the time line ###

    # # find user info
    # user = twitter.get_user("isan_rivkin")
    # # find user tweets
    # time_line = twitter.get_user_time_line("isan_rivkin")
    # # build user dictionary
    # print(user.to_dictionary().build_time_line(time_line).user_dict)
    #
