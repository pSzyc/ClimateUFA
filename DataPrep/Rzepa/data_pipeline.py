import re

def splitter(text):
    re_expr = "([A-Z]*[a-z]+)([A-Z][a-z]*)"
    matches = re.findall(re_expr, text)
    if matches != None:
        for match in matches:
            text_found = "".join(match)
            to_replace = match[0] + " " + match[1]
            text = text.replace(text_found, to_replace)
    return text

def author_extract(text):
    extracted = re.search('((?<=\\t—).*)|(.*(?=@rp\.pl))', text)
    return extracted[0] if extracted is not None else extracted


def restore_authors(df):
    df['last'] = df['text'].apply(lambda x: x.split(' ')[-1])
    df['extracted'] = df['last'].apply(author_extract)
    df.loc[df['author']=='None', 'author'] = df["extracted"]
    df.drop(columns = ['last', 'extracted'], inplace = True)
    return df

def dot_problem_solver(text):
    THREE_DOT_RE = re.compile('(?<=[^\s])\.\.\.(?=[^\s])')
    text = THREE_DOT_RE.sub('... ', text)
    DOT_RE = re.compile('(?<=[^\s\.])\.(?=[^\s\.])')
    text = DOT_RE.sub('. ', text)
    QUEST_RE = re.compile('(?<=[^\s])\?(?=[^\s])')
    text = QUEST_RE.sub('? ', text)
    return text

def data_pipeline(data, cols):
    data = data[data['text'].notna()]
    #data.loc[~data['title'].apply(lambda x: isinstance(x, str)), 'title'] = "None"  # newsweek

    for col in cols:
        data[col] = data[col].fillna('None')

    CLEAN_XLSX_1 = re.compile('[(∑)]')
    REPLACE_EXCESS_SPACES_RE = re.compile('\s\s+')
    data['text'] = data['text'].apply(lambda x: re.split('(?i)©℗\s*Więcej\s*na', x)[0])
    for col in cols:
        data[col] = data[col].apply(lambda x: REPLACE_EXCESS_SPACES_RE.sub(' ', x))
        data[col] = data[col].apply(lambda x: CLEAN_XLSX_1.sub('', x))
        data[col] = data[col].apply(lambda x: x.replace("\xad", ""))
        data[col] = data[col].apply(lambda x: x.replace("\xa0", " "))
        data[col] = data[col].apply(lambda x: x.replace("_x0007_", " "))


    data['department'] = data['department'].str.strip()
    data['author'] = data['author'].str.strip()
    return data