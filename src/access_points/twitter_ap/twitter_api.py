import tweepy



auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print (tweet.text)