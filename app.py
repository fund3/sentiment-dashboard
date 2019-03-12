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
    params = _get_env_params()

    client = Elasticsearch(hosts=[params['es_endpoint']])
    tweets = es_client.get_tweets(client)

    # Convert to DataFrame:
    df_tweets = pd.DataFrame.from_records(tweets)

    # Polarity plot using inhouse estimator:
    ih_sentiments = sentiments.calc_sentiments(df_tweets, tweet_column='full_text')

    # Add in-house sentiment to tweet_dicts:
    for tweet_dict, ih_sent in zip(tweets, ih_sentiments):
        tweet_dict['ih_sentiment'] = int(ih_sent)

    ans = {'tweets': tweets}
    return json.dumps(ans)


@app.route('/get_mean_sentiments.json', methods=['GET'])
def get_mean_sentiments():
    """
    Via a GET request, returns a JSON object containing a time series of mean hourly sentiment ticks.
    """

    params = _get_env_params()

    client = Elasticsearch(hosts=[params['es_endpoint']])
    ticks = es_client.get_mean_hourly_sentiment_ticks(client)

    # Convert to DataFrame:
    df = pd.DataFrame.from_records(ticks)
    df.index = pd.to_datetime(df['timestamp'])
    df = df.drop(columns='timestamp')
    df = df.dropna()

    # Sentiment plot:
    mean_sentiments_plot = plotting.plot_polarity_vs_time(df, polarity_column='value')

    ans = {
        'mean_sentiments_plot': bokeh.embed.json_item(mean_sentiments_plot)
    }

    return json.dumps(ans)


if __name__ == '__main__':
    app.run(port=33507)
