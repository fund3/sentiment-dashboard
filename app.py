import os

import bokeh.embed
import bokeh.plotting
import bokeh.resources
import pandas as pd
import simplejson as json
from flask import Flask, render_template
from elasticsearch import Elasticsearch

import es_client
import plotting
import sentiments


app = Flask(__name__)


def _get_env_params():
    app_env = os.environ.get('APP_ENV', default='DEVELOPMENT')
    if app_env == 'PRODUCTION':
        params = {
            'tw_oauth_key': os.environ['tw_oauth_key'],
            'tw_oauth_secret': os.environ['tw_oauth_secret'],
            'tw_token_key': os.environ['tw_token_key'],
            'tw_token_secret': os.environ['tw_token_secret'],
            'es_endpoint': os.environ['es_endpoint']
        }
    else:
        with open('secrets.txt', 'r') as f:
            params = json.load(f)
    return params


@app.route('/')
def index():
    return render_template('index.html', resources=bokeh.resources.CDN.render())


@app.route('/get_tweets.json', methods=['GET'])
def get_tweets():
    """
    Via a GET request, returns a JSON object containing a sample of recent tweets.
    """

    # TODO: client object should be cached between requests.
    params = _get_env_params()
    client = Elasticsearch(hosts=[params['es_endpoint']])

    # Get tweets and process:
    tweets = es_client.get_tweets(client)
    df_tweets = pd.DataFrame.from_records(tweets)
    df_tweets = df_tweets[df_tweets['full_text'].apply(sentiments.tweet_nonhashtag_ratio) >= 0.8]
    df_tweets['ih_sentiment'] = sentiments.calc_sentiments(df_tweets, tweet_column='full_text')

    tweets_json = json.loads(df_tweets.to_json(orient='records'))
    return json.dumps({'tweets': tweets_json})


@app.route('/get_mean_sentiments.json', methods=['GET'])
def get_mean_sentiments():
    """
    Via a GET request, returns a JSON object containing a time series of mean hourly sentiment ticks.
    """

    params = _get_env_params()

    def make_ticks_dataframe(ticks):
        df = pd.DataFrame.from_records(ticks)
        df.index = pd.to_datetime(df['timestamp'])
        df = df.drop(columns='timestamp')
        df = df.dropna()
        return df

    client = Elasticsearch(hosts=[params['es_endpoint']])

    # Mean Sentiments Ticks:
    ticks_sentiments = es_client.get_mean_hourly_sentiment_ticks(client)
    df_sentiments = make_ticks_dataframe(ticks_sentiments)
    plot_sentiments = plotting.plot_polarity_vs_time(df_sentiments, polarity_column='value')

    # Mean Scores Ticks:
    ticks_scores = es_client.get_mean_tweet_score_ticks(client)
    df_scores = make_ticks_dataframe(ticks_scores)
    plot_scores = plotting.build_plot_scores(df_scores, values_column='value')

    return json.dumps({
        'mean_sentiments_plot': bokeh.embed.json_item(plot_sentiments),
        'mean_scores_plot': bokeh.embed.json_item(plot_scores),
    })


if __name__ == '__main__':
    app.run(port=33507)
