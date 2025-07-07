import numpy as np
import re
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)
from helpers.statistics import gac1
from helpers.time_windows import set_windows, get_window_sizes, select_between_dates
from helpers.statistics import get_mi_score
import pandas as pd

def select_colocates(mi_treshold, df_words, df_mi):
    df_selected = df_words.merge(df_mi, on='word')
    numbers = df_selected['word'].apply(lambda x: True if re.search(r"\d", x) else False)
    df_selected = df_selected[~numbers]
    return df_selected[df_selected['MI'] > mi_treshold]

def window_group_vector(df_selected, date, widow_width, window_size, window_index, treshold):
    min_size = window_size.min()
    df_window = select_between_dates(df_selected, date, widow_width)
    size = window_size[window_index]
    colocates = df_window.groupby('word_id').size()
    colocates = colocates[colocates > treshold * size / min_size]
    return colocates.index

def assign_id_words(df_words):
    words = df_words['word'].unique()
    index = range(len(words))
    dict_words = dict(zip(words, index))
    return dict_words

def get_word_id_column(df_words, dict_words):
    df_words.loc[:, 'word_id'] = df_words['word'].map(dict_words)
    return df_words

def vectorize(df_selected, dict_words, window_size, dates, widow_width, treshold):
    vect_list = []
    n = len(dict_words)
    for window_index, date in enumerate(dates):
        vect = np.zeros(n, dtype=bool)
        vect[window_group_vector(df_selected, date, widow_width, window_size, window_index, treshold)] = 1
        vect_list.append(vect)
    vect_data = np.array(vect_list)
    zero_indices_list = np.where(vect_data.sum(axis=0) == 0)[0]
    non_zero_indicies = np.where(vect_data.sum(axis=0) != 0)[0]
    index_mapping = {old_index: new_index for new_index, old_index in enumerate(non_zero_indicies)}
    filtered_dict_words = {
        word: index_mapping[old_index]
        for word, old_index in dict_words.items()
        if old_index in index_mapping
    }
    vect_list = np.delete(vect_data, zero_indices_list, axis=1)
    shifted_array = np.roll(vect_list, -1, 0)
    window_pairs = np.stack([vect_list[:-1], shifted_array[:-1]], axis=1)
    window_pairs = window_pairs.astype(bool) 
    results = []
    for index in range(window_pairs.shape[0]):
        results.append(gac1(window_pairs[index]))
    return results, window_pairs, filtered_dict_words

def to_ufa_df(results, dates, window_width):
    assert len(results) == len(dates) - 1
    df_ufa = pd.DataFrame({'date': dates[1:], 'GAC1': results})
    df_ufa['date'] += pd.DateOffset(days=window_width // 2)
    return df_ufa

def vectorize_colocation_df(df_words, df_corpus, data_path, time_step, window_width, treshold):
    dates = set_windows(time_step=time_step, window_width=window_width, data_path=data_path )
    df_mi = get_mi_score(df_words, df_corpus)
    window_sizes = get_window_sizes(data_path, df_corpus, dates, window_width)
    df_selected = select_colocates(6, df_words, df_mi)
    dict_words = assign_id_words(df_selected)
    df_selected = get_word_id_column(df_selected, dict_words)
    results, window_pairs, filtered_dict_words = vectorize(df_selected, dict_words, window_sizes, dates, window_width, treshold)
    df_ufa = to_ufa_df(results, dates, window_width)
    return df_ufa, filtered_dict_words, window_pairs