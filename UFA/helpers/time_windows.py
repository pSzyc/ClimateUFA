import datetime
import numpy as np
from pathlib import Path

def set_windows(window_width, time_step, data_path: Path):

    start_date = datetime.datetime(2015, 1, 1)
    end_date = start_date + datetime.timedelta(days=window_width)
    max_date = datetime.datetime(2023, 1, 1)

    dates = []
    while end_date < max_date:
        dates.append(start_date)
        end_date += datetime.timedelta(days=time_step)
        start_date += datetime.timedelta(days=time_step)
        
    print(f"{len(dates)} windows created")
    dates = np.array(dates)
    np.savetxt(data_path / "dates.txt", dates, fmt='%s')
    return dates

def get_window_sizes(data_path, df_corp, dates, window_width):

    df_corp['text_length'] = df_corp.text.apply(len)
    window_sizes = []
    for start_date in dates:
        df_window = select_between_dates(df_corp, start_date, window_width)
        window_sizes.append(df_window["real_count"].sum()) # more logical way to measure window size

    window_sizes = np.array(window_sizes)
    np.savetxt(data_path / "window_sizes.csv", window_sizes)
    return window_sizes


def get_window_sizes_old(data_path, df_corp, dates, window_width):

    df_corp['text_length'] = df_corp.text.apply(len)
    window_sizes = []
    for start_date in dates:
        df_window = select_between_dates(df_corp, start_date, window_width)
        window_sizes.append(df_window["text_length"].sum())

    window_sizes = np.array(window_sizes)
    return window_sizes

def select_between_dates(df, start_date, widow_width):
    widow_range = df.date.between(
        start_date,
        start_date + datetime.timedelta(days=widow_width)
    )
    return df[widow_range]