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
