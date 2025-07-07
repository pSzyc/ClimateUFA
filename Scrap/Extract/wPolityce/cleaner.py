import regex as re

def title_cleaner(row):
    title = row['title'].strip()
    author = row['author']
    if author != None:
        title = re.split(r"\n", title)[0]
        return title[0].upper() + title[1:].lower()
    return title.replace("\n", " ")

def text_cleaner(text):
    text = re.sub("\s\s+", " ", text)
    line_split = re.split(r"\|", text)

    text = " ".join(split for split in line_split if len(split) > 50)
    text = re.sub("^[ \d\.-]+\n", "", text)
    text = re.sub("(?i)fot\..*\n", "", text)
    dot_problem = re.search(r"[A-Za-z]\n[A-Za-z]", text)
    if dot_problem != None:
        problem_string = dot_problem.group()
        text = re.sub(problem_string, problem_string.replace("\n", ""), text)
    text = text.replace("\n", " ").strip()
    text = re.sub("dagmarammateja@gmail\.com", "", text)
    return text

def date_cleaner(row):
    date = row['date'].replace(".", "\.")
    text = row['text']
    text = re.sub("(?i)" + date,"", text)
    text = re.sub("(�|�)", "", text)
    return text

def weird_cleaner(df):
    df['text'] = df['text'].apply(lambda x: re.sub("COC", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("(ZĄ+ )+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("OO+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("CC+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("(JSJS)+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("(AC )+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("(ZĄ )+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("(EN )+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("TE+", "", x))
    df['text'] = df['text'].apply(lambda x: re.sub("STOCK ", "", x))
    return df

def clean_df(df):
    df['title'] = df.apply(title_cleaner, axis=1)
    df['text'] = df['text'].apply(text_cleaner)
    df['text'] = df.apply(date_cleaner, axis=1)
    df.drop(columns=["next page"], inplace=True)
    return df