# from datetime import datetime
from elasticsearch_dsl import Document, Integer, Date, Text, Search, Float


class ESTweet(Document):
    id_str = Integer()
    created_at = Date()
    stored_at = Date()
    full_text = Text(analyzer='snowball')
    subjectivity = Float()
    polarity = Float()


def _get_with_default(obj, key, default=None):
    return obj[key] if key in obj else default


def prepare_tweet(t, stored_at, sentiment=None):
    subj = 'NaN'
    pola = 'NaN'
    if sentiment:
        subj = sentiment.subjectivity
        pola = sentiment.polarity
    ans = ESTweet(id_str=t.id_str,
                  created_at=t.created_at,
                  stored_at=stored_at,
                  full_text=t.full_text,
                  subjectivity=subj,
                  polarity=pola)
    return ans


def get_tweets(client):
    search = Search(index='tweets').using(client).query("match_all")
    results = search.execute()

    tweets = []
    for row in results:
        id_str = _get_with_default(row, 'tid')
        created_at = _get_with_default(row, 'created_at')
        full_text = _get_with_default(row, 'text')
        if id_str and created_at and full_text:
            t = {
                'id_str': id_str,
                'created_at': created_at,
                'full_text': full_text
            }
            tweets.append(t)

    return tweets
    # stored_at = datetime.now()
    # # TODO: switch back to 15 pages
    # for page in cursor.pages(15):
    #     for tweet in page:
    #         blob = TextBlob(tweet.full_text)
    #         sents = blob.sentences
    #         if len(sents) >= 1:
    #             sent = sents[0]
    #             sentiment = sent.sentiment
    #         else:
    #             sentiment = 'NaN'
    #
    #         t = {
    #             'id_str': tweet.id_str,
    #             'created_at': tweet.created_at.isoformat(),
    #             'full_text': tweet.full_text,
    #             'subjectivity': sentiment.subjectivity,
    #             'polarity': sentiment.polarity
    #         }
    #
    #         tweets.append(t)
    #     # tweets.extend(page)
    #     # for item in page:
    #     #     # TODO: Check if tweet is already stored.
    #     #     t = prepare_tweet(item, stored_at)
    #     #     t.save(index='tweets')
    #
    # return tweets
