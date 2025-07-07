import string
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

NGRAM_RANGE = (1, 3)

TOP_K = 7500

TOKEN_MODE = 'word'

MIN_DOCUMENT_FREQUENCY = 5

def ngram_vectorize(train_texts, train_labels, val_texts, return_models = False):

    kwargs = {
            'ngram_range': NGRAM_RANGE,
            'dtype': np.float32, 
            'strip_accents': 'unicode',
            'decode_error': 'replace',
            'analyzer': TOKEN_MODE, 
            'min_df': MIN_DOCUMENT_FREQUENCY,
    }
    vectorizer = TfidfVectorizer(**kwargs)

    x_train = vectorizer.fit_transform(train_texts)

    x_val = vectorizer.transform(val_texts)

    selector = SelectKBest(f_classif, k=min(TOP_K, x_train.shape[1]))
    selector.fit(x_train, train_labels)
    x_train = selector.transform(x_train).astype(np.float32)
    x_val = selector.transform(x_val).astype(np.float32)

    x_train = x_train.toarray()
    x_val = x_val.toarray()

    if return_models:
        return  x_train, x_val, vectorizer, selector
    else:
        return x_train, x_val

def vectorize(data, vectorizer, selector):
    data = vectorizer.transform(data)
    data = selector.transform(data).astype(np.float32)
    return data.toarray()

def meta_features(data, STOPWORDS):
  # word_count
  data['Całkowita ilość słów'] = data['text'].apply(lambda x: len(str(x).split()))
  data['Ilość słów bez powtórzeń'] = data['text'].apply(lambda x: len(set(str(x).split())))

  # stop_word_count
  data['Ilość stop-słów'] = data['text'].apply(lambda x: len([w for w in str(x).lower().split() if w in STOPWORDS]))

  # mean_word_length
  data['Średnia długość słowa'] = data['text'].apply(lambda x: np.mean([len(w) for w in str(x).split()]))

  # char_count
  data['Ilość symboli'] = data['text'].apply(lambda x: len(str(x)))

  # punctuation_count
  data['Ilość znaków interpunkcyjnych'] = data['text'].apply(lambda x: len([c for c in str(x) if c in string.punctuation]))
  return data


def vectorize_dataset(configuration, df):
    METAFEATURES = configuration.METAFEATURES
    df_train, df_test = train_test_split(df, test_size=0.1)
    scaler = StandardScaler()
    meta_train = scaler.fit_transform(df_train[METAFEATURES])
    meta_test = scaler.transform(df_test[METAFEATURES])
    train_x = df_train.drop(columns=['label'])
    train_y = df_train['label']

    test_x = df_test.drop(columns=['label'])
    test_y = df_test['label']

    text_train, text_test, vectorizer, selector = ngram_vectorize(train_x['clean_text'], train_y, test_x['clean_text'], return_models=True)
    train_ngram_x  = np.concatenate([text_train, meta_train], axis=1)
    test_ngram_x  = np.concatenate([text_test, meta_test], axis=1)
    return train_ngram_x, train_y, test_ngram_x, test_y, scaler, vectorizer, selector

def preprocess(configuration, df):
  STOPWORDS = configuration.STOPWORDS
  df = meta_features(df, STOPWORDS)
  return df