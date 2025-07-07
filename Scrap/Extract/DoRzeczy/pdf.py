import fitz
import pandas as pd
import regex as re
import numpy as np



# ------------------------------- Files -------------------------------

def txt_extractor(filename):
    with open(filename, "r") as f:
        text = f.read().strip()
    pages = len(re.findall("_Page \d+_\n", text))
    first_page = re.split("_Page 1_\n", text)[0]
    return text, first_page, pages

def pdf_extractor(path):
    doc = fitz.open(path)                           
    out = []                   
    for i, page in enumerate(doc):                  
        text = page.get_text() + f"_Page {i+1}_"
        out.append(text)      

    return "\n".join(out).strip(), out[0], i+1


# --------------------------------------- Text extraction --------------------------------

def author_extractor(row):
    raw_title = row['raw_title'].strip()
    row['author'] = None
    if "ROZMOWA" == raw_title[:len("ROZMOWA")].upper():

        row['raw_title'] = "\n".join(re.split("\n",raw_title))
        pattern = r"(^[AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż\w\s]+):"
        author_match = re.search(pattern, row['content'])
        if author_match:
            row['author'] = author_match[1].upper().strip()
        return row
    
    elif "WIELKA ANKIETA" == raw_title[:len("WIELKA ANKIETA")].upper():
        row['raw_title'] = "\n".join(re.split("\n",raw_title)[1:])
        return row
    else:
        splits = re.split("\n",raw_title)

        if splits[0] != '':
            i = 0
        else:
            i = 1

        row['author'] = splits[i].upper().strip()      
        row['raw_title'] = "\n".join(splits[i+1:])

        return row
    
def content_extractor(start, text):
    try:
        text = re.split(f"_Page {start-1}_", text)[1]
    except:
        raise ValueError(str(start))
    
    text = re.split(f"©.*℗", text)[0]
    return text
    
def subtitle_extractor(row):
    title = row['raw_title']
    match = re.search("\n[A-Z]*[a-z](.|\n)+", title)
    if match != None:
        row["subtitle"] = match.group().replace("\n", " ")
        row["raw_title"] = row['raw_title'].replace(match.group(),"")
        return row
    else:
        row["subtitle"] = None
        return row

# -------------------------- Cleaning up --------------------------------



def title_cleaning(raw_title):
    return raw_title.replace("\n", " ")

def text_processor(text):
    if text == None: return None
    words = text.split()
    processed_words = []

    for word in words:
        if len(word) > 1:
            processed_word = word[0] + word[1:].lower()
        else:
            processed_word = word.lower()
        processed_words.append(processed_word)

    processed_text = ' '.join(processed_words)
    return processed_text

def content_cleaner(row):
    start = row['page']
    end = row['next_article_page']
    text = row['content']
    for i in range(start, end):
        text = re.sub(f"_Page {i}_", "", text)
    text = re.sub("© ℗(.|\n)*", "", text)
    text = re.sub("-\n", "", text)
    row['content'] = text
    row['error'] =  re.findall("_Page \d+_", text)
    return row

def big_letter_unifier(text):
    matches = re.findall("\n(\w)\n", text)
    for match in matches:
        text = re.sub(match + "\n", match, text)
    return text

def space_problem_solver(text):
    text = text.replace("\n", " ")
    text = text.replace("\s\s+", " ")
    return text.strip()  

def first_letter_capitalizer(text):
    if len(text) > 1:
        return text[0].upper() + text[1:]
    else:
        print("title error")
        return text


