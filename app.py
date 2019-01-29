from flask import Flask, render_template
import os
import simplejson as json
import bokeh.resources
import bokeh.plotting
import bokeh.embed
from elasticsearch import Elasticsearch
from textblob import TextBlob
import es_client
import pandas as pd

app = Flask(__name__)


def _get_env_params():
    if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'PRODUCTION':
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


    import dateutil

    id_strs = []
    created_ats = []
    full_texts = []
    subjs = []
    polas = []
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
        subjs.append(float(sentiment.subjectivity))
        polas.append(float(sentiment.polarity))

        id_strs.append(t['id_str'])
        created_ats.append(dateutil.parser.parse(t['created_at']))
        full_texts.append(t['full_text'])

    df = pd.DataFrame({
        'id_str': id_strs,
        'created_at': created_ats,
        'full_text': full_texts,
        'subjectivity': subjs,
        'polarity': polas
    })

    fig = bokeh.plotting.figure(plot_width=600, plot_height=400)
    fig.xaxis.axis_label = 'subjectivity'
    fig.yaxis.axis_label = 'polarity'
    fig.circle(x=subjs, y=polas, size=5)

    # Second plot (average hourly polarity):
    s_polarity = df[['polarity', 'created_at']].set_index('created_at').resample('H').mean()

    fig2 = bokeh.plotting.figure(plot_width=600, plot_height=400)
    fig2.xaxis.axis_label = 'hour'
    fig2.yaxis.axis_label = 'polarity'
    fig2.line(x=s_polarity.index.values, y=s_polarity['polarity'].values)

    ans = {
        'tweets': tweets,
        'plot': bokeh.embed.json_item(fig, 'plot_div'),
        'plot2': bokeh.embed.json_item(fig2, 'plot2_div')
    }

    return json.dumps(ans)


if __name__ == '__main__':
    app.run(port=33507)
