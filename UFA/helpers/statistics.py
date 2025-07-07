import numpy as np
from collections import Counter
import itertools

def gac1(pairs):
    v1, v2 = pairs
    a = np.sum(v1 & v2)
    b = np.sum(v1 & ~v2)
    c = np.sum(~v1 & v2)
    d = np.sum(~v1 & ~v2)
    n = a + b + c + d

    raw_agreement = (a + d) / n
    alpha = (2 * a + b + c) / (2 * n)
    f = 2 * alpha * (1 - alpha)
    GAC1 = (raw_agreement - f) / (1 - f)
    return GAC1

def MI(word, fab, word_counts, n, fa):
    fb = word_counts[word]
    return np.log2(n * (fab / (fa * fb)))


def get_mi_score(df_words, df_corpus):

    text_corpus = df_corpus['text_processed']
    # fb is number of occurences of b in whole corpus
    word_counts = Counter(itertools.chain(*text_corpus.str.split()))
    # n is total number of words
    n = sum(word_counts.values())

    # fa is total number of a occurences in subcorpus
    fa = df_words.id.nunique()

    # fab is number of occurences of b in proximity of a
    df_mi = df_words.word.value_counts().reset_index()
    df_mi.columns = ['word', 'count']
    # df_mi = df_mi[df_mi['count'] > 5] # speed up
    df_mi['MI'] = df_mi.apply(lambda x: MI(x['word'], x['count'], word_counts, n, fa), axis=1)
    return df_mi