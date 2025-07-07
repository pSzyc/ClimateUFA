import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog
from matplotlib.widgets import Button, TextBox
import matplotlib.dates as mdates
from pygam import LinearGAM, s

plt.style.use('ggplot')

def plot_prediction_intervals(ax, gam, XX, XX_dates, width=0.99, color='lightblue'):
    """Plot the prediction intervals for a GAM model."""
    pred_intervals = gam.confidence_intervals(XX, width=width)
    lower, upper = pred_intervals[:, 0], pred_intervals[:, 1]
    ax.plot(XX_dates, lower, color=color, ls='--')
    ax.plot(XX_dates, upper, color=color, ls='--')
    ax.fill_between(XX_dates, lower, upper, color=color, alpha=0.5)

def format_grid_matrix(XX, n_start, n_end):
    XX_data = XX.reshape(-1)
    diff = XX_data[1] - XX_data[0]
    XX_append_start = np.arange(XX_data[0] - n_start * diff, XX_data[0], diff)
    XX_append_end = np.arange(XX_data[-1] + diff, XX_data[-1] + (n_end + 1) * diff, diff)
    XX_data = np.concatenate([XX_append_start, XX_data, XX_append_end])
    XX = XX_data.reshape(-1, 1)
    return XX

def gam_prediction(data, n_splines=25, n_start=10, n_end=10, ax=None):
    if ax is None:
        ax = plt.gca()
    start_date = pd.Timestamp('2015-01-01')
    data['days_from_start'] = (data['date'] - start_date).dt.days
    X = data['days_from_start'].values.reshape(-1, 1)
    y = data['GAC1'].values

    gam = LinearGAM(s(0, n_splines)).gridsearch(X, y)
    XX = gam.generate_X_grid(term=0, n=500)
    XX = format_grid_matrix(XX, n_start, n_end)
    XX_dates = start_date + pd.to_timedelta(XX.ravel(), unit='D')

    ax.plot(XX_dates, gam.predict(XX), 'r--')
    plot_prediction_intervals(ax, gam, XX, XX_dates, width=0.99, color='lightblue')
    plot_prediction_intervals(ax, gam, XX, XX_dates, width=0.95, color='darkblue')

    sc = ax.scatter(data['date'], data['GAC1'], color='black', s=10)
    ax.set_xlim([start_date, XX_dates[-1]])

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for label in ax.get_xticklabels():
        label.set_rotation(45)
    return sc

class GamPlot:
    def __init__(self):
        self.app = QApplication([])
        
        # Create figure and main axes
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(80, 80)
        
        self.df = None
        self.sc = None
        self.annot = None
        
        # Default parameters
        self.n_splines = 30
        self.n_start = 10
        self.n_end = 10
        self.current_filepath = None
        
        # File selection button
        file_button_ax = self.fig.add_axes([0.80, 0.01, 0.1, 0.05])
        self.file_button = Button(file_button_ax, "Select CSV")
        self.file_button.on_clicked(self.change_file)
        
        # Always-visible input fields using Matplotlib TextBox widgets
        # n_splines
        splines_box_ax = self.fig.add_axes([0.05, 0.01, 0.10, 0.04])
        self.splines_box = TextBox(splines_box_ax, "n_splines\n(# splines): ", initial=str(self.n_splines))
        self.splines_box.on_submit(self.update_splines)
                        
        # n_start: moved to the right for spacing
        start_box_ax = self.fig.add_axes([0.20, 0.01, 0.10, 0.04])
        self.start_box = TextBox(start_box_ax, "n_start\n(Extra at start): ", initial=str(self.n_start))
        self.start_box.on_submit(self.update_nstart)
                        
        # n_end: further to the right
        end_box_ax = self.fig.add_axes([0.35, 0.01, 0.10, 0.04])
        self.end_box = TextBox(end_box_ax, "n_end\n(Extra at end): ", initial=str(self.n_end))
        self.end_box.on_submit(self.update_nend)
        
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        
        file, _ = QFileDialog.getOpenFileName(None, "Select CSV file", "", "CSV files (*.csv)")
        if file:
            self.load_file(file)
    
    def update_splines(self, text):
        try:
            self.n_splines = int(text)
        except ValueError:
            pass
        if self.current_filepath:
            self.load_file(self.current_filepath)
    
    def update_nstart(self, text):
        try:
            self.n_start = int(text)
        except ValueError:
            pass
        if self.current_filepath:
            self.load_file(self.current_filepath)
    
    def update_nend(self, text):
        try:
            self.n_end = int(text)
        except ValueError:
            pass
        if self.current_filepath:
            self.load_file(self.current_filepath)
    
    def load_file(self, filepath):
        self.current_filepath = filepath
        self.df = pd.read_csv(filepath, parse_dates=['date'])
        self.ax.clear()
        self.sc = gam_prediction(self.df, n_splines=self.n_splines, n_start=self.n_start, n_end=self.n_end, ax=self.ax)
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                      textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="w"),
                                      arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.ax.set_xlabel('Date', fontsize=20)
        self.ax.set_ylabel('GAC1', fontsize=20)
        self.fig.canvas.draw_idle()
    
    def change_file(self, event):
        newfile, _ = QFileDialog.getOpenFileName(None, "Select CSV file", "", "CSV files (*.csv)")
        if newfile:
            self.load_file(newfile)
    
    def update_annot(self, ind):
        pos = self.sc.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        idx = ind["ind"][0]
        ufa_point = self.df.iloc[idx]
        text = (f"Windows:{idx},{idx+1}\n"
                f"Started to colocate: {ufa_point['started']}\n"
                f"No longer colocates: {ufa_point['stoped']}\n"
                f"keep: {ufa_point['keep']}")
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)
    
    def hover(self, event):
        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            elif self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()
    
    def show(self):
        plt.show()


if __name__ == "__main__":
    gam_plot = GamPlot()
    gam_plot.show()