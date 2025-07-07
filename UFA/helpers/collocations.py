import re


def _insert_space_before_pattern(text, pattern):
        replacement = r' \1'
        return re.sub(pattern, replacement, text)

def correct_text(df, correction_pattern):
    df['text_processed'] = df['clean_text'].apply(lambda x: re.sub(r'[\n\.\-]', ' ', x)) ### substitutes '\n', '.' and '-' with ' '
    df['text_processed'] = df['text_processed'].apply(lambda x: re.sub(r'\u2028', ' ', x)) ### substitute
    df['text_processed'] = df['text_processed'].apply(lambda x: re.sub(r'\s+', ' ', x)) ### substitutes one or more ' ' with just one ' '
    df['text_processed'] = df['text_processed'].apply(lambda x: re.sub(r'[^\dAaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż ]', '', x)) ### removes non-digits and non-polish characters with ' ', why the last space???
    df['text_processed'] = df['text_processed'].str.lower()
    df['text_processed'] = df['text_processed'].apply(lambda x: _insert_space_before_pattern(text=x, pattern=correction_pattern))
    return df

def _get_collocations(article, bigram_pattern):
    word1, word2 = bigram_pattern.split()
    collocations = []
    for i in range(len(article) - 1):
        if article[i].startswith(word1) and article[i+1].startswith(word2):
            collocations_left = article[max(0, i-5):i]  # use slice notation
            collocations_right = article[i+2:min(i+7, len(article))]  # use slice notation
            collocation = ' '.join(collocations_left + collocations_right)
            collocations.append(collocation)
    return collocations
   

def extract_collocations_bigram(df, bigram_pattern):
     #### SPLITTING TEXT INTO LISTS
    word1, word2 = bigram_pattern.split()
    df['text_processed'] = df['text_processed'].apply(lambda x: x.split())
    df['collocations'] = df.text_processed.apply(lambda x: _get_collocations(x, bigram_pattern))
    df['raw_count'] = df['collocations'].apply(len)
    df['text_processed'] = df['text_processed'].apply(lambda x: ' '.join(x))
    df['real_count'] = df['text'].apply(lambda x: len(re.findall(f"{word1}[^ ]* {word2}[^ ]*", x, re.IGNORECASE)))
    print(f"Real count: {df['real_count'].sum()}")
    print(f"Raw count: {df['raw_count'].sum()}")
    #assert (df['real_count'] == df['raw_count']).all()
    return df

def collocations_df(df):
    df_exploded = df[df['raw_count'] > 0].explode('collocations')
    df_exploded.reset_index(drop=True, inplace=True)
    df_exploded.rename(columns={'raw_colocates': 'colocate', 'id': 'text_id'}, inplace=True)
    df_exploded['id'] = df_exploded.index
    df_exploded.drop(columns=['clean_text', 'text_processed', 'raw_count', 'real_count'], inplace=True)
    return df_exploded

def words_df(df):
    df['word'] = df.collocations.str.split(" ")
    df = df.explode('word')
    df.drop('collocations', inplace=True, axis=1)
    return df