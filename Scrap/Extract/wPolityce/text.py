import regex as re

def same_page_solver(df, split_by_pages):
    articles_count = df['page'].value_counts().reset_index()
    pages_many_articles = articles_count[articles_count['count'] > 1]
    for _, row in pages_many_articles.iterrows():
        count = row['count']
        page = row['page']
        page_text = split_by_pages[page]
        splitted = re.split("(?:^|\n)([A-Za-z])[ ]*\n", page_text)[1:]
        texts = []
        for i in range(int(len(splitted)/2)):
            texts.append("".join([splitted[2*i], splitted[2*i + 1]]))
        if len(texts) != count: raise ValueError(f"Wrong Count! - {page} - {splitted}")
        df.loc[df.page == page, "text"] = texts
    return df

def monothonic_page_solver(page_start, page_end, split_by_pages):
    return "\n".join(split_by_pages[page_start:page_end])

def simple_same_page_solver(df):
    articles_count = df['page'].value_counts().reset_index().rename(columns = {"index": "page", "page": "count"})
    pages_many_articles = articles_count[articles_count['count'] > 1].page.values
    return df[~df.page.isin(pages_many_articles)]

def get_text_by_pages(df, content):
    split_by_pages = re.split(r"_Page \d+_", content)
    df['text'] = df.apply(lambda row: monothonic_page_solver(row['page'], row['next page'], split_by_pages), axis=1)
    df = simple_same_page_solver(df)
    return df
