from pathlib import Path
import pandas as pd

class config:
    source_dict = {
    "rzepa": "Rzeczypospolita",
    'gpc': "Gazeta Polska Codziennie",
    'newsweek': "Newsweek",
    'wprost' : 'Wprost',
    'dorzeczy': "DoRzeczy",
    'polityka': "Polityka",
    'wyborcza': "Gazeta Wyborcza",
    "wpolityce": "wPolityce"
    }

    METAFEATURES = [
        'Całkowita ilość słów',
        'Ilość słów bez powtórzeń',
        'Ilość stop-słów',
        'Średnia długość słowa',
        'Ilość symboli',
        'Ilość znaków interpunkcyjnych'
    ]

    def __init__(self, corpus, drive_path, files_path, STOPWORDS):
        self.corpus = corpus
        self.drive_path = drive_path
        self.files_path = files_path
        self.STOPWORDS = STOPWORDS

def get_setup(corpus):
    corp_dict = {1: 'rzepa', 2: 'gpc', 3: 'newsweek', 4: 'wprost', 5: 'dorzeczy', 6: 'polityka', 7: 'wyborcza', 8: 'wpolityce'}
    print(corp_dict)
    print(corpus)
    drive_path = Path("")
    files_path = Path("files")
    stopwords = pd.read_csv( files_path / 'polish_stopwords.txt', header=None)
    STOPWORDS = set([word.rstrip() for word in stopwords[0]])
    configuration = config(corpus, drive_path, files_path, STOPWORDS)
    return configuration