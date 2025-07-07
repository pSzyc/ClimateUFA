import pandas as pd

def get_current_data(configuration):
    drive_path = configuration.drive_path
    corpus = configuration.corpus
    df_eco = pd.read_csv(drive_path / corpus / "eco_result.csv", index_col=['id', 'source'], parse_dates=['date'])
    df_non_eco = pd.read_csv(drive_path / corpus / "non_eco_result.csv", index_col = ['id', 'source'], parse_dates=['date'])
    df_rest = pd.read_csv(drive_path / corpus / "results.csv", index_col = ['id', 'source'], parse_dates=['date'])
    df_eco['label'] = 1
    df_non_eco['label'] = 0
    return df_eco, df_non_eco, df_rest

def make_dataset(configuration, df_eco, df_non_eco):
    drive_path = configuration.drive_path
    corpus = configuration.corpus

    if corpus in ["rzepa", 'wyborcza']:
        n = min(len(df_eco), len(df_non_eco))
        df = pd.concat([df_eco.sample(n), df_non_eco.sample(n)])
    else:
        df_eco_rzepa = pd.read_csv(drive_path / "rzepa" / "eco_result.csv", index_col=['id', 'source'], parse_dates=['date']).sample(3000)
        df_non_eco_rzepa = pd.read_csv(drive_path / "rzepa" / "non_eco_result.csv", index_col = ['id', 'source'], parse_dates=['date']).sample(3000)
        df_eco_rzepa['label'] = 1
        df_non_eco_rzepa['label'] = 0
        df = pd.concat([df_eco, df_eco, df_non_eco, df_non_eco, df_eco_rzepa, df_non_eco_rzepa])
    return df