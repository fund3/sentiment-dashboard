import os
from datetime import datetime
import tweepy
from elasticsearch_dsl import connections
from textblob import TextBlob
import es_client
import nltk
nltk.download('punkt')


def run_task(params, ntweets=3, maxpages=2):
    """
    Standalone task which searches for tweets using tweepy and stores them
    in an Elasticsearch instance.

    :param params: Twitter auth and Elasticsearch parameters.
    :param ntweets: Number of tweets to request.
    :param maxpages: Max pages to iterate.
    :return:
    """

    # Setup Twitter access:
    auth = tweepy.OAuthHandler(params['tw_oauth_key'], params['tw_oauth_secret'])
    auth.set_access_token(params['tw_token_key'], params['tw_token_secret'])
    api = tweepy.API(auth)

    # Set default Elasticsearch client
    connections.create_connection(hosts=[params['es_endpoint']])

    cursor = tweepy.Cursor(api.search, q='bitcoin', lang='en', count=ntweets, tweet_mode='extended')
    stored_at = datetime.now()

    for page in cursor.pages(maxpages):
        for result in page:
            print(result)
            blob = TextBlob(result.full_text)
            sents = blob.sentences
            sentiment = None
            if len(sents) >= 1:
                sent = sents[0]
                sentiment = sent.sentiment

            tid = result.id
            es_tweet = es_client.ESTweet.get(tid, ignore=404)
            if not es_tweet:
                print('new tweet')
                t = es_client.tweet_to_estweet(result, stored_at=stored_at, sentiment=sentiment)
                t.save(index='tweets')  # TODO: explicitly giving the index shouldn't be necessary
                print(t)
            else:
                print('old tweet')
                print(es_tweet)
    print('done')


if __name__ == '__main__':
    if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'PRODUCTION':
        params = {
            'tw_oauth_key': os.environ['tw_oauth_key'],
            'tw_oauth_secret': os.environ['tw_oauth_secret'],
            'tw_token_key': os.environ['tw_token_key'],
            'tw_token_secret': os.environ['tw_token_secret'],
            'es_endpoint': os.environ['es_endpoint']
        }
    else:
        import simplejson as json
        with open('secrets.txt', 'r') as f:
            params = json.load(f)

    run_task(params)
