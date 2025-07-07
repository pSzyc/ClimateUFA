from pathlib import Path
import pandas as pd
import os
from datetime import datetime
import re

materials_path = Path(__file__).parent.parent.parent / 'Classification' / "files"

stopwords = pd.read_csv( materials_path / 'polish_stopwords.txt', header=None)
STOPWORDS = set([word.rstrip() for word in stopwords[0]])


REPLACE_BY_SPACE_RE = re.compile(r'[/(){}\[\]\|@,;\.-]')
REPLACE_EXCESS_SPACES_RE = re.compile(r'\s\s+')
BAD_SYMBOLS_RE = re.compile('[^AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż1234567890 ]')

def create_results_dir(name: str):
    # Get current date and time
    now = datetime.now()

    # Format as a string
    now_str = now.strftime("%Y-%m-%d_%H-%M")

    # Create directory name
    dir_name = f"files/{now_str}"

    # Create directory
    os.makedirs(dir_name, exist_ok=False)
    dir_name = Path(dir_name)
    folder_name = dir_name / name
    os.makedirs(folder_name, exist_ok=False)

    return folder_name

def clean_text(text):
    text = text.lower()
    text = REPLACE_BY_SPACE_RE.sub(' ', text)
    text = REPLACE_EXCESS_SPACES_RE.sub(' ', text)
    text = BAD_SYMBOLS_RE.sub('', text)
    text = ' '.join(word for word in text.split() if word not in STOPWORDS)
    return text

def load_collocations(data_path: Path):
    if type(data_path) == str:
        data_path = Path(data_path)
    df = pd.read_csv(data_path / "colocates.csv", parse_dates= ['date'])
    return df

def load_lemma(folder_path:Path | str):
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    df = pd.read_csv(folder_path / "lemma_new.csv", parse_dates=['date'])
    df['clean_text'] = df['lemma'].apply(clean_text)
    cols = ["text", "clean_text", "id", 'date', 'source', 'eco_id']
    df = df[cols]
    return df

def load_corpus(corpus_path):
    if type(corpus_path) == str:
        corpus_path = Path(corpus_path)
    corp_files = [
        'eco_dorzeczy.csv',
        'eco_gpc.csv',
        'eco_newsweek.csv',
        'eco_polityka.csv',
        'eco_rzepa.csv',
        'eco_wpolityce.csv',
        'eco_wprost.csv',
        'eco_wyborcza.csv',
    ]

    data_list = []
    cols = ["text", "clean_text", "id", 'date', 'source']

    for file in corp_files:
        # Load the data
        data = pd.read_csv(corpus_path / file, parse_dates=['date'])
    
        # Make sure to only include columns of interest
        if 'id' not in data.columns:
            print(f"No id in {file}")
            data['id'] = data.index
        data = data[cols]   

        # Append to list
        data_list.append(data)

    df = pd.concat(data_list)
    assert (df['text'].isna() == False).all()

    return df

def save_corpus_df(data_path, df):
    df.to_csv(data_path / "corpus.csv", index=False)

def save_collocations_df(data_path, df):
    df.to_csv(data_path / "colocates.csv", index=False)

def save_words_df(data_path, df):
    df.to_csv(data_path / "words.csv", index=False)