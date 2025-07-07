import pandas as pd
import regex as re
from pdf_menager import pdf_to_string


def split_helper_two(text, file):
    text = text.replace("2o", "20")
    text = text.replace("3o", "30")
    text = text.replace("100-lecie", "Stolecie")
    text = text.replace("100- l e c i e ", "Stolecie")
    if file == "wPolityce/2018/user_47522_Sieci_26_2018_B_1.pdf":
      text = text.replace("18 z bernardem", "23 z bernardem")      
    elif file == "wPolityce/2018/user_47522_Sieci_51-52_2018_B.pdf":
      text = re.split("(?i)k r a j", text)[1]
    elif file == "wPolityce/2018/user_47522_Sieci_41_2018_B_1.pdf":
         text = text.replace("62 charleS", "60 Charles")
    elif file == "wPolityce/2019/user_47522_Sieci_08_2019_B_1.pdf":
        text = text.replace("82 góry", "98 góry")
    elif file == "wPolityce/2020/user_47522_Sieci_03_2020-skompresowany.pdf":
        text = text.replace("26 felietony", "16 felietony")
    elif file == "wPolityce/2022/user_47522_Sieci_14_2022.pdf":
        text = text.replace("35 słodKo-słony", "słodKo-słony")
    elif file == "wPolityce/2022/user_47522_Sieci_22_2022-compressed.pdf":
        text = text.replace("55 z ", "65 z ")
    elif file == "wPolityce/2020/user_47522_Sieci_33_2020.pdf":
        with open("wPolityce/special/user_47522_Sieci_33_2020.txt", "r") as f:
          text = f.read()
    elif file == "wPolityce/2020/user_47522_Sieci_47_2020_9FEmVev.pdf":
        with open("wPolityce/special/47_2020.txt", "r") as f:
          text = f.read()
    elif file == "wPolityce/2021/user_47522_Sieci_03_2021.pdf":
      text = text.replace("18 „perSonel niemedyczny”", "20 „Personel niemedyczny”")
    elif file == "wPolityce/2021/user_47522_Sieci_10_2021.pdf":
        with open("wPolityce/special/10_2021.txt", "r") as f:
            text = f.read()
    elif file == "wPolityce/2022/user_47522_Sieci_18_2022-compressed.pdf":
        with open("wPolityce/special/18_2022.txt", "r") as f:
            text = f.read()
    elif file in [
        "wPolityce/2016/user_47522_wSieci_17_2016.pdf",
        "wPolityce/2016/user_47522_wSieci_19_2016.pdf",
        "wPolityce/2016/user_47522_wSieci_18_2016.pdf",
        "wPolityce/2016/user_47522_wSieci_46_2016.pdf",
        ]:
      text = re.sub("(.|\n)*(?i)na PocząteK", '', text)
    return text
    
def split_helper_one(splits, file):
      if file in ['wPolityce/2017/user_47522_wSieci_25_2017_C.pdf',
            "wPolityce/2017/user_47522_wSieci_23_2017_B.pdf",
            "wPolityce/2018/user_47522_Sieci_19_2018_B.pdf",
            "wPolityce/2018/user_47522_Sieci_21_2018_B_2.pdf",
            "wPolityce/2018/user_47522_Sieci_22_2018_B_1.pdf",
            "wPolityce/2019/user_47522_Sieci_22_2019_B.pdf",
            "wPolityce/2019/user_47522_Sieci_21_2019_C.pdf",
            "wPolityce/2019/user_47522_Sieci_16-17_2019.pdf",
            "wPolityce/2019/user_47522_Sieci_19_2019.pdf",
            "wPolityce/2019/user_47522_Sieci_20_2019_B.pdf"]:
        splits.pop(3)
      return splits

def get_tbc_page(text, file):

  '''
    Function takes pdf converted to string and splits it by pages. Then it tries to find page with many matches of regex "\n[ ]*\d+[ ]+"
  '''
  splits = re.split("_Page \d+_\n", string = text)
  split_helper_one(splits, file)
  for i, split in enumerate(splits):
      if len(re.findall('\n[ ]*\d+[ ]+', split, re.IGNORECASE)) > 8 and i > 2:
          return split_helper_two(split, file)
  raise ValueError("No table of contents found")

def get_table_of_contents(table_text):
  '''
    Function takes page with table of contents and splits it by number of page mentioned. it captures page number and text which follows it and zips it.
  '''
  pages = []
  titles = []
  article_info = re.split("\n[ ]*(\d+)[ ]*", table_text)[1:]
  for i, content in enumerate(article_info):
      if i % 2 == 0:
          pages.append(content)
      else:
          titles.append(content)
  non_monothonical = 0
  for i in range(len(pages)-1):
      if pages[i] >= pages[i+1]: non_monothonical += 1

  return list(zip(pages, titles))

def get_index(df):
        monothonic_bool = df['page'].astype(int).diff().fillna(0) >= 0
        if (monothonic_bool == True).all():
              return None
        else:
            drop_index = df[monothonic_bool == False].index[0]  
            return drop_index 

def extract_monothonical(df):
    drop_index = get_index(df)
    while drop_index != None:
        if drop_index < 5:
             df = df[df.index >= drop_index]
        else:
             df = df[df.index < drop_index]
        drop_index = get_index(df)
    return df

def dodatek_extractor(content, df):  
    splits = re.search("(\d\d)-\n-(\d\d)", content)
    if splits != None:
      page = int(splits.group(1))
      next_page = int(splits.group(2))
      if not (df.page.between(page, next_page)).any():
        df_dodatek = pd.DataFrame(
          data = [('dodatek',page, next_page)],
          columns=['title', 'page', 'next page']
        )
        df = pd.concat([df, df_dodatek])    
    return df

def new_dodatek(content, df):
  if (df['title'].str.startswith("-")).any():
    df = df[~df['title'].str.startswith("-")]
    matches = re.findall("(\d\d)-(\d+)", content)   
    for match in matches:
        df_dodatek = pd.DataFrame(
          data = [('dodatek',int(match[0]), int(match[1]))],
          columns=['title', 'page', 'next page']
        )
        df = pd.concat([df, df_dodatek])    
  return df

def get_next_page(df):
  df['next page'] = df.page.shift(-1).fillna(-3).astype(int)
  return df

def table_of_contents_extractor(file):
    content = pdf_to_string(file)
    content = re.sub("(–|—)", "-", content)
    content = content.replace(" ", " ")

    tbl_page = get_tbc_page(content, file)
    tbc = get_table_of_contents(tbl_page)

    df_tbc = pd.DataFrame(tbc, columns=["page", 'title'])
    df_tbc['page'] = df_tbc['page'].astype(int)
    df_tbc = df_tbc[df_tbc['page'] > 3]

    df_tbc = extract_monothonical(df_tbc)
    df_tbc = get_next_page(df_tbc)
    df_tbc = dodatek_extractor(tbl_page, df_tbc)
    df_tbc = new_dodatek(tbl_page, df_tbc)
    df_tbc = df_tbc.sort_values("page")
    df_tbc = get_next_page(df_tbc)

    df_tbc['title'] = df_tbc['title'].apply(lambda x: re.sub(" \n\s+", " \n ", x))
    return df_tbc, content
