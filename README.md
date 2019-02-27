# Bitcoin Sentiments

A real-time Bitcoin sentiments dashboard.
Developed by [gdiazc](https://github.com/gdiazc),
in collaboration with Fund3 and The Data Incubator.

Demo available at [bitcoin-sentiment-dashboard.herokuapp.com](http://bitcoin-sentiment-dashboard.herokuapp.com/).

Description of requirements:

1. **A clear business objective.**
The business objective of Bitcoin Sentiments is to improve
prediction of Bitcoin currency exchange price by providing
users with real-time visual tracking of Bitcoin related
conversations on Twitter, and to provide the data pipeline
and storage infrastructure for Bitcoin sentiment data to
be made available for further Bitcoin currency exchange
analytics.
2. **Data ingestion.**
Bitcoin sentiments uses an hourly scheduled cron job
(see [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler))
to pull tweets from the [Twitter API](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html).
The tweets are subsequently stored in an Elasticsearch instance
which is hosted on [AWS Elasticsearch](https://aws.amazon.com/elasticsearch-service/).
The logic can be seen in `bin/cron_pull_tweets.py`.
3. **Visualizations.**
The dashboard itself has as a real-time visualization of
*mean hourly sentiment* of recent tweets, retrieved
asynchronously via a `GET` request to the `/get_mean_sentiments.json`
path, and plotted using [Bokeh](https://bokeh.pydata.org/en/latest/).
In addition, the right panel contains a sample of recent
tweets.
4. **Machine learning.**
The tweet sentiments themselves are calculated using machine
learning, where a Multinomial Naive Bayes classifier has
been trained on the [Sentiments Analysis Dataset](http://thinknook.com/twitter-sentiment-analysis-training-corpus-dataset-2012-09-22),
which consists of ~1.5 million labelled tweets. The model
was implemented using [scikit-learn](http://scikit-learn.org/),
achieving 77.4 f-score.
5. **A deliverable**.
The present repository will be delivered to Fund3, consisting
of the documented code and the `Analysis.ipynb` notebook.
