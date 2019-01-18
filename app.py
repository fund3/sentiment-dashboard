from flask import Flask, render_template
import simplejson as json
import bokeh.resources
import bokeh.plotting
import bokeh.embed

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', resources=bokeh.resources.CDN.render())


@app.route('/get_tweets.json', methods=['GET'])
def get_tweets():
    import cron_pull_tweets
    with open('secrets.txt', 'r') as f:
        params = json.load(f)

    tweets = cron_pull_tweets.get_tweets(params)

    print(tweets)

    xs = []
    ys = []
    for t in tweets:
        xs.append(float(t['subjectivity']))
        ys.append(float(t['polarity']))

    fig = bokeh.plotting.figure(plot_width=800, plot_height=400)
    fig.xaxis.axis_label = 'subjectivity'
    fig.yaxis.axis_label = 'polarity'
    fig.circle(x=xs, y=ys)

    print(xs)
    print(ys)

    ans = {
        'tweets': tweets,
        'plot': bokeh.embed.json_item(fig, 'plot_div')
    }

    return json.dumps(ans)


if __name__ == '__main__':
    app.run(port=33507)
