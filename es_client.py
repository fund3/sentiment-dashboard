# from datetime import datetime
from elasticsearch_dsl import Document, InnerDoc, Integer, Date, Text, Search, Float


class ESTweet(Document):
    """
    elasticsearch-dsl model for storing and retrieving tweets.
    """
    created_at = Date()
    stored_at = Date()
    full_text = Text(analyzer='snowball')
    subjectivity = Float()
    polarity = Float()
    author_id = Integer()
    author_followers = Integer()

    class Index:
        name = 'tweets'


def _get_with_default(obj, key, default=None):
    return obj[key] if key in obj else default


def tweet_to_estweet(t, stored_at, sentiment=None):
    """
    Converts a tweepy Tweet object to an ESTweet.

    :param t: tweepy Tweet object
    :param stored_at: datetime object
    :param sentiment: TextBlob sentiment object
    :return:
    """

    subj = 'NaN'
    pola = 'NaN'
    if sentiment:
        subj = sentiment.subjectivity
        pola = sentiment.polarity

    ans = ESTweet(created_at=t.created_at,
                  stored_at=stored_at,
                  full_text=t.full_text,
                  subjectivity=subj,
                  polarity=pola,
                  author_id=t.user.id,
                  author_followers=t.user.followers_count)
    ans.meta.id = t.id
    return ans


def get_tweets(client, max_tweets=5000):
    """
    Get tweets from the Elasticsearch endpoint specified by client.

    :param client: Elasticsearch client object.
    :return: list of tweet represented as dicts.
    """
    search = Search(index='tweets').using(client).query('match_all').sort('created_at')
    search.execute()

    tweets = []
    for row in search.scan():
        if len(tweets) <= max_tweets:
            created_at = _get_with_default(row, 'created_at')
            full_text = _get_with_default(row, 'full_text')
            if created_at and full_text:
                t = {
                    'id_str': row.meta.id,
                    'created_at': created_at,
                    'full_text': full_text
                }
                tweets.append(t)

    if len(tweets) > max_tweets:
        tweets = tweets[:max_tweets]

    return tweets
