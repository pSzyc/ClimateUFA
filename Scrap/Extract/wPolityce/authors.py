import regex as re

def clean_author(fun):
    def wrapped(text):
        author = fun(text)
        if author != None:
            author = re.sub("(?i)rozm(o|a)w[^ ]*","", author)
            author = re.sub("(?i)redaguj[^ ]*","", author)
            author = re.sub("\s\s+", " ", author)
            author = author.strip()
            author_split = author.split(" ")
            if len(author_split) <= 1:
                return None
            if all(list(map(lambda x: len(x) == 1, author_split))):
                return None
            author = " ".join([
                word[0].upper() + word[1:].lower()
                for word in author_split
                ])
        return author
    return wrapped

@clean_author
def get_authors_1(text):
    search = re.search("\n [a-zA-Z].*", text)
    if search == None:
        return None
    else:
        author = search.group().strip()
        return author
    
@clean_author
def get_authors_2(text):
    search = re.search("\n[a-zA-Z].*", text)
    if search == None:
        return None
    else:
        author = search.group().strip()
        splits = re.split(" ", author)
 
        return author
    
def get_authors(df, year):
    df['author'] = df['title'].apply(get_authors_1)
    if year < 2017:
        df.loc[df['author'].isna(), 'author'] = df.loc[df['author'].isna(), 'title'].apply(get_authors_2)
    return df