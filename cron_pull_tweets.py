import os
from datetime import datetime
import tweepy
# from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections, Search
from textblob import TextBlob
import es_client
import nltk
nltk.download('punkt')


def run_task(params, ntweets=3, maxpages=2):
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

            t = es_client.prepare_tweet(result, stored_at=stored_at, sentiment=sentiment)

            ans = t.save(index='tweets')
            print(ans)

    # search = Search(index='tweets').query("match_all")
    # results = search.execute()
    # print(results.hits.total)
    # for row in search.scan():
    #     print(row)
    # print(results)
    print('done')


if __name__ == '__main__':
    if 'PRODUCTION' in os.environ:
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
