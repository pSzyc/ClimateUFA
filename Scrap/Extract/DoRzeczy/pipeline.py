import pandas as pd
import regex as re
import numpy as np
from pdf import txt_extractor, pdf_extractor
from pdf import general_preprocesing, error_dfs
from pdf import get_table_of_contents, validate_table_of_contents
from pdf import get_magazine_number, get_article_info
from os import walk

def rzepa_pipeline(folder_name, special_files, year):
    f = []

    for (dirpath, dirnames, filenames) in walk(folder_name):
        f.extend(filenames)
        
    pdf_files = list(filter(lambda x: True if re.search(".pdf$", x) else False, f))

    dfs = []
    problem_files = []

    for file in pdf_files:
        print(file, end=":")

        if file in special_files:
            print("special", end = ":")
            text, first_page_content, num_pages = txt_extractor(dirpath + file.replace(".pdf", ".txt"))
        else:
            text, first_page_content, num_pages = pdf_extractor(dirpath + file)


        # Table of contents
        table_text = get_table_of_contents(text)
        error_handled, table_text = validate_table_of_contents(table_text, year)
        if error_handled: problem_files.append((file, "Table of Contents"))
        
        # Magazine numbert
        try:
            magazine_nrs = get_magazine_number(first_page_content)
        except:
            magazine_nrs = (np.nan, np.nan)

        # Dataframe creation
        article_info_list, not_monothonical = get_article_info(table_text, year)
        df = pd.DataFrame(article_info_list, columns=["page", "raw_title"]) 
        df = general_preprocesing(df, num_pages, magazine_nrs, file, text)
        df.drop(columns = ["raw_title","next_article_page"], inplace=True)
        

        if not_monothonical > 1:
            print(not_monothonical, end="N:")
            problem_files.append((file, "Page number"))


        print(f"{len(df)}")
        if len(df) < 16: problem_files.append((file, "Few Found"))
        elif len(df) > 28: problem_files.append((file, "Many found"))
        dfs.append(df)

    df_final = error_dfs(dfs)
    return df_final, problem_files