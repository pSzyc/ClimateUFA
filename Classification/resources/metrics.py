from sklearn.metrics import roc_curve
import seaborn as sns
import matplotlib.pyplot as plt

def plot_confusion_matrix(conf_matrix):
  plt.figure(figsize=(8,6), dpi=100)

  # Scale up the size of all text
  sns.set(font_scale = 1.1)


  # annot = True: show the numbers in each heatmap cell
  # fmt = 'd': show numbers as integers.
  ax = sns.heatmap(conf_matrix, annot=True, fmt='d')

  ax.set_xlabel("Predicted Label", fontsize=14, labelpad=20)
  ax.xaxis.set_ticklabels(['Negative', 'Positive'])

  ax.set_ylabel("Actual Label", fontsize=14, labelpad=20)
  ax.yaxis.set_ticklabels(['Negative', 'Positive'])

  ax.set_title("Confusion Matrix for the Articles Classification", fontsize=14, pad=20)

  plt.show()

def plot_roc_curve(true_y, y_prob):
    """
    plots the roc curve based of the probabilities
    """

    fpr, tpr, thresholds = roc_curve(true_y, y_prob)
    plt.plot(fpr, tpr)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    return fpr, tpr , thresholds