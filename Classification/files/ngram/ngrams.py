import pandas as pd
import regex as re
import spacy
from pathlib import Path
from collections import defaultdict

nlp = spacy.load('pl_core_news_sm')
files_path = Path(__file__).parent.parent
stopwords = pd.read_csv(files_path / 'polish_stopwords.txt', header=None)
STOPWORDS = set([word.rstrip() for word in stopwords[0]])
REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;\.]')
REPLACE_EXCESS_SPACES_RE = re.compile('\s\s+')
BAD_SYMBOLS_RE = re.compile('[^AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż1234567890 ]')

def lemmatizer(text):
  doc = nlp(text)
  return " ".join([token.lemma_ for token in doc])

def clean_text(text):
    """
        text: a string

        return: modified initial string
    """
    text = text.lower() # lowercase text
    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
    text = REPLACE_EXCESS_SPACES_RE.sub(' ', text)
    text = BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # No Stemming
    if text == None:
      text == "None None None"
    return text

def preprocess(df):
    df['title'] = df['title'].fillna("None")
    df['clean_text'] = df['text'].apply(clean_text)
    df['clean_title'] = df['title'].apply(clean_text)
    df['clean_title'] = df['clean_title'].apply(lemmatizer)
    df['clean_text'] = df['clean_text'].apply(lemmatizer)
    return df


def generate_ngrams(text, n_gram=1):
    token = [token for token in text.lower().split(' ') if token != '' if token not in STOPWORDS]
    ngrams = zip(*[token[i:] for i in range(n_gram)])
    return [' '.join(ngram) for ngram in ngrams]


def ngram_counter(ngram, df):
  eco_ngrams = defaultdict(int)

  for article in df['clean_text']:
      for word in generate_ngrams(article, ngram):
          eco_ngrams[word] += 1
        
          
  df_eco_ngrams = pd.DataFrame(sorted(eco_ngrams.items(), key=lambda x: x[1])[::-1])

  return df_eco_ngrams


def get_eco_vocab():
    df = pd.read_csv(files_path / "ngram" / "ngrams.csv")
    return df['phrase'].values

def save_rest_ngrams(df, n = 400, file = "rest"):
    df_eco_unigrams = ngram_counter(1, df)
    df_eco_bigrams = ngram_counter(2, df)
    df_eco_trigrams = ngram_counter(3, df)
    eco_vocab = get_eco_vocab()

    df_eco_unigrams[~df_eco_unigrams[0].isin(eco_vocab)].iloc[:n].to_csv(files_path/ f"ngram/uni_{file}.csv", index = False)
    df_eco_bigrams[~df_eco_bigrams[0].isin(eco_vocab)].iloc[:n].to_csv(files_path/ f"ngram/bi_{file}.csv", index = False)
    df_eco_trigrams[~df_eco_trigrams[0].isin(eco_vocab)].iloc[:n].to_csv(files_path/ f"ngram/tri_{file}.csv", index = False)