from datetime import datetime
import simplejson as json
import tweepy
import elasticsearch_dsl
from elasticsearch_dsl import connections
from textblob import TextBlob
import nltk
nltk.download('punkt')


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

    # TODO: switch back to 100
    cursor = tweepy.Cursor(api.search, q='bitcoin', lang='en', count=10, tweet_mode='extended')

    tweets = []
    stored_at = datetime.now()
    # TODO: switch back to 15 pages
    for page in cursor.pages(1):
        for tweet in page:
            blob = TextBlob(tweet.full_text)
            sents = blob.sentences
            if len(sents) >= 1:
                sent = sents[0]
                sentiment = sent.sentiment
            else:
                sentiment = 'NaN'

            t = {
                'id_str': tweet.id_str,
                'created_at': tweet.created_at.isoformat(),
                'full_text': tweet.full_text,
                'subjectivity': sentiment.subjectivity,
                'polarity': sentiment.polarity
            }

            tweets.append(t)
        # tweets.extend(page)
        # for item in page:
        #     # TODO: Check if tweet is already stored.
        #     t = prepare_tweet(item, stored_at)
        #     t.save(index='tweets')

    return tweets


if __name__ == '__main__':
    with open('secrets.txt', 'r') as f:
        params = json.load(f)
    get_tweets(params)
