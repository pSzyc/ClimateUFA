import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pandas as pd
import numpy as np
np.random.seed(1)
import sys

plt.style.use('ggplot')

file = sys.argv[1]
text_max = int(sys.argv[2])

df = pd.read_csv(file)
c = df['class']
x = df['x']
y = df['y']
norm = Normalize()
cmap = plt.cm.brg
fig,ax = plt.subplots()
fig.set_size_inches(80,80)
ax.set_title("t-SNE results on input data of the classification layer of neural network", fontsize=20)
sc = plt.scatter(x, y, c=c, norm=norm, cmap=cmap, s=15, alpha=0.5)

legend = [sc.legend_elements()[0], ['Other Articles', 'Articles about Climate Change']]
plt.legend(*legend, fontsize=15)

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    idex = ind["ind"][0]
    article  = df.iloc[idex]
    text = article['text']
    text = str(article['id']) + "| " + "\n".join([text[i:i+100] for i in range(0, min(len(text),text_max), 100)])
    c = article['class']
    annot.set_text(text)
    annot.get_bbox_patch().set_facecolor(cmap(norm(c)))
    annot.get_bbox_patch().set_alpha(0.4)
    

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)
plt.xlabel("t-SNE dimension x")
plt.ylabel("t-SNE dimension y")
plt.show()