def general_preprocesing(df, num_pages, magazine_nrs, file, text):
    magazine_nr_1, magazine_nr_2 = magazine_nrs
    df['page'] = df['page'].astype(int)
    df = df.sort_values("page")
    df['next_article_page'] = df['page'].shift(-1).fillna(num_pages).astype(int)
    df['file'] = file
    df['magazine_nr_1'] = magazine_nr_1
    df['magazine_nr_2'] = magazine_nr_2
    df['content'] = df.apply(lambda row: content_extractor(row['page'], text), axis=1)
    df = df.apply(lambda row: content_cleaner(row), axis=1)

    df['content'] = df['content'].apply(big_letter_unifier)
    df['content'] = df['content'].apply(space_problem_solver)
    df['content'] = df['content'].apply(first_letter_capitalizer)
    
    df = df.apply(author_extractor, axis=1)

    df['title'] = df['raw_title'].apply(title_cleaning)
    df['title'] = df['title'].apply(text_processor)
    df['title'] = df['title'].apply(first_letter_capitalizer)
    df['title'] = df['title'].apply(space_problem_solver)

    return df


def error_dfs(dfs):
    df = pd.concat(dfs)
    df['error_count'] = df['error'].apply(lambda x:len(x))
    print("Before selection:" + str(len(df)))
    df = df[df['error_count']==0]
    print("After selection:"  + str(len(df)))
    return df

# --------------------------------------- Information Extraction --------------------------------

def validate_table_of_contents(table_text, year):

    table_text = re.sub("(?i)w w w \. d o r z e c z y \. p l", "" ,table_text)
    departments = ["kraj","kultura","Cywilizacja","nie przegap","opinie","historia","ekonomia","życie i nauka","temat tygodnia","świat","sport"]
    for dep in departments: table_text = re.sub(f"\n(?i){dep}\n", "\n", table_text)
    table_text = re.sub("(?i)spis treści", "" ,table_text)
    search = re.search("(\n\d+.*\n)(\d+)(.*)", table_text)
    if search:
        print("handling error:")
        print(search[0].strip(),end="\nerror_handled:")
        if year == 2015:
            table_text = re.sub(search[0], f'{search[1]}"{search[2]}"{search[3]}', table_text)
        return True, table_text
    else:
        return False, table_text
    
def get_table_of_contents(text):

    splits = re.split("_Page \d+_\n", string = text)
    
    for i, split in enumerate(splits):
        if re.search('\nspis treści\n', split, re.IGNORECASE) and i < 8: 
            return split

    for i, split in enumerate(splits):
        if len(re.findall('\n\d\d  ', split, re.IGNORECASE)) > 5 and i < 8: 
            print(f"Warning: experimental searching method {i}:", end="")
            return split
    for i, split in enumerate(splits):
        if len(re.findall('\n\d\d\p{Lu}', split, re.IGNORECASE)) > 5 and i < 8: 
            print(f"Warning: experimental searching method {i}:", end="")
            return split
            
    raise ValueError("No content found")

def get_magazine_number(first_page_content):
    number_1 =  re.search(r"(\n|^)(?i)nr ([0-9–]+)/(\d+)", first_page_content)[2]
    number_2 =  re.search(r"(\n|^)(?i)nr ([0-9–]+)/(\d+)", first_page_content)[3]
    return number_1, number_2


def get_article_info(table_text, year = 2015):
    pages = []
    titles = []
    


    if year != 2015: 

        article_info = re.split("\n(\d+)[ ]*(\p{Lu})", table_text)[1:]
        for i, content in enumerate(article_info):
            if i % 3 == 0:
                pages.append(content)
            elif i % 3 == 1:
                letter = content
            else:
                content = re.sub("(?i)felietony(\n|.)*", "", content)
                content = letter + content
                titles.append(content)

    if year == 2015 or len(pages) < 15:
        if year != 2015:
            print("Warning: Experimental Extraction", end=":")
        article_info = re.split("\n(\d+) ", table_text)[1:]
        for i, content in enumerate(article_info):
            if i % 2 == 0:
                pages.append(content)
            else:
                content = re.sub("(?i)felietony(\n|.)*", "", content)
                titles.append(content)

    for i, title in enumerate(titles):
        if re.search("(?i)NASZ PRZEWODNIK", title) or re.search("(?i)LGBT okladka", title):
            pages.pop(i)
            titles.pop(i)

    non_monothonical = 0
    for i in range(len(pages)-1):
        if pages[i] >= pages[i+1]: non_monothonical += 1
        
    return list(zip(pages, titles)), non_monothonical