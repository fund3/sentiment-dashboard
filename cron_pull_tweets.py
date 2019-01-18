from datetime import datetime
import simplejson as json
import tweepy
import elasticsearch_dsl
from elasticsearch_dsl import connections


# Model for storing tweets in Elasticsearch
class ESTweet(elasticsearch_dsl.Document):
    tid = elasticsearch_dsl.Integer()
    created_at = elasticsearch_dsl.Date()
    stored_at = elasticsearch_dsl.Date()
    text = elasticsearch_dsl.Text(analyzer='snowball')


def prepare_tweet(t, stored_at):
    ans = ESTweet(tid=t.id_str,
                  created_at=t.created_at,
                  stored_at=stored_at,
                  text=t.text)
    return ans


def get_tweets(env):
    # Setup Twitter access:
    auth = tweepy.OAuthHandler(env['tw_oauth_key'], env['tw_oauth_secret'])
    auth.set_access_token(env['tw_token_key'], env['tw_token_secret'])
    api = tweepy.API(auth)

    # Set default Elasticsearch client
    connections.create_connection(hosts=[env['es_endpoint']])

    tweets_response = api.search('bitcoin')

    cursor = tweepy.Cursor(api.search, q='bitcoin', lang='en', count=100, tweet_mode='extended')

    # tweets = []
    stored_at = datetime.now()
    for page in cursor.pages(15):
        # tweets.extend(page)
        for item in page:
            # TODO: Check if tweet is already stored.
            t = prepare_tweet(item, stored_at)
            t.save(index='tweets')

    # for t in tweets:
    #
    #     es_tweet = ESTweet(tid=t.id_str,
    #                        created_at=t.created_at,
    #                        stored_at=datetime.now(),
    #                        text=t.text)
    #     ans = es_tweet.save(index='tweets')
    #     print(ans)


if __name__ == '__main__':
    with open('secrets.txt', 'r') as f:
        params = json.load(f)
    get_tweets(params)
