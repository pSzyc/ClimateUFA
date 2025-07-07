import pandas as pd
import numpy as np
import sys
sys.path.insert(0, "./resources")
from resources.preprocessing import preprocess, vectorize_dataset
from resources.setup import get_setup
from resources.model import Model, chunk_it_predictions
from resources.get_data import get_current_data, make_dataset
from functools import reduce
import re

def data_pipeline(corpus): 
    # setup
    configuration = get_setup(corpus)
    print("Configuration finished")
    # get_dataset
    df_eco, df_non_eco, df_rest = get_current_data(configuration)
    df = make_dataset(configuration, df_eco, df_non_eco)
    print(f"Dataset of {len(df)} samples")
    print(df['label'].value_counts())
    # preprocessing
    df = preprocess(configuration, df)
    train_ngram_x, train_y, test_ngram_x, test_y, scaler, vectorizer, selector = vectorize_dataset(configuration, df)
    print("Preprocessing ended")
    # Model and prediction
    lr = Model(train_ngram_x, train_y, test_ngram_x, test_y)
    with pd.option_context('mode.chained_assignment', None):
        proba = np.concatenate([x for x in chunk_it_predictions(lr, df_rest, 500, vectorizer, selector, scaler, configuration)])
    df_rest['proba'] = proba
    df_rest = df_rest[~df_rest.index.isin(df_eco.index)]
    return df_rest, df_eco


def phrases_of_interest(df, regex):
    IsPresent = df.clean_text.apply(lambda x: True if re.search(regex, x) is not None else False)
    return IsPresent

def eco_selector(df, main=False):
    df['klimat_count'] = df['ngram_sum'] * df['klimat']
    condition_list_zk = [
        phrases_of_interest(df, r'zmian[^ ]*\s+klimat'),
    ]
    condition_list_go = [
        phrases_of_interest(df, r'globaln[^ ]*\s+ociepleni')
    ]
    condition_list_1 = [
        df['ngram_sum_squared_to_total'] > 0.75,
        df['proba'] > 0.5,
        df['weak_count'] < 0.5
    ]
    condition_list_2 = [
        df['weak_count']  < 0.3,
        df['ngram_sum_squared_to_total'] > 0.5,
        df['num_words'] > 2,
        df['proba'] > 0.5
    ]
    condition_list_3 = [
        df['klimat_count'] > 2,
        df['ngram_sum_squared_to_total'] > 0.33,
        df['proba'] > 0.5
    ]
    condition_list_4 = [
        df['klimat_count'] > 0,
        df['proba'] > 0.5,
        df['weak_count'] < 0.5,
        df['num_words'] > 2
    ]
    condition_list_5 = [
        df['proba'] > 0.7,
        df['weak_count'] < 0.8,
        df['num_words'] > 2
    ]
    condition_list_6 = [
        df['proba'] > 0.9,
        df['klimat_count'] > 0,
    ]
    conditions_all = [condition_list_zk, condition_list_go, condition_list_1, condition_list_2, condition_list_3, condition_list_4,condition_list_5, condition_list_6]
    if not main:  
        conditions_all.append([
            df['proba'] > 0.5,
            df['klimat_count'] > 0,
        ])
        conditions_all.append([
            df['proba'] > 0.5,
            df['weak_count'] < 0.75,
            df['ngram_sum_squared_to_total'] > 0.1
        ])
    selector = lambda c_list: reduce(lambda x, y: x & y, c_list)
    mask_maker = lambda conditions_list: reduce(lambda x, y: selector(x) | selector(y), conditions_list)
    mask = mask_maker(conditions_all)
    print(len(df), len(df[mask]))
    return df[mask]