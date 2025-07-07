import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from pygam import LinearGAM, s
import numpy as np

plt.style.use('bmh')

def plot_prediction_intervals(gam, XX, XX_dates, width=0.99, color='lightblue'):
    """Plot the prediction intervals for a GAM model."""
    
    # Get prediction intervals
    pred_intervals = gam.confidence_intervals(XX, width=width)
    lower, upper = pred_intervals[:, 0], pred_intervals[:, 1]

    # Plot the curves
    plt.plot(XX_dates, lower, color=color, ls='--')
    plt.plot(XX_dates, upper, color=color, ls='--')

    # Fill the area between the curves
    plt.fill_between(XX_dates, lower, upper, color=color, alpha=0.5)

def format_grid_matrix(XX, n_start, n_end):
    XX_data = XX.reshape(-1)
    diff = XX_data[1] - XX_data[0]
    XX_append_start = np.arange(XX_data[0] - n_start * diff, XX_data[0], diff)
    XX_append_end = np.arange(XX_data[-1] + diff, XX_data[-1] + (n_end + 1) * diff, diff)
    XX_data = np.concatenate([XX_append_start, XX_data, XX_append_end])
    XX = XX_data.reshape(-1, 1)
    return XX

def gam_prediction(data, n_splines=25, n_start=10, n_end=10):
    start_date = pd.Timestamp('2015-01-01')  # Replace 'YYYY-MM-DD' with your given date
    data['days_from_start'] = (data['date'] - start_date).dt.days
    X = data['days_from_start'].values.reshape(-1, 1)
    y = data['GAC1'].values

    gam = LinearGAM(s(0, n_splines)).gridsearch(X, y)
    XX = gam.generate_X_grid(term=0, n=500)
    XX = format_grid_matrix(XX, n_start, n_end)
    XX_dates = start_date + pd.to_timedelta(XX.ravel(), unit='D')

    #plt.figure(figsize=(10, 5))
    plt.plot(XX_dates, gam.predict(XX), 'r--')

    plot_prediction_intervals(gam, XX, XX_dates, width=0.99, color='lightblue')
    plot_prediction_intervals(gam, XX, XX_dates, width=0.95, color='darkblue')

    # Plot the data
    sc = plt.scatter(data['date'], data['GAC1'], color='black', s=10)

    plt.xlim([start_date, XX_dates[-1]])

    # Set x-axis ticks to display only years and rotate them 45 degrees
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    return sc