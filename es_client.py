from elasticsearch_dsl import Document, Integer, Date, Text, Search, Float


class ESTweet(Document):
    """
    elasticsearch-dsl model for storing and retrieving tweets.
    """
    created_at = Date()
    stored_at = Date()
    version = Text()
    full_text = Text(analyzer='snowball')
    author_id = Integer()
    author_followers = Integer()
    retweet_count = Integer()

    class Index:
        name = 'tweets'


class MeanSentimentTick(Document):
    value = Float()
    timestamp = Date(default_timezone='UTC')
    version = Text()
    label = Text()

    class Index:
        name = 'mean_sentiment_ticks'


def _get_with_default(obj, key, default=None):
    return obj[key] if key in obj else default


def make_mean_sentiment_tick(value, timestamp, version, label):
    ans = MeanSentimentTick(
        value=value,
        timestamp=timestamp,
        version=version,
        label=label
    )
    return ans


def tweet_to_estweet(t, stored_at, version):
    """
    Converts a tweepy Tweet object to an ESTweet.

    :param t: tweepy Tweet object
    :param stored_at: datetime object
    :param version: version information to distinguish tweets
    :return:
    """

    ans = ESTweet(created_at=t.created_at,
                  stored_at=stored_at,
                  version=version,
                  full_text=t.full_text,
                  author_id=t.user.id,
                  author_followers=t.user.followers_count,
                  retweet_count=t.retweet_count)
    ans.meta.id = t.id
    return ans


def tweepy_to_dict(tweet, stored_at=None, version=None):
    """
    Converts a tweepy Tweet object to a dict.
    """

    ans = {
        'created_at': tweet.created_at,
        'full_text': tweet.full_text,
        'author_id': tweet.user.id,
        'author_followers': tweet.user.followers_count,
        'retweet_count': tweet.retweet_count,
        'id_str': tweet.id,
    }

    if stored_at:
        ans['stored_at'] = stored_at

    if version:
        ans['version'] = version

    return ans


def get_tweets(client, max_tweets=500):
    """
    Get tweets from the Elasticsearch endpoint specified by client.

    :param client: Elasticsearch client object.
    :return: list of tweets represented as dicts.
    """

    search = Search(index='tweets')\
        .using(client)\
        .query('match_all')\
        .sort({'created_at': {'order': 'desc'}})[:max_tweets]
    search.execute()

    tweets = []
    for hit in search:
        if len(tweets) < max_tweets:
            version = _get_with_default(hit, 'version', default=None)
            created_at = _get_with_default(hit, 'created_at', default=None)
            full_text = _get_with_default(hit, 'full_text', default=None)
            if created_at and full_text:
                t = {
                    'id_str': hit.meta.id,
                    'created_at': created_at,
                    'full_text': full_text
                }

                if version and version >= '20190222':
                    t['version'] = version
                    t['author_followers'] = _get_with_default(hit, 'author_followers', default=None)
                    t['retweet_count'] = _get_with_default(hit, 'retweet_count', default=None)

                tweets.append(t)

    return tweets


def get_mean_hourly_sentiment_ticks(client, max_ticks=1000):
    """
    Get mean hourly sentiment ticks from the Elasticsearch endpoint specified by client.

    :param client: Elasticsearch client object.
    :param max_ticks: Max length of the hourly ticks series to be retrieved.
    :return: list of ticks represented as dicts.
    """

    # TODO: match a specific version
    search = Search(index='mean_sentiment_ticks')\
        .using(client)\
        .query('match', label='mean_hourly_sentiment')\
        .sort({'timestamp': {'order': 'desc'}})[:max_ticks]
    search.execute()

    return [
        {
            'timestamp': hit.to_dict().get('timestamp', None),
            'value': hit.to_dict().get('value', None)
        } for hit in search
    ]


def get_mean_tweet_score_ticks(client, max_ticks=1000):
    """
    Get mean hourly sentiment ticks from the Elasticsearch endpoint specified by client.

    :param client: Elasticsearch client object.
    :param max_ticks: Max length of the hourly ticks series to be retrieved.
    :return: list of ticks represented as dicts.
    """

    # TODO: match a specific version
    search = Search(index='mean_sentiment_ticks')\
        .using(client)\
        .query('match', label='mean_tweet_score')\
        .sort({'timestamp': {'order': 'desc'}})[:max_ticks]
    search.execute()

    return [
        {
            'timestamp': hit.to_dict().get('timestamp', None),
            'value': hit.to_dict().get('value', None)
        } for hit in search
    ]
