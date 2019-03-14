import os
from datetime import datetime

import numpy as np
import pandas as pd
import tweepy
from elasticsearch_dsl import connections

import es_client
import sentiments

# Version information to track elasticsearch tweets
ES_TWEET_VERSION = '20190222'


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

    tweets = []
    for page in cursor.pages(maxpages):
        for result in page:
            tid = result.id
            es_tweet = es_client.ESTweet.get(tid, ignore=404)
            if not es_tweet:
                tweets.append(es_client.tweepy_to_dict(result))
                t = es_client.tweet_to_estweet(result,
                                               stored_at=stored_at,
                                               version=ES_TWEET_VERSION)
                t.save(index='tweets')

    df_tweets = pd.DataFrame.from_records(tweets)
    df_tweets = df_tweets[df_tweets['full_text'].apply(sentiments.tweet_nonhashtag_ratio) >= 0.8]
    df_tweets['ih_sentiment'] = sentiments.calc_sentiments(df_tweets, tweet_column='full_text')

    # Precompute and persist hourly ticks:
    precompute_mean_sentiment(df_tweets, stored_at)
    precompute_mean_score(df_tweets, stored_at)

    print('done')


def precompute_mean_sentiment(df_tweets, stored_at):
    """
    Calculate and persist the mean sentiment for retreived tweets.
    """
    hourly_mean = df_tweets['ih_sentiment'].mean()
    tick = es_client.make_mean_sentiment_tick(
        value=hourly_mean, timestamp=stored_at, version=ES_TWEET_VERSION, label='mean_hourly_sentiment')
    tick.save(index='mean_sentiment_ticks')


def precompute_mean_score(df_tweets, stored_at):
    """
        Calculate and persist the mean score for retreived tweets.
    """
    mean_tweet_score = df_tweets['ih_sentiment'] \
                       * (np.log(df_tweets['author_followers']) + 1) \
                       * (df_tweets['retweet_count'] + 1)
    mean_tweet_score = mean_tweet_score.mean()

    tick = es_client.make_mean_sentiment_tick(
        value=mean_tweet_score, timestamp=stored_at, version=ES_TWEET_VERSION, label='mean_tweet_score')
    tick.save(index='mean_sentiment_ticks')


if __name__ == '__main__':
    app_env = os.environ.get('APP_ENV', default='DEVELOPMENT')

    if app_env == 'PRODUCTION':
        params = {
            'tw_oauth_key': os.environ['tw_oauth_key'],
            'tw_oauth_secret': os.environ['tw_oauth_secret'],
            'tw_token_key': os.environ['tw_token_key'],
            'tw_token_secret': os.environ['tw_token_secret'],
            'es_endpoint': os.environ['es_endpoint'],
            'param_ntweets': os.environ.get('P_CRON_NTWEETS', default=100)
        }
    else:
        import simplejson as json

        with open('secrets.txt', 'r') as f:
            params = json.load(f)

    run_task(params, ntweets=params['param_ntweets'])
