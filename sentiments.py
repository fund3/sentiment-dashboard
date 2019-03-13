import re

import dill
import nltk
from sklearn import base
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class TwitterPreprocessor(base.BaseEstimator, base.TransformerMixin):
    def __init__(self, tweet_column):
        self.tweet_column = tweet_column
        self.tw_tokenizer = nltk.tokenize.TweetTokenizer(
            strip_handles=True, reduce_len=True, preserve_case=False)

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        col = X[self.tweet_column]
        col = col.apply(self._prepare_tweet)
        return col

    def _prepare_tweet(self, tweet):
        tokens = self.tw_tokenizer.tokenize(tweet)
        clean_tweet = ' '.join([token for token in tokens
                                if len(token) > 1
                                and not token.startswith('http')])
        return clean_tweet


def tweet_nonhashtag_ratio(tweet):
    """
    Calculates the percentage of the tweet left over after removing hastags.
    """
    return len(re.sub(r'#\w+', '', tweet)) / len(tweet)


def calc_sentiments(df_tweets, tweet_column='full_text'):
    """
    Return a sentiments series

    :param df_tweets: A DataFrame containing tweets
    :param tweet_column: column to extract tweet content from
    :return:
    """

    tw_preprocessor = TwitterPreprocessor(tweet_column=tweet_column)
    tfidf_vectorizer: TfidfVectorizer = dill.load(open('tfidf_vectorizer.dill', 'rb'))
    best_mnb_estimator: MultinomialNB = dill.load(open('best_mnb_estimator.dill', 'rb'))

    pipe_estimator = Pipeline([
        ('tw_preprocessor', tw_preprocessor),
        ('tfidf_vectorizer', tfidf_vectorizer),
        ('best_mnb_estimator', best_mnb_estimator)
    ])

    prediction = pipe_estimator.predict(df_tweets)
    return prediction
