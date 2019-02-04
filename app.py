import os

import dateutil
import bokeh.embed
import bokeh.plotting
import bokeh.resources
import nltk
import pandas as pd
import simplejson as json
from flask import Flask, render_template
from elasticsearch import Elasticsearch
from textblob import TextBlob

import es_client
import plotting


nltk.download('punkt')
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

    id_strs = []
    created_ats = []
    full_texts = []
    subjectivities = []
    polarities = []
    for t in tweets:
        blob = TextBlob(t['full_text'])
        sents = blob.sentences
        if len(sents) >= 1:
            sent = sents[0]
            sentiment = sent.sentiment
        else:
            sentiment = None

        t['subjectivity'] = sentiment.subjectivity
        t['polarity'] = sentiment.polarity
        subjectivities.append(float(sentiment.subjectivity))
        polarities.append(float(sentiment.polarity))

        id_strs.append(t['id_str'])
        created_ats.append(dateutil.parser.parse(t['created_at']))
        full_texts.append(t['full_text'])

    df = pd.DataFrame({
        'id_str': id_strs,
        'created_at': created_ats,
        'full_text': full_texts,
        'subjectivity': subjectivities,
        'polarity': polarities
    })

    # First plot:
    polarity_subjectivity_scatter_plot = plotting.plot_polarity_vs_subjectivity(df)

    # Second plot:
    s_polarity = df[['polarity', 'created_at']].set_index('created_at').resample('H').mean()
    polarity_plot = plotting.plot_polarity_vs_time(s_polarity)

    ans = {
        'tweets': tweets,
        'plot': bokeh.embed.json_item(polarity_subjectivity_scatter_plot, 'plot_div'),
        'plot2': bokeh.embed.json_item(polarity_plot, 'plot2_div')
    }

    return json.dumps(ans)


if __name__ == '__main__':
    app.run(port=33507)
